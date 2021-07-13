import datetime
import requests
import lxml.html as lh
import pandas as pd

## VARS
# Code of meteo station
station_code = 'CE'
# year-month-day to start retrieving data from
meteodate = (2021, 5, 13)
# how many days of data do we retrieve?
meteodays = 62
# name of excel file to write to
excelfile = r'meteo_data.xlsx'
sheet_name = r'HostaletsPierola'
## CONSTANTS - DON'T MODIFY BEYOND THIS LINE
meteocat_url_template = "https://www.meteo.cat/observacions/xema/dades?codi={}&dia={}T00:00Z"
# this is the data structure of meteocat web for the table of data for a single day
# since we are going to combine data from several days, we also add the additional column "date" at the beggining
column_headers = ["fecha", "periodo", "tm", "tx", "tn", "hrm", "ppt", "vvm", "dvm", "vvx", "pm", "rs"]
final_data = pd.DataFrame(columns=column_headers)


## FUNCTIONS
def generate_date_range(startdate, days):
    start_date = datetime.date(startdate[0], startdate[1], startdate[2])
    date_list = []
    for day in range(days):
        a_date = (start_date + datetime.timedelta(days=day)).isoformat()
        # isoformat is 'yyyy-mm-dd' which is perfect for this case
        date_list.append(a_date.format())
    return date_list


for currentmeteodate in generate_date_range(meteodate, meteodays):
    scrappedcontents = []
    meteocat_url_formatted = meteocat_url_template.format(station_code, currentmeteodate)
    print(f"Obteniendo información meteorológica de la estación {station_code} para el dia {currentmeteodate}...")
    # print(meteocat_url_formatted)
    html = requests.get(meteocat_url_formatted)
    # scrappedcontents.append(r.content)
    htmlcontent = lh.fromstring(html.content)
    meteodata_elements = htmlcontent.xpath("//table[@class='tblperiode']//tr")
    # sanity check = value should be 11 always (the table we want contains 11 fields)
    # [print(len(T)) for T in meteodata_elements[:12]]
    # Now we parse the table and add to a dataframe, but skipping header, hence the "range 1,len"
    for row in range(1, len(meteodata_elements)):
        # print("Row = {}".format(row))
        row_contents = meteodata_elements[row]
        column = 0
        data = [currentmeteodate]
        for column_contents in row_contents.iterchildren():
            # print("Column = {}".format(column))
            data.append(str.strip(column_contents.text_content()))
            column += 1
        # print(data)
        # print(type(data))
        data_to_append = pd.Series(data, index=final_data.columns)
        # print(data_to_append)
        final_data = final_data.append(data_to_append, ignore_index=True)
# print(final_data)
final_data.to_excel(excelfile, sheet_name=sheet_name, index=False, startrow=1, startcol=1, header=True)
print('Los datos se han volcado al fichero.'.format(excelfile))



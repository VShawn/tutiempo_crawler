import requests
from bs4 import BeautifulSoup
import re

''' config_start '''
year = 2019
month = 1
place_id = '744860'

# proxies = {'http': 'http://172.20.65.197:808',
#            'https': 'http://172.20.65.197:808'}
proxies = None

''' config_end '''

month_dic = {'january': '01',
             'february': '02',
             'march': '03',
             'april': '04',
             'may': '05',
             'june': '06',
             'july': '07',
             'august': '08',
             'september': '09',
             'october': '10',
             'november': '11',
             'december': '12',
             }

def get_everydayweather(year, month, place_id='744860'):
    url = 'https://en.tutiempo.net/climate/{month:02}-{year:04}/ws-{place_id}.html'.format(year=year, month=month, place_id=place_id)

    '''     request html
    
    '''
    r = requests.get(url=url,
                     proxies=proxies,
                     verify=True,
                     headers={'Content-Type': 'application/x-www-form-urlencoded',
                              'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                              'Accept-Encoding': 'gzip, deflate, br',
                              'Accept-Language': 'zh-CN,zh;q=0.9',
                              'Cache-Control': 'max-age=0',
                              'Connection': 'keep-alive',
                              'DNT': '1',
                              'Host': 'en.tutiempo.net',
                              'Referer': 'https://en.tutiempo.net/climate/1947/ws-545110.html',
                              'Upgrade-Insecure-Requests': '1',
                              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
                              })
    if r.status_code == 404:
        print('climate data of: palce {} year {} month{} not exist'.format(
            place_id, year, month))
        return
    # with open('log.html', 'w') as fp:
    #     fp.write(str(r.content))
    html = str(r.content)

    ''' build symbol dict like:
                                        # symbol_dict = {
                                        #     'ntkk': '.',
                                        #     'ntjj': '-',
                                        #     'ntno': '1',
                                        #     'ntvw': '2',
                                        #     'ntef': '3',
                                        #     'ntee': '4',
                                        #     'ntgo': '5',
                                        #     'ntdr': '6',
                                        #     'ntpo': '7',
                                        #     'nthy': '8',
                                        #     'ntjg': '9',
                                        # }
    '''
    symbol_dict = {}
    str_symbol_style = re.compile(
        r'(?<=<style>).tablancpy([\s\S]*?)(?=</style>)').findall(html)
    if str_symbol_style:
        str_symbol_style = str(str_symbol_style)
        symbols = re.compile(
            r'(?<=\sspan.)([\s\S]*?)(?=color)').findall(str(str_symbol_style))
        for symbol in symbols:
            key = str(re.compile(r'([\s\S]*?)(?=::after)').findall(str(symbol))[0])
            val = str(re.compile(r'(?<=content:\S)([\s\S]*?)(?=\S;)').findall(str(symbol))[0])
            symbol_dict[key.lower()] = val

    bs = BeautifulSoup(html, 'html.parser')

    '''     get base info
    
    '''
    str_city = ''
    str_year = ''
    str_month_en = ''
    str_month_num = ''
    str_table_info = ''
    str_weather_station_id = ''
    str_latitude = ''
    str_longitude = ''
    str_altitude = ''

    str_table_title = bs("title")[0].text
    str_city = re.compile(r'(?<=Climate\s)[\s\S]+?(?=\s+?\(\w+?.*\s)').findall(str_table_title)[0]
    str_year = re.compile(r'Climate.*\s(\d+)\)\s-\s').findall(str_table_title)
    if len(str_year) >= 1 and str(str_year[0]).isdigit():
        str_year = str(str_year[0])
    else:
        str_year = str(year)

    str_month_en = re.compile(r'Climate.+?[(](\w+)\s\d+\)').findall(str_table_title)
    if len(str_month_en) >= 1 and str(str_month_en[0]).lower() in month_dic:
        str_month_en = str(str_month_en[0]).lower()
        str_month_num = month_dic[str_month_en]
    else:
        str_month_en = list(month_dic.keys())[list(
            month_dic.values()).index(str(year))]
        str_month_num = str(month)

    str_table_info = bs('p', attrs={'class': 'mt5'})
    if not str_table_info:
        str_table_info = ''
    else:
        str_table_info = str_table_info[0].text
        str_weather_station_id = re.compile(r'(?<=station:\s)\d*(?=\s)').findall(str_table_info)
        if str_weather_station_id:
            str_weather_station_id = str_weather_station_id[0]
        else:
            str_weather_station_id = ''

        str_latitude = re.compile(r'(?<=Latitude):\s(\d+\.?\d*)').findall(str_table_info)
        if str_latitude:
            str_latitude = str_latitude[0]
        else:
            str_latitude = ''
        str_longitude = re.compile(r'(?<=Longitude):\s(\d+\.?\d*)').findall(str_table_info)
        if str_longitude:
            str_longitude = str_longitude[0]
        else:
            str_longitude = ''
        str_altitude = re.compile(r'(?<=Altitude):\s(\d+\.?\d*)').findall(str_table_info)
        if str_altitude:
            str_altitude = str_altitude[0]
        else:
            str_altitude = ''




    '''     get climate table data
    
    '''
    trs = bs.select('.mt5.minoverflow.tablancpy table tr')  # climate table
    # get table header
    tr_header = trs[0]
    # get trs of every day climate
    trs_everyday = trs[1:-2]

    # get table header
    array_header = [th.text for th in tr_header.select('th')]
    array_subheader = ['', ] + [abbr['title']
                                for abbr in tr_header.select('abbr')]

    # get table body (everyday climate)
    array_bodys = []
    for tr in trs_everyday:
        # convert 'span - class' symbol to number
        if tr.find_all('span'):
            tds = tr.find_all('td')
            array_line = []
            array_line.append(tds[0].text)
            for td in tds[1:]:
                stritem = ''
                for span in td.find_all('span'):
                    stritem = stritem + symbol_dict[span['class'][0].lower()]
                array_line.append(stritem)
        # save directly
        else:
            array_line = [td.text.replace('\xa0', '') for td in tr]
        # make 1st clomn into datetime
        array_line[0] = '{year}-{month}-{day:02d}'.format(year=str_year, month=str_month_num, day=int(array_line[0]))
        array_bodys.append(array_line)

    array_title = ["City: ", str_city, "Year: ",str_year, "Month: ", str_month_num]
    array_info = ["Weather station: ", str_weather_station_id, "Latitude: ",str_latitude, "Longitude: ", str_longitude, "Altitude: ", str_altitude]
    write_data = '"\n"'.join(['","'.join(tr)for tr in [array_title, array_info, array_header, ] + [array_subheader, ] + array_bodys])
    write_data = '"' + write_data + '"'
    with open('S{id}_{year}-{month}_climate.csv'.format(id=str_weather_station_id, year=str_year, month=str_month_num), 'w') as fp:
        fp.write(write_data)




'''
simple demo
'''
if __name__ == '__main__':
    get_everydayweather(year, month, place_id)

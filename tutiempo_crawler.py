import requests
from bs4 import BeautifulSoup
import re

''' config_start '''
proxies = None
# proxies = {'http': 'http://172.20.65.197:808',
#            'https': 'http://172.20.65.197:808'}
''' config_end '''

def get_html(url):
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
    if r.status_code != 200:
        print('warning: {} response with {}'.format(url, r.status_code))
        return None
    return str(r.content)




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
    

class tutiempo_month_crawler(object):
    str_location = ''
    str_year = ''
    str_month_en = ''
    str_month_num = ''
    str_weather_station_id = ''
    str_latitude = ''
    str_longitude = ''
    str_altitude = ''
    array_climate_table_title = []
    array_climate_table_subtitle = []
    array_climate_table_data = []
    
    
    @staticmethod
    def get_obj(year, month, station_id):
        if month < 1 or month > 12:
            return None
        url = 'https://en.tutiempo.net/climate/{month:02}-{year:04}/ws-{station_id}.html'.format(year=year, month=month, station_id=station_id)
        html = get_html(url)

        ret = tutiempo_month_crawler()
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
        str_symbol_style = re.compile(r'(?<=<style>).tablancpy([\s\S]*?)(?=</style>)').findall(html)
        if str_symbol_style:
            str_symbol_style = str(str_symbol_style)
            symbols = re.compile(r'(?<=\sspan.)([\s\S]*?)(?=color)').findall(str(str_symbol_style))
            for symbol in symbols:
                key = str(re.compile(r'([\s\S]*?)(?=::after)').findall(str(symbol))[0])
                val = str(re.compile(r'(?<=content:\S)([\s\S]*?)(?=\S;)').findall(str(symbol))[0])
                symbol_dict[key.lower()] = val

        bs = BeautifulSoup(html, 'html.parser')

        '''     get base info
        
        '''
        ret.str_location = ''
        ret.str_year = ''
        ret.str_month_en = ''
        ret.str_month_num = ''
        ret.str_weather_station_id = ''
        ret.str_latitude = ''
        ret.str_longitude = ''
        ret.str_altitude = ''

        str_table_title = bs("title")[0].text
        ret.str_location = re.compile(r'(?<=Climate\s)[\s\S]+?(?=\s+?\(\w+?.*\s)').findall(str_table_title)[0]
        ret.str_year = re.compile(r'Climate.*\s(\d+)\)\s-\s').findall(str_table_title)
        if len(ret.str_year) >= 1 and str(ret.str_year[0]).isdigit():
            ret.str_year = str(ret.str_year[0])
        else:
            ret.str_year = str(year)

        ret.str_month_en = re.compile(r'Climate.+?[(](\w+)\s\d+\)').findall(str_table_title)
        if len(ret.str_month_en) >= 1 and str(ret.str_month_en[0]).lower() in month_dic:
            ret.str_month_en = str(ret.str_month_en[0]).lower()
            ret.str_month_num = month_dic[ret.str_month_en]
        else:
            ret.str_month_en = list(month_dic.keys())[list(month_dic.values()).index(str(year))]
            ret.str_month_num = str(month)

        str_table_info = bs('p', attrs={'class': 'mt5'})
        if not str_table_info:
            str_table_info = ''
        else:
            str_table_info = str_table_info[0].text
            ret.str_weather_station_id = re.compile(r'(?<=station:\s)\d*(?=\s)').findall(str_table_info)
            if ret.str_weather_station_id:
                ret.str_weather_station_id = ret.str_weather_station_id[0]
            else:
                ret.str_weather_station_id = ''

            ret.str_latitude = re.compile(r'(?<=Latitude):\s(\d+\.?\d*)').findall(str_table_info)
            if ret.str_latitude:
                ret.str_latitude = ret.str_latitude[0]
            else:
                ret.str_latitude = ''
            ret.str_longitude = re.compile(r'(?<=Longitude):\s(\d+\.?\d*)').findall(str_table_info)
            if ret.str_longitude:
                ret.str_longitude = ret.str_longitude[0]
            else:
                ret.str_longitude = ''
            ret.str_altitude = re.compile(r'(?<=Altitude):\s(\d+\.?\d*)').findall(str_table_info)
            if ret.str_altitude:
                ret.str_altitude = ret.str_altitude[0]
            else:
                ret.str_altitude = ''




        '''     get climate table data
        
        '''
        trs = bs.select('.mt5.minoverflow.tablancpy table tr')  # climate table
        # get table header
        tr_header = trs[0]
        # get trs of every day climate
        trs_everyday = trs[1:-2]

        # get table header
        ret.array_climate_table_title = [th.text for th in tr_header.select('th')]
        ret.array_climate_table_subtitle = ['', ] + [abbr['title']
                                    for abbr in tr_header.select('abbr')]

        # get table body (everyday climate)
        ret.array_climate_table_data = []
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
            array_line[0] = '{year}-{month}-{day:02d}'.format(year=ret.str_year, month=ret.str_month_num, day=int(array_line[0]))
            ret.array_climate_table_data.append(array_line)

        return ret






class tutiempo_climate_data(object):
    str_location = ''
    str_weather_station_id = ''
    str_latitude = ''
    str_longitude = ''
    str_altitude = ''
    array_climate_table_title = []
    array_climate_table_subtitle = []
    array_climate_table_data = []

    def append(self, month_data, int_year, int_month):
        # base info
        if self.str_location == "":
            self.str_location = month_data.str_location
            self.str_weather_station_id = month_data.str_weather_station_id
            self.str_latitude = month_data.str_latitude
            self.str_longitude = month_data.str_longitude
            self.str_altitude = month_data.str_altitude
            self.array_climate_table_title = month_data.array_climate_table_title[:]
            self.array_climate_table_subtitle = month_data.array_climate_table_subtitle[:]
            self.array_climate_table_data = month_data.array_climate_table_data[:]
        elif self.str_location == month_data.str_location:
            self.array_climate_table_data = self.array_climate_table_data + month_data.array_climate_table_data[:]
            pass
        else :
            print("warning: try to append {0} into {1}\n".format(month_data.str_location,self.str_location))
        return self









'''
simple demo
'''
if __name__ == '__main__':
    year = 2018
    station_id = '744860'
    # get one month
    month_data = tutiempo_month_crawler.get_obj(year, 1, station_id)
    if month_data:
        # build csv
        array_title = ["location: ", month_data.str_location, "Year: ", month_data.str_year, "Month: ", month_data.str_month_num]
        array_info = ["Weather station: ", month_data.str_weather_station_id, "Latitude: ", month_data.str_latitude, "Longitude: ", month_data.str_longitude, "Altitude: ", month_data.str_altitude]
        write_data = '"\n"'.join(['","'.join(tr)for tr in [array_title, array_info, month_data.array_climate_table_title, ] + [month_data.array_climate_table_subtitle, ] + month_data.array_climate_table_data])
        write_data = '"' + write_data + '"'
        # write csv
        with open('S{id}_{year}-{month}_climate.csv'.format(id=month_data.str_weather_station_id, year=month_data.str_year, month=month_data.str_month_num), 'w') as fp:
            fp.write(write_data)
        
        
    # get one year
    year_data = tutiempo_climate_data()
    for i in range(1,13):
        month_data = tutiempo_month_crawler.get_obj(year, i, station_id)
        if month_data:
            year_data.append(month_data,year,i)
    # build csv
    array_title = ["location: ", year_data.str_location]
    array_info = ["Weather station: ", year_data.str_weather_station_id, "Latitude: ", year_data.str_latitude, "Longitude: ", year_data.str_longitude, "Altitude: ", year_data.str_altitude]
    write_data = '"\n"'.join(['","'.join(tr)for tr in [array_title, array_info, year_data.array_climate_table_title, ] + [year_data.array_climate_table_subtitle, ] + year_data.array_climate_table_data])
    write_data = '"' + write_data + '"'
    # write csv
    with open('S{id}_{year}_climate.csv'.format(id=year_data.str_weather_station_id, year=year), 'w') as fp:
        fp.write(write_data)
    pass

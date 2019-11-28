from tutiempo_crawler import *



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
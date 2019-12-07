from tutiempo_crawler import *



''''
simple demo
'''
if __name__ == '__main__':
    
    region_name = 'macau'
    # get locations of 
    locations = tutiempo_location_crawler.get_locations_by_region(region_name)
    if locations and len(locations) > 0:
        # build csv
        array_title = ['location', 'weather station','ICAO','Latitude','Longitude','Altitude']
        array_data = []
        for loc in locations:
            array_data.append([loc.str_location, loc.str_weather_station_id, loc.str_icao, loc.str_latitude, loc.str_longitude, loc.str_altitude])
        write_data = '"\n"'.join(['","'.join(tr)for tr in [array_title,] + array_data])
        write_data = '"' + write_data + '"'
        # write csv
        with open('{region_name}_locations.csv'.format(region_name=region_name), 'w') as fp:
            fp.write(write_data)
        
        
    
    year = 2018
    station_id = '744860'
    # get one month
    month_data = tutiempo_month_crawler.get_obj(year, 1, station_id)
    if month_data:
        # build csv
        array_title = ['location: ', month_data.location_obj.str_location, 'Year: ', month_data.str_year, 'Month: ', month_data.str_month_num]
        array_info = ['Weather station: ', month_data.location_obj.str_weather_station_id, 'ICAO', month_data.location_obj.str_icao, 'Latitude: ', month_data.location_obj.str_latitude, 'Longitude: ', month_data.location_obj.str_longitude, 'Altitude: ', month_data.location_obj.str_altitude]
        write_data = '"\n"'.join(['","'.join(tr)for tr in [array_title, array_info, month_data.array_climate_table_title, ] + [month_data.array_climate_table_subtitle, ] + month_data.array_climate_table_data])
        write_data = '"' + write_data + '"'
        # write csv
        with open('S{id}_{year}-{month}_climate.csv'.format(id=month_data.location_obj.str_weather_station_id, year=month_data.str_year, month=month_data.str_month_num), 'w') as fp:
            fp.write(write_data)
        
        
    # get one year
    year_data = tutiempo_climate_data()
    for i in range(1,13):
        month_data = tutiempo_month_crawler.get_obj(year, i, station_id)
        if month_data:
            year_data.append(month_data,year,i)
    # build csv
    array_title = ['location: ', year_data.location_obj.str_location]
    array_info = ['Weather station: ', year_data.location_obj.str_weather_station_id, 'ICAO', year_data.location_obj.str_icao, 'Latitude: ', year_data.location_obj.str_latitude, 'Longitude: ', year_data.location_obj.str_longitude, 'Altitude: ', year_data.location_obj.str_altitude]
    write_data = '"\n"'.join(['","'.join(tr)for tr in [array_title, array_info, year_data.array_climate_table_title, ] + [year_data.array_climate_table_subtitle, ] + year_data.array_climate_table_data])
    write_data = '"' + write_data + '"'
    # write csv
    with open('S{id}_{year}_climate.csv'.format(id=year_data.location_obj.str_weather_station_id, year=year), 'w') as fp:
        fp.write(write_data)
    pass

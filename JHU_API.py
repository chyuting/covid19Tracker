############################################
# Based on public data by Johns Hopkins CSSE
# Author: Yuting Chen
# Uniquename: chyuting
############################################

import secrets
import sqlite3
import json
import requests
import datetime
key = secrets.jhuapi_key
today = datetime.date.today()

CACHE_FILE_PATH = 'jhu_api_cache.json'
def open_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    None

    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILE_PATH, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict):
    ''' Saves the current state of the cache to disk
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILE_PATH,"w")
    fw.write(dumped_json_cache)
    fw.close() 

def get_regions(iso='USA'):
    '''get valid regions(state, county) by iso'''
    cache = open_cache()
    if iso in cache.keys():
        print('Loading from cache...')
        return cache[iso]
    else:
        print(f'Fetching states/provinces for country {iso}!')
        url = "https://covid-19-statistics.p.rapidapi.com/provinces"
        querystring = {"iso":iso}

        headers = {
            'x-rapidapi-host': "covid-19-statistics.p.rapidapi.com",
            'x-rapidapi-key': key
            }

        response = requests.request("GET", url, headers=headers, params=querystring)
        cache[iso] = response.json()
        save_cache(cache)
    return cache[iso]

def get_reports(region, date=today):
    '''Get reports by region name and date'''
    cache = open_cache()
    date_str = f'{date.year}-{date.month}-{date.day}'
    if region in cache.keys() and date_str in cache[region].keys():
        print('Loading from cache...')
    else:
        if region in cache.keys():
            cache[state][date_str] = {}
        else:
            cache[state] = {}
        print(f'Fetching data for {region}!')
        url = "https://covid-19-statistics.p.rapidapi.com/reports"

        querystring = {"region_province": region,"iso":"USA","region_name":"US","date":date,"q":"US Michigan"}

        headers = {
            'x-rapidapi-host': "covid-19-statistics.p.rapidapi.com",
            'x-rapidapi-key': key
            }

        response = requests.request("GET", url, headers=headers, params=querystring)
        
        cache[state][date_str] = response.json()
        save_cache(cache)
    return cache[region][date_str]

def create_DB(region_info):
    '''Create a database with a table 'Regions' '''
    conn = sqlite3.connect('UScovid19.sqlite')
    cur = conn.cursor()

    drop_regions_sql = '''DROP TABLE IF EXISTS "Regions" '''
    drop_cities_sql = '''DROP TABLE IF EXISTS "Cities" '''

    create_regions_sql = '''
        CREATE TABLE IF NOT EXISTS "Regions"(
            "Id" INTEGER PRIMARY KEY AUTOINCREMENT,
            "RegionName" TEXT NOT NULL,
            "IsCounty" BOOL
        )
    '''
    
    create_cities_sql = '''
        CREATE TABLE IF NOT EXISTS "Cities"(
            "Id" INTEGER PRIMARY KEY AUTOINCREMENT,
            "CityName" TEXT NOT NULL,
            "RegionId" INTEGER,
            "Date" DATE,
            "Comfirmed" INTEGER,
            "NewComfirmed" INTEGER,
            "Deaths" INTEGER,
            "NewDeaths" INTEGER
        )
    '''

    cur.execute(drop_regions_sql)
    cur.execute(drop_cities_sql)
    cur.execute(create_regions_sql)
    cur.execute(create_cities_sql)
    
    insert_region_sql = '''
        INSERT INTO "Regions"
        VALUES (NULL, ?, ?)
    '''
    for region in region_info['data']:
        if ',' not in region['province']:
            cur.execute(insert_region_sql, [region['province'], 'FALSE'])
        else:
            cur.execute(insert_region_sql, [region['province'], 'TRUE'])
    conn.commit()
    conn.close()


def update_DB(report):
    '''Update the database by new inports'''
    conn = sqlite3.connect('UScovid19.sqlite')
    cur = conn.cursor()

    update_sql = '''
        INSERT INTO "Cities"
        VALUES(NULL, ?, ?, ?, ?, ?, ?)
    '''

    date = report.keys()[0]
    cities = report[date]['data']['cities']
    for city in cities:
        # TODO: pharse 4 data from cities
        cur.exercute(...)


def read_regions():
    '''Read region names as a list'''
    conn = sqlite3.connect('UScovid19.sqlite')
    cur = conn.cursor()

    read_regionNames_sql = '''
        SELECT RegionName FROM Regions
    '''

    cur.execute(read_regionNames_sql)
    regions = cur.fetchall()
    return regions


if __name__ == "__main__":
    region_info = us_provinces = get_regions(iso="USA")
    create_DB(region_info)
    
    region_list = read_regions()
    for region in region_list:
        report_today = get_reports(region=region, date=today) # default date is today
        update_DB(report_today)


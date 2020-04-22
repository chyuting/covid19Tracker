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
import os
import crawlCDC

key = secrets.jhuapi_key
today = datetime.date.today()
DB_NAME = 'UScovid19.sqlite'

def get_regions(iso='USA'):
    '''get valid regions(state, county) by iso
    *cache file update everyday
    
    Parameters
    ----------
    iso: str
        i.e, 'USA' for United States, 'CHN' for China 
    
    Returns
    -------
    dict
    '''
    cache = crawlCDC.open_cache()
    if 'api_regions' not in cache:
        print(f'Fetching states/provinces for country {iso}!')
        url = "https://covid-19-statistics.p.rapidapi.com/provinces"
        querystring = {"iso":iso}

        headers = {
            'x-rapidapi-host': "covid-19-statistics.p.rapidapi.com",
            'x-rapidapi-key': key
            }

        response = requests.request("GET", url, headers=headers, params=querystring)
        cache['api_regions'] = response.json()
        crawlCDC.save_cache(cache)
    else:
        print('Reading from cache.')
    return cache['api_regions']

def get_reports(region, date):
    '''Get reports by region name and date
    *cache file update everyday

    Parameters
    ----------
    region: str
        i.e. Michigan, New York
    date: datetime.date obj
        i.e. datetime.date.today()
    
    Returns
    -------
    dict
    '''
    cache = crawlCDC.open_cache()
    date_str = f'{date.year}-{date.month}-{date.day}'
    if f'api_{region}_{date_str}' not in cache:
        print(f'Fetching data for {region} in date {date_str}!')
        url = "https://covid-19-statistics.p.rapidapi.com/reports"
        querystring = {"region_province": region,"iso":"USA","region_name":"US","date":date,"q":f"US {region}"}
        headers = {
            'x-rapidapi-host': "covid-19-statistics.p.rapidapi.com",
            'x-rapidapi-key': key
            }
        response = requests.request("GET", url, headers=headers, params=querystring)
        cache[f'api_{region}_{date_str}'] = response.json()
        crawlCDC.save_cache(cache)
    else:
        print('Reading from cache.')
    return cache[f'api_{region}_{date_str}']

def create_DB(region_info):
    '''Create a database with a table 'Regions' '''
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    drop_regions_sql = '''DROP TABLE IF EXISTS "Regions" '''
    drop_counts_sql = '''DROP TABLE IF EXISTS "Counts" '''

    create_regions_sql = '''
        CREATE TABLE IF NOT EXISTS "Regions"(
            "Id" INTEGER PRIMARY KEY AUTOINCREMENT,
            "RegionName" TEXT NOT NULL,
            "IsCounty" BOOL
        )
    '''
    
    create_counts_sql = '''
        CREATE TABLE IF NOT EXISTS "Counts"(
            "Id" INTEGER PRIMARY KEY AUTOINCREMENT,
            "RegionId" INTEGER NOT NULL,
            "Date" DATE NOT NULL,
            "Confirmed" INTEGER NOT NULL,
            "NewConfirmed" INTEGER NOT NULL,
            "Deaths" INTEGER NOT NULL,
            "NewDeaths" INTEGER NOT NULL,
            "Recovered" INTEGER NOT NULL,
            "NewRecovered" INTEGER NOT NULL,
            "FatalityRate" REAL NOT NULL
        )
    '''

    cur.execute(drop_regions_sql)
    cur.execute(drop_counts_sql)
    cur.execute(create_regions_sql)
    cur.execute(create_counts_sql)
    
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
    if report['data'] == []: # no data reported
        print('No data!')
        return
    
    print('Updating database.')
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    update_sql = '''
        INSERT INTO "Counts"
        VALUES(NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''

    region_Id_sql = '''
        SELECT Id
        FROM Regions
        WHERE RegionName = ?    
    '''

    data = report['data'][0]
    region = data['region']['province']
    regionId = cur.execute(region_Id_sql, [region]).fetchone()[0]
    date = report['data'][0]['date']
    confirmed = data['confirmed']
    confirmed_diff = data['confirmed_diff']
    deaths = data['deaths']
    deaths_diff = data['deaths_diff']
    recovered = data['recovered']
    recovered_diff = data['recovered_diff']
    fatality_rate = data['fatality_rate']

    cur.execute(update_sql, [regionId, date, confirmed, confirmed_diff, deaths, deaths_diff, 
    recovered, recovered_diff, fatality_rate])
    conn.commit()
    conn.close()

def read_regions():
    '''Read region names as a list'''
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    read_regionNames_sql = '''
        SELECT RegionName FROM Regions
    '''

    cur.execute(read_regionNames_sql)
    regions = cur.fetchall() # tuples
    conn.commit()
    conn.close()
    return [region[0] for region in regions]

def read_recentDate():
    '''Find the most recent date'''
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    read_recentDate_sql = '''
        SELECT DISTINCT Date FROM Counts
        ORDER BY Date DESC
        LIMIT 1
    '''
    date = cur.execute(read_recentDate_sql).fetchone()[0]
    conn.commit()
    conn.close()
    year, month, day = date.split('-')
    return datetime.date(year=int(year), month=int(month), day=int(day))+datetime.timedelta(1)

if __name__ == "__main__":
    if not os.path.isfile(DB_NAME): # if database doesn't exist
        print('Creating a new database.')
        region_info = get_regions(iso="USA") # get regions
        create_DB(region_info) # create tables
        start_date = datetime.date(year=2020, month=2, day=29) # building the database from initial takes a long time!
    
    else: # if the database exist, update it since the last recorded datetime
        print('Update existed database.')
        start_date = read_recentDate()

    # Write new data into the database
    region_list = read_regions()
    days_count = (today- start_date).days  # not including today (data update after 4 PM.)
    print(f"Updating databse based on {len(region_list)} regions and {days_count} days' data.")
    for region in region_list:
        for single_date in [d for d in (start_date + datetime.timedelta(n) for n in range(days_count))]:
            report = get_reports(region=region, date=single_date)
            update_DB(report)
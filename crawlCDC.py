#####################################################
# Crawl data from CDC website and commandline prompt
# Author: Yuting Chen
# Uniquename: chyuting
#####################################################

import requests
import json
import datetime
from bs4 import BeautifulSoup
import os
import re
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.remote_connection import LOGGER
import logging
LOGGER.setLevel(logging.WARNING)


driver_path = 'C:/Users/pc/Downloads/chromedriver_win32/chromedriver.exe' # Please change the driver path to where chrome driver is
CDCurl = 'https://www.cdc.gov/coronavirus/2019-ncov/cases-in-us.html'
today = datetime.date.today() # cache everyday
CACHE_FILE_PATH = f'CDC_{today.month}_{today.day}.json'

def clear_cache(clear_today = False):
    '''Delete previous cache files
    *side-effect* delete system files if exists.

    Parameters
    ----------
    claer_today: bool
        True-> clear all cache files including today's
        False-> clear all cache files except for today's

    Returns
    -------
    None
    
    '''
    flag = 1 if clear_today == True else 0
    start_date = datetime.date(year=2020, month=2, day=29)
    days_count = (today- start_date).days
    for single_date in [d for d in (start_date + datetime.timedelta(n) for n in range(days_count+flag))]:        
        cache_file = f'CDC_{single_date.month}_{single_date.day}.json'
        if os.path.isfile(cache_file):
            print('Clear cache file: %s'%cache_file)
            os.remove(cache_file)

def open_cache(file_path=CACHE_FILE_PATH):
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
        cache_file = open(file_path, 'r')
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

def cases_by_state(info):
    ''' Get each state's accumulated cases

    Parameters
    ----------
    info: beautifulsoup

    Returns
    -------
    d: dict
        {state name: accumulated cases number}

    '''
    rows = info.find_all('div', class_='rt-tr-group')
    d = {}
    for row in rows:
        content = row.find_all('div', class_ = 'rt-td')
        if len(content) >= 2:
            state = content[0].find_all('span')[-1]
            accumulated = content[2].find('span')
            if accumulated.text != '0':
                d[state.text] = accumulated.text.replace(',', '') # '1,000' ->'1000'
    return d

def cases_by_date(info):
    ''' Get accumulated cases by date

    Parameters
    ----------
    info: beautifulsoup

    Returns
    -------
    numbers: dict
        {'year-month-day': (accumulated, new)}

    '''
    table = info.find('tbody', class_='data-columns')
    results = table.find_all('td')
    numbers = {}
    d = datetime.date(year=2020, month=1, day=22) # start date
    prev = 0
    for res in results:
        acc = res.text
        numbers[f'{d.year}-{d.month}-{d.day}']=(int(acc), int(acc)-int(prev))
        d += datetime.timedelta(1) # move to the next day
        prev = acc
    return numbers

def summary_today(info):
    ''' Get today's summary

    Parameters
    ----------
    info: beautifulsoup

    Returns
    -------
    tuple 
        (total cases, total deaths)

    '''
    total_cases = info.find('h2', id='covid-19-cases-total').text.replace(',', '').strip('\ufeff').strip()
    total_deaths = info.find('h2', id='covid-19-deaths-total').text.replace(',', '').strip('\ufeff').strip()
    return (total_cases, total_deaths)

def cases_by_age_race(info):
    ''' Get today's summary

    Parameters
    ----------
    info: beautifulsoup

    Returns
    -------
    tuple
        ({age group: total number}, {race group: total number})

    '''
    table = info.find('table', class_='table table-sm table-bordered fs08 nein-scroll')
    age_group = table.find_all('th', id=re.compile('^t1r02c0[2-8]')) # head
    table_body = table.find('tbody') # body
    numbers = table_body.find_all('tr') # rows
    age_num = numbers[0].find_all('td')[1:] # first row, start from second column
    age = {}
    for i in range(len(age_group)):
        age[age_group[i].text] = age_num[i].text.replace(',', '').strip()

    race = {}
    for i in numbers[4:10]:
        race_name = i.find('td').text # first column is race name
        race_num = i.find_all('td')[-1].text.split()[0].replace(',', '') # last column is total number
        race[race_name] = race_num
    return (age, race)

def update():
    ''' Updated cache by data from CDC website
    Parameters
    ----------
    None
    
    Returns
    -------
    cache: dict
    
    '''
    cache = open_cache()
    if cache == {}: # If cache is empty
        print('Fetching')
        options = webdriver.ChromeOptions() # magic happens in silient
        options.add_argument("headless") # comment to watch how web driver works (deverloper view)
        options.add_argument("--log-level=3") # supress log output
        options.add_argument("--window-size=1920,1080") # maximize the windowsize so that clickable
        driver = webdriver.Chrome(executable_path=driver_path, options=options) # new driver
        driver.get(url=CDCurl)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser') 
        cache['today'] = summary_today(soup) # get summary for today
        cache['age'], cache['race'] = cases_by_age_race(soup) # get age and race distribution

        wait = WebDriverWait(driver, 10)
        wait.until(EC.frame_to_be_available_and_switch_to_it("cdcMaps1")) # switch to iframe
        wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "collapsed.data-table-heading"))).click() # click by class name
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        cache['state'] = cases_by_state(soup)
        
        driver.switch_to.default_content() # switch to html tag
        wait.until(EC.frame_to_be_available_and_switch_to_it("cdcCharts2")) # switch to the next iframe
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        cache['date'] = cases_by_date(soup)
        
        driver.close()
    
    else:
        print(f'Read from cache file {CACHE_FILE_PATH}')
    save_cache(cache)
    return cache

def multi_capitalize(response):
    ''' Capitalize user input
    Parameters
    ----------
    response: str
    
    Returns
    -------
    str
    
    '''
    seperated = response.split()
    captalized = []
    for i in seperated:
        captalized.append(i.capitalize()) # michigan -> Michigan
    return ' '.join(captalized)

def process_age(response):
    '''Find total cases and percentile for an age group.
    Parameters
    ----------
    response: str
    
    Returns
    -------
    none
    '''
    response = int(response)
    if response >= 0 and response<=140:
        num = 0
        group = ''
        # percentile = 0
        if response < 18:
            num = age_dict['< 18']
            group = '< 18'
        elif response <= 44:
            num = age_dict['18-44']
            group = '18-44'
        elif response <= 64:
            num = age_dict['45-64']
            group = '45-64'
        elif response <=74:
            num = age_dict['65-74']
            group = '65-74'
        else:
            num = age_dict['75+']
            group = '75+'
        percentile = int(num)/(int(age_dict['Total']) - int(age_dict['Unknown']))
        print(f'The accumulated cases of age group {group} are {num} ({"{:.1%}".format(percentile)} of total cases).\n')
    else:
        print('Please type in an age between 0 and 140.')


if __name__ == "__main__":
    clear_cache(clear_today=False) # False -> update everday, True -> delete all cache files
    cache = update()
    state_dict = cache['state']
    date_list = cache['date']
    total_cases, total_death = cache['today']
    age_dict, race_dict = cache['age'], cache['race']

    print(f'''Welcome! Today's date is {today.strftime('%B')} {today.day}, {today.year}''')
    print(f'''Unitil today, total cases number is {total_cases}, total death number is {total_death}.''')
    
    while True:
        response = input("Please type in a state's name(i.e. Michigan) or race(i.e. Asia/Black/White/American Indian/Pacific/Multiple) or age(i.e. 20): ")
        if response.lower() == 'exit':
            break

        if response.isdigit():
            process_age(response)

        else:
            response = multi_capitalize(response)
            if len(response)>0 and response in state_dict.keys():
                print(f'The accumulated COVID19 cases of state {response} is {state_dict[response]}.\n')
            
            elif len(response)>0 and any(response in race for race in race_dict.keys()):
                for race in race_dict.keys():
                    if response in race:
                        print(f'The accumulated COVID19 cases of race {race} is {race_dict[race]}.\n')
            else:
                print("Please type in a valid input.")
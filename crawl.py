import requests
import json
import datetime
from bs4 import BeautifulSoup
import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.remote_connection import LOGGER
import logging
LOGGER.setLevel(logging.WARNING)


#data_source = 'https://coronavirus.1point3acres.com/en'
driver_path = 'C:/Users/pc/Downloads/chromedriver_win32/chromedriver.exe' # Please change the driver path to where chrome driver is
CDCurl = 'https://www.cdc.gov/coronavirus/2019-ncov/cases-in-us.html'
today = datetime.date.today() # cache everyday
CACHE_FILE_PATH = f'data_{today.month}_{today.day}.json'

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
        cache_file = f'data_{single_date.month}_{single_date.day}.json'
        if os.path.isfile(cache_file):
            print('Clear cache file: %s'%cache_file)
            os.remove(cache_file)

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

def get_state_info(info):
    '''Return dict {state_name: (accumulated, new, death)}
    '''
    rows = info.find_all('div', class_='rt-tr-group')
    d = {}
    for row in rows:
        content = row.find_all('div', class_ = 'rt-td')
        if len(content) >= 2:
            state = content[0].find_all('span')[-1]
            accumulated = content[1].find('span')
            if accumulated.text != '0':
                #print(state.text, accumulated.text)
                d[state.text] = accumulated.text.replace(',', '') # '1,000' ->'1000'
    return d

def update():
    '''Get the updated information'''
    cache = open_cache()
    if cache == {}: # If cache is empty
        print('Fetching')
        options = webdriver.ChromeOptions() # magic happens in silient
        options.add_argument("headless") # don't display the window
        options.add_argument("--window-size=1920,1080") # maximize the windowsize so that clickable
        driver = webdriver.Chrome(executable_path=driver_path, chrome_options=options, service_log_path='NUL') # new driver
        driver.get(url=CDCurl)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.frame_to_be_available_and_switch_to_it("cdcMaps1")) # switch to iframe
        wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "collapsed.data-table-heading"))).click() # click by class name
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        cache = get_state_info(soup)
    else:
        print(f'Read from cache file {CACHE_FILE_PATH}')
    save_cache(cache)
    return cache

def multi_capitalize(response):
    '''Processing user input'''
    seperated = response.split()
    captalized = []
    for i in seperated:
        captalized.append(i.capitalize()) # michigan -> Michigan
    return ' '.join(captalized)



if __name__ == "__main__":
    clear_cache(clear_today=False) # update everday
    cache = update()
    print(f'''Welcome! Today's date is {today.strftime('%B')} {today.day}, {today.year}''')
    while True:
        response = input("Please type in a state's name, i.e. Michigan: ")
        if response.lower() == 'exit':
            break

        response = multi_capitalize(response)
        if response in cache:
            print(f'The accumulated COVID19 cases of {response} is {cache[response]}.\n')
        
        else:
            print("Please type in a valid state's name")
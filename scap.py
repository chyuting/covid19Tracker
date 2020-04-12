import requests
import json
import datetime
from bs4 import BeautifulSoup
import os

data_source1 = 'https://coronavirus.1point3acres.com/en'
data_source = 'https://www.cdc.gov/coronavirus/2019-ncov/cases-updates/cases-in-us.html'

today = datetime.date.today() # cache everyday
CACHE_FILE_PATH = f'data_{today.month}_{today.day}.json'

def clear_cache():
    '''Delete previous cache files except for today's
    *side-effect* delete system files if exists.

    Parameters
    ----------
    None

    Returns
    -------
    None
    
    '''
    start_date = datetime.date(year=2020, month=2, day=29)
    days_count = (today- start_date).days
    for single_date in [d for d in (start_date + datetime.timedelta(n) for n in range(days_count))]:        
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

def update_info():
    '''Return dict {state_name: (accumulated, new, death)}
    '''
    cache = open_cache()
    if cache == {}: # If cache is an empty dict
        print('Fetching')
        response = requests.get(data_source)
        print(response)
        #print(response.text)
        #soup = BeautifulSoup(response.text, 'html.parser')
        # content = soup.find('div', class_= 'container d-flex flex-wrap body-wrapper bg-white')
        # main = content.find('main', class_= 'col-lg-9 order-lg-2')
        # row = main.find_all('div', class_='row')
        # col_content = row[1].find('div', class_='col content') # second
        # syn = col_content.find_all('div', class_='syndicate')
        # row = syn[0].find_all('div') # second

        # third_row = row[2]
        # card1 = third_row.find('div', class_='col-md-12')
        # card2 = card1.find('div', class_='card md-3')
        # card_body = card2.find('div', class_='card-body')
        # docu = card_body.find('#document')
        # root = docu.find('div', id='root')
        # section = root.find('section', class_='data-table')
        # table = section.find('div', class_='ReactTable')
        # body = table.find('div', class_= 'rt-tbody')

        #rows = soup.find_all('div', class_='rt-tr-group')
        #print(rows)
        #for row in rows:
        #    content = row.find_all('div', class_ = 'rt-td')
        #    state = content[0].find('span')
        #    accumulated = content[1].find('span')
        #    print(state, accumulated)
        #save_cache(cache)
    return cache


if __name__ == "__main__":
    clear_cache()
    update_info()
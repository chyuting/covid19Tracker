########################################
# Build database based on retrieved data
# Author: Yuting Chen
# Uniquename: chyuting
########################################

import sqlite3
import datetime
from crawlCDC import open_cache, CACHE_FILE_PATH
import os

def create_db(info):
    '''create a database with cache files'''
    pass

if __name__ == "__main__":
    cache = open_cache()
    if cache != {}: # create database
        create_db(cache)
    else:
        print('Cache file missing! Please crawl covid19 data by running crawlCDC.py.')


#!/usr/bin/env python3

import os
from datetime import date

import json
import requests
import pandas as pd
from tqdm.auto import tqdm

__repository__ = 'showstats'
__license__ = "MIT"
__version__ = "0.0.1"
__location__ = "https://github.com/colin-gall/showstats/"
__author__ = "colingall"
__email__ = "colingall@pm.me"

def download_json(page):
    '''Handshakes with API address provided on MLB The Show 24 community market API docs and returns content as JSON object.'''
    url = f"https://mlb24.theshow.com/apis/items.json?type=mlb_card&page={page}"
    page = requests.get(url)
    if page.status_code == 200:
        return page.json()

def download_items():
    '''Total page count is determined, JSON data is gathered for each page from API and stored in cumulative list at the end of each iteration, and finally data is parsed, organized, and returned as a Pandas dataframe.'''
    json_data = download_json(1)
    num_pages = int(json_data['total_pages'])
    all_items = []
    #for i in range(num_pages):
    print(f'~ Downloading MLB The Show data ({num_pages} pages of items found)...')
    for i in tqdm(range(num_pages)):
        json_data = download_json(i)
        page_listings = json_data['items']
        for p in page_listings:
            all_items.append(p)
    df = pd.DataFrame.from_records(all_items, index=['uuid'])
    return df

def download_csv(df, filename=None):
    '''Attempts to convert dataframe containing JSON data to Excel workbook file saved to current working directory, and creates a 'pkl' (i.e. pickle) file if it encounters any issues during the process to prevent data loss.''' 
    try:
        if filename is None:
            filename = f"mlbtheshow_data_{date.today().year}{date.today().month}{date.today().day}.xlsx"
        print(f'~ Creating Excel file with the data collected for MLB The Show data (filename: {filename})')
        df.to_excel(filename)
    except:
        print('~ Unable to create Excel file - creating pickle file to prevent loss of data')
        filename = f"{os.path.expanduser('~')}/mlbtheshow_dataloss_{date.today().year}{date.today().month}{date.today().day}.pkl"
        df.to_pickle(filename)

def execute():
    '''Runtime core functionality for script execution or if called as main module.'''
    df = download_items()
    download_csv(df)
    print('_____________\n|   Done!   |\n*-----------*')

if __name__ == '__main__':
    execute()


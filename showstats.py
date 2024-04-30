#!/usr/bin/env python3

import os
import argparse
from datetime import date

import json
import requests
import pandas as pd
from tqdm.auto import tqdm

__repository__ = 'showstats'
__license__ = "MIT"
__version__ = "0.0.1"
__location__ = "https://github.com/colin-gall/showstats/"
__author__ = "colin-gall"
__email__ = "colingall@pm.me"

def convert_json(param="items", page=1):
    '''Handshakes with API address provided on MLB The Show 24 community market API docs and returns content as JSON object.'''
    # check if page number is invalid
    if page == 0:
        page = 1
    url = f"https://mlb24.theshow.com/apis/{param}.json?type=mlb_card&page={page}"
    page = requests.get(url)
    if page.status_code == 200:
        return page.json()
    else:
        retries = 0
        while retries < 2:
            try:
                print("Attempting to fetch data (retries left: %i)" % (2 - retries))
                page = requests.get(url, timeout=5)
                # raises HTTP error for bad responses
                requests.raise_for_status()
                return page.json
            except:
                retries += 1

def download_data(param="items"):
    '''Total page count is determined, JSON data is gathered for each page from API and stored in cumulative list at the end of each iteration, and finally data is parsed, organized, and returned as a Pandas dataframe.'''
    # checking param for list of valid API calls
    if param not in ['items', 'listings', 'captains', 'roster_updates']:
        if param in ['item', 'listing', 'captain', 'roster_update', 'roster', 'rosters']:
            if param == 'roster_update' or param == 'roster' or param == 'rosters':
                param = 'roster_updates'
            else:
                param = f"{param}s"
    json_data = convert_json(param, 1)
    num_pages = int(json_data['total_pages'])
    all_items = []
    #for i in range(num_pages):
    print(f'~ Downloading MLB The Show data ({num_pages} pages found, type: {param})...')
    for i in tqdm(range(num_pages)):
        json_data = convert_json(param, i)
        page_listings = json_data[param]
        for p in page_listings:
            all_items.append(p)
    df = pd.DataFrame.from_records(all_items, index=['uuid'])
    return df

def create_file(df, filename=None):
    '''Attempts to convert dataframe containing JSON data to Excel workbook file saved to current working directory, and creates a 'pkl' (i.e. pickle) file if it encounters any issues during the process to prevent data loss.''' 
    if filename is None:
        filename = f"mlbtheshow_data_{date.today().year}{date.today().month}{date.today().day}.xlsx"
    print(f'~ Attempting to create Excel file with the data collected for MLB The Show data (filename: {filename})')
    try:
        df.to_excel(filename)
    except:
        try:
            filename = f"{os.path.expanduser('~')}/{filename}"
            df.to_excel(filename)
        except:
            try:
                if filename is None:
                    filename = f"{os.path.expanduser("~")}/mlbtheshow_data_{date.today().year}{date.today().month}{date.today().day}.csv"
                df.to_csv(filename)
            except:
                picklefile = f"{os.path.expanduser('~')}/mlbtheshow_dataloss_{date.today().year}{date.today().month}{date.today().day}.pkl"
                df.to_pickle(picklefile)
    if os.path.exists(picklefile):
        print(f"~ Error occured when attempting to store data in both Excel & CSV file types...\
            \nPandas data file (i.e. 'pickle' file or .pkl file) was created to prevent loss of data.\
            \nLocation: {picklefile}")
    else:
        if filename[len(filename)-3:] == 'csv':
            filetype = 'CSV'
        else:
            filetype = 'Excel'
        print(f"Successfully created {filetype} file containing MLB The Show data.\
            \nLocation: {filename}")

def parse_arguments():
    '''Arguments passed during script execution are parsed and passed as parameters for customization in types of data to download from API'''
    parser = argparse.ArgumentParser()
    parser.add_argument('datatype', type=str, default='items', required=False, help='Type of data to download from MLB The Show API')
    parser.add_argument('-f', '--filename', type=str, dest='filename', default=None, required=False, help='Name of file for storing data from Pandas dataframe (*INCLUDE EXTENSION*)')
    args = parser.parse_args()
    return args.datatype, args.filename


def execute():
    '''Runtime core functionality for script execution or if called as main module.'''
    datatype, filename = parse_arguments()
    df = download_data(datatype)
    if filename is not None:
        create_file(df)
    else:
        create_file(df, filename)
    print('_____________\n|   Done!   |\n*-----------*')

if __name__ == '__main__':
    execute()

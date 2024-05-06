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
__version__ = "0.0.2"
__location__ = "https://github.com/colin-gall/showstats/"
__author__ = "colin-gall"
__email__ = "colingall@pm.me"


PATHDIRS = [os.getcwd(), os.path.expanduser('~')]
PARAMS = ['items', 'listings', 'captains', 'roster_updates', 'game_history']
PLATFORMS = ['psn', 'xbl', 'mlbts', 'nsw']

API_URL = 'https://mlb24.theshow.com'
API_LINKS = {
    'items' : '/apis/items.json?type=mlb_card&',
    'listings' : ' /apis/listings.json?type=mlb_card&',
    'captains' : '/apis/captains.json?',
    'roster_updates' : ' /apis/roster_updates.json',
    'game_history' : '/apis/game_history.json?username={username}&platform={platform}&mode=arena&',
}
API_PAGE = 'page={page}'


def convert_json(param, platform, username, page=1):
    '''Handshakes with API address provided on MLB The Show 24 community market API docs and returns content as JSON object.'''
    # check if page number is invalid
    if page == 0:
        page = 1
    # grabbing specific URL from global dictionary based on datatype passed as argument
    if param == 'game_history':
        url = str(API_URL + API_LINKS[param].format(username=username, platform=platform))
    else:
        url = str(API_LINKS[param])
    # combining unique URL for API request with generic JSON page extension
    url = str(url + API_PAGE.format(page=page)) 
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


def download_data(param, platform, username=None):
    '''Total page count is determined, JSON data is gathered for each page from API and stored in cumulative list at the end of each iteration, and finally data is parsed, organized, and returned as a Pandas dataframe.'''
    # checking param for list of valid API calls
    if param not in PARAMS:
        if param in PARAMS or param in ['roster', 'rosters', 'games', 'history']:
            if param == 'roster_update' or param == 'roster' or param == 'rosters':
                param = 'roster_updates'
            elif param == 'game_history' or param =='games' or param == 'history':
                param == 'game_history'
            else:
                param = f"{param}s"
        else:
            raise Exception(f"{*param}* is not a valid datatype for API requests. For a list of acceptable options, please pass one of the following as an argument:\n{PARAMS}")
    # checks platform type if parameter for data download is game history or if username is provided as an argument
    if param == 'game_history' or username is not None:
        if platform.lower() is not PLATFORMS:
            if platform.upper() == 'PS5':
                platform = 'psn'
            elif platform.lower() == 'xbox':
                platform = 'xbl'
            else:
                raise Exception(f"*{platform}* is not a valid platform for API requests. For a list of acceptable options, please pass one of the following as an argument:\n{PLATFORMS}")
    json_data = convert_json(param, platform, username, 1)
    num_pages = int(json_data['total_pages'])
    all_items = []
    print(f'~ Downloading MLB The Show data ({num_pages} pages found, type: {param})...')
    for i in tqdm(range(num_pages)):
        json_data = convert_json(param, platform, username, i)
        page_listings = json_data[param]
        for p in page_listings:
            all_items.append(p)
    df = pd.DataFrame.from_records(all_items, index=['uuid'])
    return df


def create_file(df, filename=None):
    '''Attempts to convert dataframe containing JSON data to Excel workbook file saved to current working directory, and creates a 'pkl' (i.e. pickle) file if it encounters any issues during the process to prevent data loss.'''
    date_str = f"{date.today().year}{date.today().month}{date.today().day}"
    if filename is None:
        filename = f"mlbtheshow_data_{date_str}.xlsx"
    elif filename[-4:] != 'xlsx' and filename[-3:] != 'csv':
        filename = f"{filename}.xlsx"
    print(f'~ Attempting to create Excel file with the data collected for MLB The Show data (filename: {filename})')
    try:
        df.to_excel(os.path.join(os.getcwd(),filename))
    except:
        filename = f"{filename[:-3]}csv"
        df.to_csv(os.path.join(os.getcwd(),filename))
    finally:
        excel_file = f"mlbtheshow_data_{date_str}.xlsx"
        csv_file = f"mlbtheshow_data_{date_str}.csv"
        create_pickle = False
        if os.path.exists(excel_file) is False and os.path.exists(csv_file) is False:
            file_list = []
            file_exts = []
            # grabbing list of file names and file extensions to check for successful file creation
            for p in PATHDIRS:
                file_names = [f for f in os.listdir(p) if os.path.isfile(os.path.join(p,f))]
                for x in file_names:
                    file_list.append(x)
                    file_exts.append(os.path.splitext(x)[-1].lower())
            if '.xlsx' in file_exts or 'xlsx' in file_exts or '.csv' in file_exts or 'csv' in file_exts:
                if excel_file in file_list or csv_file in file_list:
                    create_pickle = False
                else:
                    create_pickle = True
            else:
                create_pickle = True
        else:
            create_pickle = True
        # checks boolean and creates pickle file if true
        if create_pickle is True:
            print("~ Error occured while attempting to export data to '.xlsx' file and '.csv' file...")
            try:
                print("~ Attempting to create '.pkl' file to prevent loss of API data...")
                pickle_file = f"mlbtheshow_dataloss_{date_str}.pkl"
                df.to_pickle(os.path.join(os.getcwd(), pickle_file))
                print(f"~ Successfully created '.pkl' file [{os.path.join(os.getcwd(), pickle_file)}]")
            except:
                print("Error occured while attempting to create '.pkl' file...")
                print("Failed to prevent data loss after encountering multiple issues.")
                sys.exit(1)
        else:
            print(f"Successfully exported data for MLB The Show [{os.path.join(os.getcwd(), filename)}]")
            print('_____________\n|   Done!   |\n*-----------*')


def parse_arguments():
    '''Arguments passed during script execution are parsed and passed as parameters for customization in types of data to download from API'''
    parser = argparse.ArgumentParser()
    parser.add_argument('-d','--datatype', type=str, dest='datatype', default='items', help='Type of data to download from MLB The Show API')
    parser.add_argument('-p', '--platform', type=str, dest='platform', default='psn', required=False, help='Platform of choice of user for downloading game history from API (default: psn)')
    parser.add_argument('-u', '--username', type=str, dest='username', default=None, required=False, help='Username of player for downloading game history from API. (*MUST INCLUDE PLATFORM IF PROVIDING USERNAME*)')
    parser.add_argument('-f', '--filename', type=str, dest='filename', default=None, required=False, help='Name of file for storing data from Pandas dataframe (*INCLUDE EXTENSION*)')
    args = parser.parse_args()
    return args


def execute():
    '''Runtime core functionality for script execution or if called as main module.'''
    api_url = "https://mlb24.theshow.com/apis/"
    print(f"~ Getting ready to download data from API for MLB The Show [{api_url}]...")
    args= parse_arguments()
    if args.username is not None:
        df = download_data(args.datatype, args.platform, args.username)
    else:
        df = download_data(args.datatype, args.platform)
    if args.filename is not None:
        create_file(df)
    else:
        create_file(df, args.filename)
    print('_____________\n|   Done!   |\n*-----------*')


if __name__ == '__main__':
    execute()


# OLD CODE FOR CREATING EXCEL / CSV / PICKLE FILES
'''
try:
    filename = f"{os.path.expanduser('~')}/{filename}"
    df.to_excel(filename)
except:
    try:
        if filename is None:
            filename = f"{os.path.expanduser('~')}/mlbtheshow_data_{date.today().year}{date.today().month}{date.today().day}.csv"
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
'''

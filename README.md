# showstats
Python script for downloading attributes and statistics for all currently available Diamond Dynasty player card items in MLB The Show '24 . 

(relative%20path/to/img.jpg?raw=true "Title")




### Install

Install the required dependencies if missing necessary packages:
```
~$ pip install -r requirements.txt
```

### Usage

Execute script using any terminal or interactive shell, & watch as data is gathered from online API.
```
~$ python3 showstats.py
```
Data will be saved to an Excel file in the user's home directory, but in the event of an error during the conversion, a pandas 'pkl' file will be created to prevent data loss..
> ./mlbtheshow_data_YYMMDD.xlsx

> /usr/home/dir/mlbtheshow_dataloss_YYMMDD.pkl 

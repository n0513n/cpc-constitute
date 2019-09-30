#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Data frame loading and processing functions.

Tested with Pandas version 0.24.2.
'''

import numpy as np
import pandas as pd

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from os import getpid
from os.path import abspath, isfile, splitext
from sys import getsizeof
from time import time

from worldmap import WORLDMAP

def df_write(df, output_file, index_label='', overwrite=False):
    '''
    Write a data frame to output path.
    '''
    if isfile(output_file) and not overwrite:
        # append process ID and timestamp
        str_new = str(getpid()) + '_' + str(int(time()))
        output_file = splitext(output_file)[0] + '_' + str_new + splitext(output_file)[1]
    df.to_csv(output_file, index_label=index_label)
    return output_file

def df_concat(lst, axis=0, ignore_index=False, sort=False):
    '''
    Concatenate and returns data frame
    including all data frames in a list.
    '''
    df_ = []
    df_.append(x for x in lst)
    return pd.concat(*df_, axis=axis, ignore_index=ignore_index, sort=sort)

def df_filter_timestamp(df, min_date=None, max_date=None, column=None):
    '''
    Fillter values by date strings using timestamps.
    Time traveling issues might happen after 2038.
    '''
    err = 'Error: expected "YYYY-MM-DD" or "YYYY-MM-DD HH:MM:SS".'

    if not min_date:
        min_date = "1970-01-01 00:00:00"
    if len(min_date) == 19:
        min_value = int(datetime.strptime(min_date, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).timestamp())
    elif len(min_date) == 10:
        min_value = int(datetime.strptime(min_date+" 00:00:00", "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).timestamp())
    else: print(err); return None

    if not max_date:
        max_date = "2038-01-19 03:14:07"
    if len(max_date) == 19:
        max_value = int(datetime.strptime(max_date, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).timestamp())
    elif len(max_date) == 10:
        max_value = int(datetime.strptime(max_date+" 23:59:59", "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).timestamp())
    else: print(err); return None

    df_filtered = df_filter_interval(df, min_value, max_value, column=column)
    return df_filtered

def df_filter_interval(df, min_value=None, max_value=None, column=None):
    '''
    Filter values by numeric interval.
    '''
    if not column:
        print('Error: missing column field name.')
        return None

    elif all(v != None for v in [min_value, max_value]):
        df_filtered = df[df[column] < max_value][df[column] > min_value]
    elif min_value != None:
        df_filtered = df[df[column] > min_value]
    elif max_value != None:
        df_filtered = df[df[column] < max_value]

    else: print('Error: missing minimum or maximum value.')

    print('Selected', len(df_filtered), 'rows out of', len(df))
    return df_filtered

def df_filter_text(df, text=str, column=None):
    '''
    Filter values by string according to rule.
    '''
    if column == None:
        print('Error: missing column field name.')
        return None

    df_filtered = df[~(df[column].str.contains(text))]
    print('Selected', len(df_filtered), 'rows out of', len(df))
    return df_filtered

def df_groupsort(df, group_by=None, sort_by=None, ascending=False, n=None):
    '''
    Return n items in data frame after sorting by
    column and grouping by the specified attribute.
    '''
    df_ = []

    if sort_by:
        df = df.sort_values(sort_by, ascending=ascending)

    if group_by:
        for i in sorted(range(0, len(df[group_by].unique()))):
            df_grouped = df[df[group_by] == i][:n]
            df_.append(df_grouped)
        # concatenate all in a new dataframe
        return pd.concat(df_, axis=0, ignore_index=False, sort=True)
    return df[:n]

def df_worldmap(filename=None):
    '''
    Return data frame with country names and codes
    for plotting a global heatmap with Plotly.
    '''
    df = pd.DataFrame.from_dict(WORLDMAP, orient='index', columns=['country_code'])
    df['country'] = df.index
    df['value'] = 0
    df.index = pd.RangeIndex(len(df.index))
    df.reset_index(drop=True)

    if not filename:
        return df

    c = pd.read_csv(filename)
    c = c.groupby('country')['country'].count()
    c = pd.DataFrame([c]).T

    dict_country = defaultdict(int)

    for i in c['country'].items():
        country = i[0]
        value = i[1]
        dict_country[country] = value

    for i in df.index:
        country = df.iloc[i]['country']
        value = dict_country[country]
        df.loc[i, 'value'] = value

    return df

def df_check(df):
    '''
    Returns a data frame
    containing each column:
    * max_len: maximum length
    * max_value: maximum value
    * column_type: series data type
    * unique_values: total unique
    * null_values: total null
    * max_bytes: from max_value
    '''
    d = {}

    for c in df.columns:

        max_len = 0
        max_value = 0

        if df[c].dtype in (np.float64, np.int64):
            max_len = None
            max_value = int(df[c].max())

        else: # elif df[c].dtype == np.object:
            for v in df[c]:
                try: newlen = len(str(v))
                except: continue
                if (newlen > max_len):
                    max_len = newlen
                    max_value = v

        column_type = df[c].dtype
        num_unique = len(df[c].unique())
        num_null = df[c].isna().sum()
        max_bytes = int(getsizeof(max_value))\
                    if max_value != 0 else v

        d[c] = {'column_type': column_type,
                'max_len': max_len,
                'max_value': max_value,
                'unique_values': num_unique,
                'null_values': num_null,
                'max_bytes': max_bytes}

    return pd.DataFrame.from_dict(d).transpose()
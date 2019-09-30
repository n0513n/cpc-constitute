#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
This module contains functions for writing
Excel XLS/XSLX files to and from CSV files.
'''

import pandas as pd

from csv import writer, QUOTE_MINIMAL
from os import makedirs
from os.path import basename, exists, splitext
from xlrd import open_workbook

def xls2csv(input_file, output='.', delimiter=',',
    skip_blank_lines=True, quoting=QUOTE_MINIMAL):
    '''
    Converts Excel (xls/xlsx) format files to CSV.
    '''
    name, ext = splitext(input_file)
    name = basename(name)

    input_xls = open_workbook(input_file)
    sheets = input_xls.sheet_names()

    if not exists(output):
        makedirs(output)

    lst = []
    for i in sheets:
        s = input_xls.sheet_by_name(i)
        o = output+'/'+name+'_'+str(i)+'.csv'
        with open(o, 'w') as f:
            w = writer(f, quoting=quoting)
            for line in range(s.nrows):
                row = s.row_values(line)
                if skip_blank_lines\
                and all('' == r for r in row):
                    continue
                w.writerow(row)
        lst.append(o)

    return lst

def csv2xls(input_files, output=None,
    skip_blank_lines=True, quoting=QUOTE_MINIMAL):
    '''
    Converts CSV format file to Excel (xls).
    '''
    if isinstance(input_files, str):
        input_files = [input_files]

    if not output:
        name, ext = (input_files[0])
        output = basename(name)+'.csv'

    # for i in input_files:
    # to-do: concatenate as sheets
    pd.read_csv(input_files[0]).to_excel(output)
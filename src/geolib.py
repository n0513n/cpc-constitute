#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
This module downloads and reads geocode locations
available from GeoNames gazetteer datasets.

Country or city-based geolocations are available
from the official site in the URL below:

http://download.geonames.org/export/dump/
'''

import zipfile

from csv import reader
from collections import defaultdict
from os import getpid, remove
from os.path import exists, isfile
from subprocess import call

from webbrowser import open as web_open

def get_geonames(input_name='', output='.'):
    '''
    Download a GeoNames gazetteer and
    unzip it to specified output path.
    '''
    if input_name in ('', None):
        print('Opening GeoNames on browser...')
        print("http://download.geonames.org/export/dump/")
        return

    if len(input_name) == 2:
        input_name = input_name.upper()

    name = input_name + ".zip"
    url = "http://download.geonames.org/export/dump/" + name
    output_file = output + "/" + name

    if not isfile(output_file):
        print('Downloading', url + '...')
        call(['wget', url, '-O', output_file]) # , shell=True

    if isfile(output_file):
        print('Extracing', output_file + '...')
        with zipfile.ZipFile(output_file) as z:
            z.extractall(path=output)
        print('Cleaning up...')
        remove(output_file)

def load_geonames(filename):
    ''''
    Returns a GeoNames gazetteer read
    from a file in dictionary format.
    '''
    geonames = defaultdict(dict)

    with open(filename, 'rt', encoding='utf8') as csvfile:
        csvfile = reader(csvfile, delimiter='\t')
        for line in csvfile:
            geoname_id = line[0]
            name = line[1].lower()
            latitude = str(line[4])
            longitude = str(line[5])
            country_code = line[8]
            # Twitter returns longitude first, latitude second
            geonames[country_code][name] = (longitude, latitude, geoname_id)

    countries = 0
    locations = 0

    for c in geonames:
        countries += 1
        locations += len(geonames[c])

    print('Loaded', countries, 'countries and', locations, 'locations.\n')

    return geonames
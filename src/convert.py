#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
This module contains the legacy function for
converting tweet objects to array of strings.
'''

import json
import time

from csv import writer, QUOTE_MINIMAL
from datetime import datetime
from os import getpid
from os.path import basename, exists, splitext

HEADER_TWEETS = ['tweet_text', 'retweet_count', 'favorite_count', 'followers_count', 'original_tweet_screen_name',
    'retweet_screen_name', 'original_tweet_created_at', 'retweet_created_at', 'retweet_id', 'original_tweet_id',
    'original_tweet_coordinates', 'retweet_coordinates', 'original_tweet_user_id', 'retweet_user_id', 'search_string',
    'is_retweet', 'timestamp', 'type', 'source', 'in_reply_to_status_id', 'in_reply_to_screen_name', 'in_reply_to_user_id',
    'quoted_id', 'quoted_screen_name', 'quoted_user_id', 'quoted_created_at', 'quoted_coordinates', 'place_name',
    'place_fullname', 'place_country', 'place_cc', 'place_bb', 'media_url', 'media_expanded_url', 'lang']

HEADER_USERS = ['screen_name', 'id_str', 'name', 'statuses_count', 'followers_count', 'friends_count', 'listed_count',
    'favourites_count', 'created_at', 'lang', 'location', 'time_zone', 'description', 'url', 'protected',
    'default_profile', 'default_profile_image', 'verified']

def convert_json_tweets(input_file, delimiter=',', output_file=None, redux=False):
    '''
    Convert a JSON streaming dataset to CSV format
    using the above load_tweet_object() function.
    '''
    int_valid_lines = 0

    if not output_file:
        output_file = basename(input_file).replace('.json','.csv')

    if exists(output_file):
        # append process ID and timestamp
        file_name, file_ext = splitext(output_file)
        str_unique = str(getpid()) + '_' + str(int(time.time()))
        output_file = file_name + '_' + str_unique + file_ext
        print('Warning: output file set as', output_file + '.')

    print('Converting', input_file + '...')

    with open(output_file, 'w', newline='', encoding='utf8') as csvfile:
        file_writer = writer(csvfile, delimiter=delimiter, quoting=QUOTE_MINIMAL)
        file_writer.writerow(HEADER_TWEETS)

        with open(input_file, 'rb') as tweet_file:
            for tweet in tweet_file:
                tweet = tweet.decode('utf8', 'ignore')
                tweet = json.loads(tweet)
                tweet = load_tweet_object(tweet, redux=redux)
                file_writer.writerow(tweet)
                int_valid_lines += 1

    print('Read', int_valid_lines, 'valid tweets.')

def load_tweet_object(tweet, search_string='', legacy=False, redux=False):
    '''
    Read Twitter data returned from API.
    '''
    tweet_text = (tweet['full_text']\
                 if 'full_text' in tweet\
                 else tweet['text'])\
                 .replace('\n', ' ')\
                 .replace('\r', ' ')

    tweet_type = 'Tweet'
    is_retweet = False

    place_name = None
    place_fullname = None
    place_country = None
    place_cc = None
    place_bb = None

    media_url = None
    media_expanded_url = None
    media_source_status_id = None
    media_source_status_user_id = None

    in_reply_to_status_id = None
    in_reply_to_screen_name = None
    in_reply_to_user_id = None

    retweet_id = None
    retweet_user_id = None
    retweet_coordinates = None
    retweet_created_at = None
    retweet_screen_name = None

    quoted_id = None
    quoted_user_id = None
    quoted_coordinates = None
    quoted_created_at = None
    quoted_screen_name = None

    favorite_count = tweet['favorite_count']
    retweet_count = tweet['retweet_count']
    followers_count = tweet['user']['followers_count']
    lang = tweet['lang']

    tweet_id = tweet['id_str']
    tweet_screen_name = tweet['user']['screen_name']
    tweet_user_id = tweet['user']['id_str']
    tweet_coordinates = tweet['coordinates']
    tweet_created_at = time.strftime('%Y-%m-%d %H:%M:%S',
        time.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y'))

    timestamp = int(datetime.strptime(tweet['created_at'], "%a %b %d %H:%M:%S +0000 %Y").timestamp())

    if redux: # get only fields required for TSM
        return [tweet_screen_name, tweet_text.replace(","," "), time.strftime("%x", time.gmtime(timestamp))]

    source = tweet['source']
    head, sep, tail = source.partition('<')
    head, sep, tail = source.partition('>')
    source = tail.replace('</a>', '')

    if 'place' in tweet and tweet['place']:
        place_name = tweet['place']['name']
        place_fullname = tweet['place']['full_name']
        place_country = tweet['place']['country']
        place_cc = tweet['place']['country_code']
        if 'bounding_box' in tweet and 'coordinates' in tweet['bounding_box']:
            place_bb = tweet['place']['bounding_box']['coordinates']

    if 'coordinates' in tweet and tweet['coordinates']:
        tweet_coordinates = tweet['coordinates']

    if 'entities' in tweet and tweet['entities']:
        if 'media' in tweet['entities'] and tweet['entities']['media']:
            media_url = tweet['entities']['media'][0]['media_url']
            media_expanded_url = tweet['entities']['media'][0]['expanded_url']

    if tweet['in_reply_to_status_id']:
        tweet_type = 'reply'
        in_reply_to_status_id = tweet['in_reply_to_status_id_str']
        in_reply_to_screen_name = tweet['in_reply_to_screen_name']
        in_reply_to_user_id = tweet['in_reply_to_user_id_str']

    if 'retweeted_status' in tweet:
        is_retweet = True
        tweet_type = 'retweet'

        rt_text = (tweet['retweeted_status']['full_text']\
                  if 'full_text' in tweet['retweeted_status']\
                  else tweet['retweeted_status']['text'])\
                  .replace('\n', ' ')\
                  .replace('\r', ' ')

        favorite_count = tweet['retweeted_status']['favorite_count']
        retweet_count = tweet['retweeted_status']['retweet_count']
        followers_count = tweet['retweeted_status']['user']['followers_count']

        retweet_id = tweet['retweeted_status']['id_str']
        retweet_screen_name = tweet['retweeted_status']['user']['screen_name']
        retweet_user_id  = tweet['retweeted_status']['user']['id_str']
        retweet_coordinates = tweet['retweeted_status']['coordinates']
        retweet_created_at = time.strftime('%Y-%m-%d %H:%M:%S',
            time.strptime(tweet['retweeted_status']['created_at'], '%a %b %d %H:%M:%S +0000 %Y'))

        if 'quoted_status' in tweet['retweeted_status']:
            tweet['quoted_status'] = tweet['retweeted_status']['quoted_status']

    if 'quoted_status' in tweet:
        tweet_type = 'quote'

        quoted_text = (tweet['quoted_status']['full_text']\
                      if 'full_text' in tweet['quoted_status']\
                      else tweet['quoted_status']['text'])\
                      .replace('\n', ' ')\
                      .replace('\r', ' ')

        favorite_count = tweet['quoted_status']['favorite_count']
        retweet_count = tweet['quoted_status']['retweet_count']
        followers_count = tweet['quoted_status']['user']['followers_count']

        quoted_id = tweet['quoted_status']['id_str']
        quoted_screen_name = tweet['quoted_status']['user']['screen_name']
        quoted_user_id  = tweet['quoted_status']['user']['id_str']
        quoted_coordinates = tweet['quoted_status']['coordinates']
        quoted_created_at = time.strftime('%Y-%m-%d %H:%M:%S',
            time.strptime(tweet['quoted_status']['created_at'],'%a %b %d %H:%M:%S +0000 %Y'))

    # ensure full text workaround
    if tweet_text.endswith('…')\
    and tweet_text.startswith('RT @'):
        a,b = tweet_text.rstrip('…').split(': ',1)
        if tweet_type == 'retweet' and rt_text.startswith(b):
            tweet_text = str(a+': '+rt_text)
        elif tweet_type == 'quote' and quoted_text.startswith(b):
            tweet_text = str(a+': '+quoted_text)

    data = [tweet_text, retweet_count, favorite_count, followers_count, tweet_screen_name, retweet_screen_name,
            tweet_created_at, retweet_created_at, retweet_id, tweet_id, tweet_coordinates, retweet_coordinates,
            tweet_user_id, retweet_user_id, search_string, is_retweet, # <-- legacy stops here
            timestamp, tweet_type, source, in_reply_to_status_id, in_reply_to_screen_name, in_reply_to_user_id,
            quoted_id, quoted_screen_name, quoted_user_id, quoted_created_at, quoted_coordinates, place_name,
            place_fullname, place_country, place_cc, place_bb, media_url, media_expanded_url, lang]

    # keep true to MySQL rules (legacy)
    # for i in range(0, data.__len__()):
    #     if type(data[i]) == dict:
    #         data[i] = str(data[i])

    return data[:15] if legacy else data

def load_user_object(user):
    '''
    Read user data returned from API.
    '''
    screen_name = user['screen_name']
    id_str = user['id_str']
    name = user['name']
    statuses_count = user['statuses_count']
    followers_count = user['followers_count']
    friends_count = user['friends_count']
    listed_count = user['listed_count']
    favourites_count = user['favourites_count']
    created_at = user['created_at']
    lang = user['lang']
    time_zone = user['time_zone']
    profile_image_url = user['profile_image_url']
    default_profile = str(user['default_profile']).replace('False', '')
    default_profile_image = str(user['default_profile_image']).replace('False', '')
    protected = str(user['protected']).replace('False', '')
    verified = str(user['verified']).replace('False', '')

    if user['url']:
        url = user['url'].replace('\n', ' ').replace('\r', ' ')
    else: url = ''

    if user['description']:
        description = user['description'].replace('\n', ' ').replace('\r', ' ')
    else: description = ''

    if user['location']:
        location = user['location'].replace('\n', ' ').replace('\r', ' ')
    else: location = ''

    data = [screen_name, id_str, name, statuses_count, followers_count, friends_count,
            listed_count, favourites_count, created_at, lang, location, time_zone,
            description, url, protected, default_profile, default_profile_image, verified]

    return data
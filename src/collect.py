#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Collect tweets by text, location, tweet IDs, user names or IDs.
]
Query input might be empty if coordinates are given as in:
    'latitude,longitude,radius' eg. '-20.3,-40.1,100km'

Multiple API keys are accepted in the following format:
    [['api_key_1','api_secret_1'],['api_key_2','api_secret_2']]

Accepts different query types:
    'tweets' - strings such as words and hashtags
    'timeline' - array of user names/IDs
    'ids' - array of tweet IDs
    'id' - a single tweet ID
    'retweets' - a single tweet ID
    'retweeters' - a single tweet ID
    'users' - array of user names/IDs
    'user' - a single user name/ID
    'friends' - a single user name/ID
    'followers' - a single user name/ID

Available extension formats for output writing:
    'json' - full output returned from Twitter
    'csv' - store only selected data from tweets
    'txt' - dehydrated output like IDs only

More information on query operators is available at:
    https://dev.twitter.com/rest/public/search
"""

import json

from collections import OrderedDict
from csv import writer, QUOTE_MINIMAL
from os import makedirs
from os.path import abspath, splitext
from os.path import exists, isfile
from time import time, sleep
from tqdm import tqdm
#from twython import Twython, TwythonError
from twython import TwythonRateLimitError

from api import twython_auth, post_tweets, sleep_seconds
from convert import HEADER_TWEETS, load_tweet_object
from convert import HEADER_USERS, load_user_object

try: from config import TWITTER_KEYS
except: TWITTER_KEYS = []

def collect_twitter(query,
    app_keys=TWITTER_KEYS,
    query_type='tweets',
    format='csv',
    output='.',
    output_file=None,
    geocode=None,
    is_user_id=False,
    lang=None,
    limit=0,
    max_id=None,
    post_url=None,
    separator=None,
    since_id=None,
    wait_time=None,
    write_output=True):

    is_split = False # query as split flag
    last_date = None # last captured date
    maximum = None   # last captured ID
    max_retries = 3  # skip when reaching number
    current = 0      # current ongoing query
    total = 0        # total tweets captured
    tts = 900        # time to sleep if error on endpoint
    count = 100      # number of tweets in each query

    if limit and limit < count:
        count = limit # set tweets max limit to receive

    if isinstance(query, str):
        # read from file
        if isfile(query):
            query_strings = []
            with open(query, 'rt', encoding='utf8') as f:
                for line in f:
                    query_strings.append(line.rstrip('\n'))
            query = list(OrderedDict.fromkeys(query_strings).keys())
        # transform to list
        else: query = query.split(separator) if separator else [query]

    int_len_query = len(query) # read total count

    # default format and extension
    if query_type in ('retweeters', 'friends', 'followers'):
        format = 'txt'

    # default header if CSV format
    header = HEADER_TWEETS
    if query_type.startswith('user'):
        header = HEADER_USERS

    # output paths
    if not exists(output):
        makedirs(output)
    if not output_file:
        output_file = output+'/'+query_type+'.'+format

    # error messages to re-authenticate
    auth_on = ['429 (Too Many Requests)']

    # error messages to break on return
    break_on = ['401 (Unauthorized)',
                '403 (Forbidden)',
                '404 (Not Found)']

    # error messages to sleep on return
    sleep_on = ['503 (Service Unavailable)']

    # split IDs into hundreds
    if query_type == 'ids':
        query = split_list(query, count)
        int_len_query = int(int_len_query/count)
        is_split = True

    # log into Twitter
    twitter = twython_auth(app_keys, query_type)
    sleep(0.25)

    with open(output_file, 'w', newline='', encoding='utf8') as f:
        file_writer = writer(f, delimiter=',', quoting=QUOTE_MINIMAL)
        file_writer.writerow(header) if format == 'csv' else None

        while True:
            #t = tqdm(query, ascii=True, total=int_len_query, desc='Collecting')
            for q in query:
                current += (len(q) if is_split else 1)
                captured = 0            # number of tweets captured in this query
                cursor = 0              # navigate from query to query
                finished = False        # flag to mark when done collecting
                first_id = None         # first captured ID for future searches
                first_date = None       # first ID captured date string
                int_retries = 0         # counter to stop retrying query
                maximum = max_id        # oldest tweet to finish capturing
                minimum = since_id      # most recent tweet to start capturing
                previous_cursor = None  # iterate through results
                previous_results = None # compare returned output
                search_results = None   # returned output itself

                # if query_type in ('tweets', 'users', 'userids'):
                #     print('\nCollecting', ('"' + q + '"' if query_type == 'tweets' else ('@' + q + ' timeline')),
                #           '(' + str(current) + '/' + str(len(query)) + ')...')

                while True: # keep searching
                    try: # collecting
                        if query_type == 'tweets':
                            search_results = twitter.search(q=q,
                                                tweet_mode='extended',
                                                count=count,
                                                lang=lang,
                                                max_id=maximum,
                                                since_id=minimum,
                                                geocode=geocode)
                            search_results = search_results['statuses']

                        elif query_type == 'timeline':
                            search_results = twitter.get_user_timeline(screen_name=q if not is_user_id else None,
                                                user_id=q if is_user_id else None,
                                                tweet_mode='extended',
                                                count=count,
                                                max_id=maximum,
                                                since_id=minimum)

                        elif query_type == 'users':
                            search_results = twitter.lookup_user(screen_name=q if not is_user_id else None,
                                                user_id=q if is_user_id else None,
                                                include_entities=False)

                        elif query_type == 'user':
                            search_results = twitter.show_user(screen_name=q if not is_user_id else None,
                                                user_id=q if is_user_id else None,
                                                include_entities=False)
                            search_results = [search_results] # <-- to list

                        elif query_type == 'ids':
                            search_results = twitter.lookup_status(id=q,
                                                tweet_mode='extended')

                        elif query_type == 'id':
                            search_results = twitter.show_status(id=q,
                                                tweet_mode='extended')
                            search_results = [search_results] # <-- to list

                        elif query_type == 'retweets':
                            search_results = twitter.get_retweets(id=q,
                                                tweet_mode='extended')

                        elif query_type == 'retweeters':
                            seach_results = twitter.get_retweeters_ids(id=q,
                                                count=count,
                                                cursor=cursor)
                            cursor = search_results['next_cursor']
                            search_results = search_results['ids']

                        elif query_type == 'friends':
                            seach_results = twitter.get_friends_ids(id=q,
                                                count=count,
                                                cursor=cursor)
                            cursor = search_results['next_cursor']
                            search_results = search_results['ids']

                        elif query_type == 'followers':
                            seach_results = twitter.get_followers_ids(id=q,
                                                count=count,
                                                cursor=cursor)
                            cursor = search_results['next_cursor']
                            search_results = search_results['ids']

                        # check if the output is new
                        if (previous_results == search_results):
                            break

                        # iterate through returned tweets
                        for some_results in split_list(search_results, 10):
                            statuses = [] # array to store and send tweets

                            for status in some_results:
                                captured += 1 # data returned from this query
                                total += 1 # data returned from all queries

                                tweet_text = status['full_text'].replace("\n", "")
                                tweet_username = '@' + status['user']['screen_name']
                                print(tweet_username, str(' ')*int(20-len(tweet_username)), tweet_text, '(' + status['id_str'] + ')')

                                if post_url:
                                    tweet = json.dumps(status)
                                    statuses.append(tweet)

                                if write_output:

                                    if format == 'json':
                                        # write output data to JSON file
                                        json.dump(status, f, sort_keys=True)#, indent=4)
                                        f.write('\n')

                                    elif format == 'csv':
                                        # load data and write to CSV file
                                        if query_type in ('users', 'user'):
                                            row = load_user_object(status)
                                        else: row = load_tweet_object(status)#, redux=True)
                                        file_writer.writerow(row)

                                    elif format == 'txt':
                                        # write output IDs to text file
                                        if 'id' in status:
                                            f.write(str(status['id'])+'\n')
                                        else: f.write(status+'\n')

                                if 'id' in status:
                                    maximum = (status['id'] - 1)
                                    if not first_id:
                                        first_id = status['id']

                                if 'created_at' in status:
                                    last_date = status['created_at'].replace(' +0000','')
                                    if not first_date:
                                        first_date = status['created_at'].replace(' +0000','')

                            if post_url: # send to API endpoint
                                post_tweets(statuses, post_url)

                        #t.set_description("Collecting (%i total)" % total)
                        #t.refresh()

                        cond1 = is_split
                        cond2 = (not search_results)
                        cond3 = (limit and limit != 0 and captured >= limit)
                        cond4 = (max_id and int(maximum) >= int(max_id))
                        cond5 = (since_id and int(minimum) <= int(since_id))
                        cond6 = (previous_cursor == cursor) and (previous_results == search_results)

                        if any(c for c in [cond1,cond2,cond3,cond4,cond5,cond6]):
                            break

                        previous_cursor = cursor
                        previous_results = search_results

                    except TwythonRateLimitError:
                        twitter = twython_auth(app_keys, query_type)

                    except KeyboardInterrupt:
                        print('Finishing...'); return

                    except Exception as e:
                        raise # <-- uncomment this line if bug-hunting!

                        int_retries += 1
                        print('Warning:', str(e))

                        if int_retries == max_retries\
                        or any(x in str(e) for x in break_on):
                            break

                        elif any(x in str(e) for x in auth_on):
                            twitter = twython_auth(api_keys, query_type)

                        elif any(x in str(e) for x in sleep_on):
                            sleep_seconds(15)

            if isinstance(wait_time, int):
                since_id = first_id
                print('Got', total if query_type in ('ids', 'reweeters') else captured,
                      'tweets. Last:', last_date, 'ID:', maximum)
                sleep_seconds(wait_time)
            else: break

    if total == 1 and header == HEADER_TWEETS:
        text = status['full_text'] if 'full_text' in status else status['text']
        user = status['user']['screen_name']
        url = 'https://twitter.com/'+user+'/'+str(first_id)
        print('Got 1 tweet from @' + user + '.\nURL:'+url+'\n'+text)

    elif total > 1:
        print('\nGot', total, 'total', ('tweets' if query_type == 'timeline' else query_type) + '.',
              '\nFirst:', first_id,
              '\nLast:', maximum,
              '\nSince:', first_date,
              '\nUntil:', last_date)

def split_list(iterable, chunksize=100):
    '''
    Split an array in iterables of N items.
    '''
    for i,c in enumerate(iterable[::chunksize]):
        yield iterable[i*chunksize:(i+1)*chunksize]
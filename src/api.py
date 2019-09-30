#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Authenticate using Twitter's credentials as in 'config.py'.

More information on API rate limits is available at:
    https://dev.twitter.com/rest/public/rate-limits
"""

from datetime import datetime
from requests import post
from time import time, sleep
from twython import Twython, TwythonRateLimitError

import mysql.connector

def connect_mysql(HOST, DB, USER, PWD):
    '''
    Connect to the MySQL database to send tweets to.
    '''
    try: db = mysql.connector.connect(host=HOST,
                                      database=DB,
                                      user=USER,
                                      password=PWD)

    except Exception as e:
        print(str(e))

    return db

def twython_auth(app_keys, query_type='tweets'):
    '''
    Authenticate to Twitter using multiple credentials.
    '''
    resource = {
        'tweets': ['search', '/search/tweets'],
        'timeline': ['statuses', '/statuses/user_timeline'],
        'ids': ['statuses', '/statuses/lookup'],
        'id': ['statuses', '/statuses/show/:id'],
        'retweets': ['statuses', '/statuses/retweets/:id'],
        'retweeters': ['statuses', '/statuses/retweeters/ids'],
        'users': ['users', '/users/lookup'],
        'user': ['users', '/users/show/:id'],
        'friends': ['friends', '/friends/ids'],
        'followers': ['followers', '/followers/ids'],
        'trends': ['trends', '/trends/place']}

    rtype = resource[query_type][0]
    rpoint = resource[query_type][1]
    remaining = 0
    len_app_keys = len(app_keys)

    while True:
        tts = 900
        rate_limit_exceeded = False

        for key in app_keys:
            try: # authenticate
                twitter = Twython(key[0], key[1], oauth_version=2)
                access_token = twitter.obtain_access_token()
                twitter = Twython(key[0], access_token=access_token)
                rate_limit_status = twitter.get_application_rate_limit_status(resources=rtype)
                rate_limit_status = rate_limit_status['resources'][rtype][rpoint]
                reset = rate_limit_status['reset'] - time() + 1
                remaining = rate_limit_status['remaining']
                limit = rate_limit_status['limit']

                if remaining > 0:
                    print('Requests left:', str(remaining) + '/' + str(limit),
                          '(' + str(app_keys.index(key)+1) + '/' + str(len_app_keys) + ')')
                    return twitter

                elif tts > reset:
                    tts = reset

            except TwythonRateLimitError:
                rate_limit_exceeded = True

            except Exception as e:
                #raise # <-- uncomment line if bug-hunting
                print('Warning:', e)

        if remaining == 0:
            print('Warning: 0 requests left.')\
                if rate_limit_exceeded else None

            sleep_seconds(tts)

def post_tweets(array, url, max_retries=3):
    '''
    Send tweets array to API endpoint.
    '''
    count = 0
    while True:
        if count == max_retries:
            break
        count += 1
        response = post(url, json=array)
        print(response)
        if '200' not in str(response):
            print('\nWarning: error sending tweets to API endpoint.')
            # print(response) # <-- uncomment to print response error
            sleep_seconds(3)
        else: break

def sleep_seconds(tts):
    '''
    Sleep for a given amount of seconds.
    '''
    ttw = datetime.fromtimestamp(int(time() + tts))
    ttw = datetime.strftime(ttw, "%H:%M:%S")
    print('Sleeping', str(int(tts)) + 's until', ttw + '.')
    for i in range(3):
        sleep(0.5)
        print('.')
    sleep(tts)
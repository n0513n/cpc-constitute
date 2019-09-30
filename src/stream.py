#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Get a sample of currently flowing data on Twitter
or stream tweets by keywords, writing to an output
file or sending to an external API endpoint.

Requires API key/secret and token key/secret.

More information on query operators can be read at:
    https://dev.twitter.com/rest/public/search

Documentation on the sample of flowing tweets:
    https://dev.twitter.com/en/docs/tweets/sample-realtime/api-reference/get-statuses-sample
"""

import json

from os import makedirs
from os.path import abspath, exists
from requests import post
from time import time
from twython import TwythonStreamer

from api import post_tweets

try: # user credentials
    from config import TWITTER_TOKENS
    APP_KEY = TWITTER_TOKENS[0][0]
    APP_SECRET = TWITTER_TOKENS[0][1]
    OAUTH_TOKEN = TWITTER_TOKENS[0][2]
    OAUTH_SECRET = TWITTER_TOKENS[0][3]
except: # all empty
    APP_KEY = None
    APP_SECRET = None
    OAUTH_TOKEN = None
    OAUTH_SECRET = None

try: # capture @-messages
    from config import STREAM_ATS
except: STREAM_ATS = True

try: # capture retweets
    from config import STREAM_RTS
except: STREAM_RTS = True

class Stream(TwythonStreamer):
    '''
    Execute action on every streamed tweet.
    '''
    def on_success(self, data):
        if 'text' in data:
            load_tweet(data)

    def on_error(self, status_code, data):
        print(status_code, data)
        return True # don't quit streaming
        # self.disconnect() # quit streaming

    def on_timeout(self):
        print >> sys.stderr, 'Timeout...'
        return True # don't quit streaming

def stream_tweets(query="",
    stream_type='filter',
    app_key=APP_KEY,
    app_secret=APP_SECRET,
    oauth_token=OAUTH_TOKEN,
    oauth_secret=OAUTH_SECRET,
    ats=STREAM_ATS,
    rts=STREAM_RTS,
    limit=None,
    interval=10,
    output='.',
    post_url=None,
    quiet=False):

    global TWEETS, CAPTURED, LIMIT, OUTPUT, POST_URL
    global INTERVAL, QUIET, TOTAL_ATS, TOTAL_RTS
    global stream

    if not exists(output):
        makedirs(output)

    output = abspath(output+'/tweets.json')

    TWEETS = []         # array of tweets to send
    CAPTURED = 0        # captured tweets counter
    TOTAL_ATS = 0       # captured @-messages counter
    TOTAL_RTS = 0       # captured retweets counter
    LIMIT = limit       # maximum number of tweets to capture
    OUTPUT = output     # output file name to write tweets
    POST_URL = post_url # endpoint URL to send tweets to
    INTERVAL = interval # number of tweets to send at once
    QUIET = quiet       # True for less verbose output

    # requires authentication as of Twitter API v1.1
    stream = Stream(app_key, app_secret, oauth_token, oauth_secret)

    if (not query) or (stream_type == 'sample'):
        stream.statuses.sample()

    elif stream_type == 'filter': # default
        stream.statuses.filter(track=query)

    # stream.site(follow='twitter')
    # stream.user()

def load_tweet(data):
    '''
    Store tweet to array in JSON format.
    '''
    def send_tweets():
        '''
        Send tweets array to API endpoint.
        '''
        post_tweets(TWEETS, POST_URL)

    def flush_tweets():
        '''
        Reset tweets array after successful post.
        '''
        global TWEETS
        TWEETS = []

    def write_tweet_json(data):
        '''
        Write tweets to JSON output file.
        '''
        with open(OUTPUT, 'a', encoding='utf8') as f:
            json.dump(data, f, sort_keys=True)#, indent=4)
            f.write('\n')

    def print_tweet(data):
        '''
        Print captured tweet on terminal screen.
        '''
        tweet_text = data['text'].encode('utf8', 'ignore').decode('ascii', 'ignore').replace("\n", "")
        tweet_username = '@' + data['user']['screen_name']
        print(tweet_username, str(' ')*int(20-len(tweet_username)), tweet_text, '(' + data['id_str'] + ')')

    global CAPTURED, TOTAL_ATS, TOTAL_RTS, stream

    is_at = True if data['in_reply_to_status_id'] else False # tweet_text.startswith('@')
    is_rt = True if 'retweeted_status' in data else False # tweet_text.startswith('RT @')
    is_tweet = all(not i for i in [is_at, is_rt])
    TOTAL_ATS += 1 if is_at else 0
    TOTAL_RTS += 1 if is_rt else 0

    if is_tweet or (is_at and STREAM_ATS) or (is_rt and STREAM_RTS):
        CAPTURED += 1

        # print stdout
        if QUIET:
            print('Got', CAPTURED, 'tweets (' +\
              str("%0.2f"%(TOTAL_RTS*100/CAPTURED)) + '% RTs and ' +\
              str("%0.2f"%(TOTAL_ATS*100/CAPTURED)) + '% @-messages).')\
            if (CAPTURED/100).is_integer() else None
        else: print_tweet(data)

        # write to file
        if OUTPUT:
            write_tweet_json(data)

        # append to array
        if POST_URL:
            tweet = json.dumps(data)
            TWEETS.append(tweet)

            # send to URL and reset var
            if CAPTURED >= LIMIT or len(TWEETS) == INTERVAL:
                send_tweets() if bool(POST_URL) else None
                flush_tweets()

    if LIMIT and CAPTURED >= LIMIT:
        print('\nGot', CAPTURED, 'total tweets.')
        stream.disconnect()
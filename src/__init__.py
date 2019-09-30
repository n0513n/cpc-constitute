    #!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
This module contains functions for E-CONSTITUINTE.
'''

import json
import networkx as nx
import pandas as pd
import requests
import wikipedia

from datetime import datetime, timedelta
from google import google
from newsapi import NewsApiClient
#from newsplease import NewsPlease

from dflib import df_concat

NEWS_API_KEY = 'e974ed5a947d40e69163ef97bffdc71c'

def news_top_headlines(query, lang='en', days=30, start_date=None, end_date=None):
    newsapi = NewsApiClient(api_key=NEWS_API_KEY)

    if not start_date: # "2019-01-31"
        start_date = datetime.today().strftime("%Y-%m-%d")

    if not end_date: # "YYYY-MM-DD"
        end_date = (datetime.today() - timedelta(days=days)).strftime("%Y-%m-%d")

    # /v2/top-headlines
    top_headlines = newsapi.get_top_headlines(q=query, language=lang)
    return top_headlines['articles']

def news_get_everything(query, lang='en', pages=1, days=30, start_date=None, end_date=None, sort_by='popularity'):
    newsapi = NewsApiClient(api_key=NEWS_API_KEY)

    if not start_date: # "2019-01-31"
        start_date = datetime.today().strftime("%Y-%m-%d")

    if not end_date: # "YYYY-MM-DD"
        end_date = (datetime.today() - timedelta(days=days)).strftime("%Y-%m-%d")

    articles = []

    for i in range(int(pages)):

        output = newsapi.get_everything(q= query,
                                        language=lang,
                                        from_param=start_date,
                                        to=end_date,
                                        sort_by='popularity',
                                        page=i+1)

        for a in output['articles']:
            articles.append(a)

    return articles

def constitute_query(method_name, params="", output='.'):
    """
    Lists of objects:
        * constitutions
        * topics
        * regions
    Topic searches:
        * constopicsearch
        * sectionstopicsearch
    Free-text search:
        * textsearch
    Constitution HTML:
        * html
    """
    url = "https://www.constituteproject.org/service/<method_name><params>"
    url = url.replace('<method_name>',method_name)
    url = url.replace('<params>',params)
    output = requests.get(url)
    data = output.json()
    with open('cp.json', 'w') as f:
        json.dump(data, f)
    return data

def google_search(query, pages=1):
    """
    Returns for each object:
    obj.name
    obj.link
    obj.google_link
    obj.description
    obj.thumb
    obj.cached
    obj.page
    obj.index
    obj.number_of_results
    """
    return google.search(query, pages)

def wiki_summary(query, sentences=1, lang='en'):
    wikipedia.set_lang(lang)
    return wikipedia.summary("Facebook", sentences=sentences)

def wiki_page(query, lang='en'):
    wikipedia.set_lang(lang)
    return wikipedia.page(query)

def wiki_search(query, lang='en'):
    wikipedia.set_lang(lang)
    return wikipedia.search(query)

def wiki_graph(query, lang='en', n=None):
    G = nx.Graph()
    for q in query:
        w = wikipedia.page(q, lang)
        for i in w.links[:n]:
            G.add_node(i)
            G.add_edge(i,q)
        from plotlib import scatter_plot
    return G

def concat_dict(data):
    dfs = []
    for d in data:
        dfs.append(pd.DataFrame.from_dict(d, orient='index').T)
    return df_concat(dfs)
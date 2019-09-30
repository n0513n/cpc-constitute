#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
This module contains functions for plotting
graphic elements using the NetworkX library.

Tested with NetworkX version 2.3.
'''

import community
import math
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

def ng(graph, name):
    '''
    Returns named NetworkX.Graph() object.
    '''
    graph.name = name
    return graph

def nx_layout(G):
    '''
    Returns nodes and edges for a NetworkX.Graph() object.
    '''
    pos = nx.circular_layout(G)
    data = [[node, *pos[node]] for node in G.nodes]
    nodes = pd.DataFrame(data, columns=['id', 'x', 'y'])
    nodes.set_index('id', inplace=True)
    edges = pd.DataFrame(list(G.edges), columns=['source', 'target'])
    return nodes, edges

def nx_stats(G, it=100, communities=True):
    '''
    Returns a data frame containing network statistics for
    the nodes and their communities for a NetworkX.Graph().

    Note: the number of iterations (it) may need to be raised
    for calculating the eigenvector centrality of the nodes.
    '''
    deg = nx.degree_centrality(G)
    eig = nx.eigenvector_centrality(G, it)
    bet = nx.betweenness_centrality(G)
    clo = nx.closeness_centrality(G)

    df = pd.DataFrame.from_dict([deg, eig, bet, clo])
    df = pd.DataFrame.transpose(df)
    df.columns = ['degree', 'eigenvector', 'betweeness', 'closeness']

    if communities: # louvain method
        partition = community.best_partition(G)
        modularity = community.modularity(partition, G)
        df['partition'] = pd.Series(partition)

    df['name'] = df.index

    print('Groups:', len(df['partition'].unique()),
          '\nModularity:', modularity)

    return df

def nx_plot(G, figsize=(10, 10), show_labels=True):
    '''
    Plots a NetworkX.Graph() object.
    '''
    ndTypes = []
    ndColors = []
    colors = "brcmykwg"

    fig = plt.figure(1, figsize=figsize, dpi=80, facecolor='w', edgecolor='k')
    ax = fig.add_subplot(1,1,1)
    #fig.set_facecolor('w')
    plt.axis('off')

    k = 4 / math.sqrt(len(G.nodes()))
    pos = nx.spring_layout(G, k=k)

    for nd in G.nodes(data=True):
        if 'type' in nd[1]:
            if nd[1]['type'] not in ndTypes:
                ndTypes.append(nd[1]['type'])
            ndColors.append(colors[ndTypes.index(nd[1]['type']) % len(colors)])
        elif len(ndColors) > 1:
            raise RuntimeError("Some nodes do not have a type")

    if len(ndColors) < 1:
        node_color = colors[0]
    else: node_color = ndColors

    nx.draw_networkx_nodes(G, pos=pos, node_color=node_color, node_shape='8', node_size=100, ax=ax)
    nx.draw_networkx_edges(G, pos=pos, width=1, ax=ax)
    nx.draw_networkx_labels(G, pos=pos, font_size=8, ax=ax) if show_labels else None

    plt.show()
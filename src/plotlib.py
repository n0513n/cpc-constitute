#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
This module contains functions for plotting
graphic elements using the plotly library.

Tested with plotly version 3.9.0.
'''

import networkx as nx
import pandas as pd
import plotly.graph_objs as go
#import plotly as py

from dslib import ds_layout
from nxlib import nx_layout

def plot_bar(df, column='degree', n=None, name=None):
    '''
    Returns figure to plot, e.g. as in:
    py.iplot(fig, filename='filename')

    Accepted vars:
        df => data frame
        column => metric to sort
        n => number of nodes
        layout => plot parameters
        name => figure title
    '''
    sorted_df = df.sort_values(column, ascending=False)[:n]

    trace = go.Bar(
        x=sorted_df.index,
        y=sorted_df[column])

    data = [trace]

    if not name:
        name = str('Top '+str(n)+ ' by '+column)

    layout = go.Layout(
        title=name,
        yaxis=dict(title=column))

    fig = go.Figure(data=data, layout=layout)
    return fig

def plot_worldmap(df, layout=None, name='Worldmap'):
    '''
    Returns figure to plot, e.g. as in:
    py.iplot(fig, filename='filename')

    Accepted vars:
        df => data frame
        layout => plot parameters
        name => figure title
    '''
    trace = go.Choropleth(
        locations=df['country_code'],
        z=df['value'],
        text=df['country'],
        colorscale=[
            [0, "rgb(178, 34, 34)"],
            [0.25, "rgb(255, 140, 0)"],
            [0.5, "rgb(255, 255, 51)"],
            [0.75, "rgb(40, 60, 190)"],
            [1, "rgb(230, 230, 250)"]],
        autocolorscale=False,
        reversescale=True,
        marker=go.choropleth.Marker(
            line=go.choropleth.marker.Line(
                color='rgb(180,180,180)',
                width=0.5)),
        colorbar=go.choropleth.ColorBar(
            tickprefix='',
            name='# per country'))

    data = [trace]

    if not layout:
        layout = go.Layout(
            title=go.layout.Title(
                text=name),
            geo=go.layout.Geo(
                showframe=False,
                showcoastlines=False,
                projection=go.layout.geo.Projection(
                    type='equirectangular')),
            annotations=[go.layout.Annotation(
                x=0.55,
                y=0.1,
                xref='paper',
                yref='paper',
                text='Source: Twitter',
                showarrow=False)])

    fig = go.Figure(data=data, layout=layout)
    return fig

def scatter_plot(G, layout='random', name='Network graph'):
    '''
    Returns network in a scatter plot by
    circular, forceatlas2 or random layout.

    Accepted vars:
        G => networkx graph obj
        layout => for nodes positions
        name => graph title
    '''
    minsize = 10 # minimum node size
    ncenter = 0  # first node as center
    dmin = 1     # minimum diameter

    # load test data
    # G = nx.random_geometric_graph(100, 0.1)
    # pos = nx.get_node_attributes(G, 'pos')

    # get nodes and edges
    n, e = nx_layout(G)

    # datashader layout
    nodes = ds_layout(n, e, layout)

    # store positions
    pos = {}
    for n in nodes.index:
        x = nodes.loc[n]['x']
        y = nodes.loc[n]['y']
        pos[n] = [x, y]

    # get center node
    # by its diameter
    for n in pos:
        x, y = pos[n]
        d = (x-0.5)**2+(y-0.5)**2
        if d < dmin:
            ncenter = n
            dmin = d

    # node positions
    x_nodes = []
    y_nodes = []
    for node in G.nodes():
        x, y = pos[node] # G.node[node]['pos']
        x_nodes += tuple([x])
        y_nodes += tuple([y])

    # node traces data
    node_trace = go.Scatter(
        x=x_nodes,
        y=y_nodes,
        text=[],
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            # colorscale options
            #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
            #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
            #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
            colorscale='YlOrRd',
            reversescale=True,
            color=[],
            size=[],
            colorbar=dict(
                thickness=15,
                title='Path Length from Center Node',
                xanchor='left',
                titleside='right'),
            line=dict(
                color='rgb(0, 0, 0)',
                width=2)))

    # edge positions
    x_edges = []
    y_edges = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]] # G.node[edge[0]]['pos']
        x1, y1 = pos[edge[1]] # G.node[edge[1]]['pos']
        x_edges += tuple([x0, x1, None])
        y_edges += tuple([y0, y1, None])

    # edge traces data
    edge_trace = go.Scatter(
        x=x_edges,
        y=y_edges,
        line=dict(width=0.5,color='#888'),
        hoverinfo='none',
        mode='lines')

    # populate attributes
    names = list(G.nodes())
    paths = nx.single_source_shortest_path_length(G, ncenter)
    for node, adjacencies in enumerate(G.adjacency()):
        num_edges = len(adjacencies[1])
        node_name = names[node]
        node_info = 'name: '+node_name+', # of connections: '+str(num_edges)
        node_size = minsize
        if node_name in paths:
            node_size = paths[node_name]*minsize
        node_trace['marker']['size'] += tuple([node_size]) # num_edges*3
        node_trace['marker']['color'] += tuple([num_edges])
        node_trace['text'] += tuple([node_info])

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                    title=name,
                    titlefont=dict(size=16),
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    annotations=[ dict(
                        text="<a href='https://plot.ly/ipython-notebooks/network-graphs/'> https://plot.ly/ipython-notebooks/network-graphs/</a>",
                        showarrow=False,
                        xref="paper", yref="paper",
                        x=0.005, y=-0.002 ) ],
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))
    return fig

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
This module contains functions for plotting
graphic elements using the Datashader library.

For more information on the ForceAtlas2 layout
it implements (JACOMY; VENTURINI; HEYMANN; BASTIAN):

> https://doi.org/10.1371/journal.pone.0098679

Tested with Datashader version 0.7.0,
'''

import datashader as ds
import datashader.transfer_functions as tf

from itertools import chain

from datashader.bundling import connect_edges, hammer_bundle
from datashader.layout import circular_layout, forceatlas2_layout, random_layout

from nxlib import nx_layout

cvsopts = dict(plot_height=400, plot_width=400)

def tf_plot(figs, cols=1):
    '''
    Returns figures to plot split by the number of
    columns set using datashader.transfer_functions().

    Accepted vars:
        figs => list of figures or graphs
        cols => number of columns to plot
    '''
    plots = []
    plots.append(g for g in figs)
    return tf.Images(*chain.from_iterable(plots)).cols(cols)

def ds_plot(G, layout='circular', method='direct', bw=0.05, name='', kwargs=cvsopts):
    '''
    Returns graph plot using datashader layout
    fir nodes positions from circular (default),
    forceatlas2 or random position layout.

    Accepted vars:
        G => network graph obj
        layout => circular; forceatlas2; random
        method => connect; bundle
        bw => initial bandwith for bundled
        name => title or label
    '''
    n, e = nx_layout(G)
    nodes = ds_layout(n, e, layout)
    if method == 'bundle':
        edges = hammer_bundle(nodes, e, initial_bandwidth=bw)
    else: # lightweight
        edges = connect_edges(nodes, e)
    return graph_plot(nodes, edges, name, kwargs=kwargs)

def ds_layout(nodes, edges=[], layout='circular'):
    '''
    Return nodes positions based on set layout.]]]]]
    '''
    if layout == 'circular':
        return circular_layout(nodes)
    elif layout == 'forceatlas2':
        return forceatlas2_layout(nodes, edges)
    return random_layout(nodes)

def nodes_plot(nodes, name=None, canvas=None, cat=None, kwargs=cvsopts):
    '''
    Plot nodes using datashader Canvas functions and
    returns datashader.transfer_functions.spread().
    '''
    canvas = ds.Canvas(**kwargs) if canvas is None else canvas
    aggregator = None if cat is None else ds.count_cat(cat)
    agg = canvas.points(nodes,'x','y',aggregator)
    return tf.spread(tf.shade(agg, cmap=["#FF3333"]), px=3, name=name)

def edges_plot(edges, name=None, canvas=None, kwargs=cvsopts):
    '''
    Plot edges using datashader Canvas functions.
    returns datashader.transfer_functions.shade().
    '''
    canvas = ds.Canvas(**kwargs) if canvas is None else canvas
    return tf.shade(canvas.line(edges, 'x','y', agg=ds.count()), name=name)

def graph_plot(nodes, edges, name="", canvas=None, cat=None, kwargs=cvsopts):
    '''
    Plot graph using datashader Canvas functions.
    returns datashader.transfer_functions.stack().
    '''
    if canvas is None:
        xr = nodes.x.min(), nodes.x.max()
        yr = nodes.y.min(), nodes.y.max()
        canvas = ds.Canvas(**kwargs, x_range=xr, y_range=yr)
    np = nodes_plot(nodes, name + " nodes", canvas, cat)
    ep = edges_plot(edges, name + " edges", canvas)
    return tf.stack(ep, np, how="over", name=name)
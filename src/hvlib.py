#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
This module contains functions for plotting
graphic elements using the HoloViews library.

Tested with HoloViews version 1.12.1.
'''

import holoviews as hv
import holoviews.operation.datashader as hd

from holoviews.operation.datashader import datashade, dynspread

from nxlib import nx_layout

opts = dict(width=400, height=400,
            xaxis=None, yaxis=None,
            padding=0.1)

def hv_plot(G, layout='circular', method='bokeh', name='', kwargs=opts):
    '''
    Returns graph plot using HoloViews wrapper for bokeh.
    Optionally, draws edges using datashade functions.

    Accepted vars:
        G => networkx.Graph() object
        layout => circular; forceatlas2; random
        method => bokeh; datashader
        name => graph title or label
        kwargs => optionals
    '''
    hv.extension("bokeh")
    nodes, edges = nx_layout(G)
    # apply parameters
    if kwargs:
        hv.opts.defaults(
            hv.opts.EdgePaths(**kwargs),
            hv.opts.Graph(**kwargs),
            hv.opts.Nodes(**kwargs))
    # plot edges with bokeh
    circle = hv.Graph(edges, label=name).opts(style=dict(node_size=10))
    # plot edges with datashader (WIP)
    if method == 'datashader':
        hnodes = circle.nodes.opts(style=dict(size=10))
        dscirc = (hd.dynspread(hd.datashade(circle))*hnodes).relabel(name)
        return dscirc
    return circle
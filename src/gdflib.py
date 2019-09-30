#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Functions for handling Graph Data Format (GDF).
'''

import networkx as nx

from csv import reader, writer

NODES = ['nodedef>name VARCHAR']
EDGES = ['edgedef>node1 VARCHAR', 'node2 VARCHAR']

def export_gdf(filename, network=[], header_nodes=[], header_edges=[], directed=True):
    '''
    Export a list to a GDF graph format file.
    '''
    header_nodes = NODES + header_nodes
    header_edges = EDGES + header_edges
    header_edges.append('directed BOOLEAN')

    with open(filename, 'w', newline='', encoding='utf8') as graphfile:
        file_writer = writer(graphfile, delimiter=',')
        file_writer.writerow(header_nodes)
        file_writer.writerow(header_edges)

        for line in network:
            row = list(line)
            row.append(directed)
            file_writer.writerow(row)

def read_gdf(filename):
    '''
    Read GDF and returns graph object from networkx.
    '''
    G = nx.Graph()
    nodes, edges = False, False
    with open(filename, 'r', newline='', encoding='utf8') as graphfile:
        file_reader = reader(graphfile, delimiter=',')
        for line in file_reader:
            if line[0].startswith('nodedef>'):
                nodes, edges = True, False
            elif line[0].startswith('edgedef>'):
                nodes, edges = False, True
            elif nodes: # add to graph
                name = line[0]
                G.add_node(name)
            elif edges: # add to graph
                source = line[0]
                target = line[1]
                G.add_node(source)
                G.add_node(target)
                G.add_edge(source, target)
    return G

def read_gdf_groupedges(filename, by):
    '''
    Read GDF and returns graph objects from networkx
    with the edges grouped by the according value.
    '''
    G_dict = {}
    nodes, edges, pos = False, False, False
    with open(filename, 'r', newline='', encoding='utf8') as graphfile:
        file_reader = reader(graphfile, delimiter=',')
        for line in file_reader:
            if line[0].startswith('nodedef>'):
                nodes, edges = True, False
            elif line[0].startswith('edgedef>'):
                pos = line.index(by)
                nodes, edges = False, True
            elif nodes: # add to graph
                pass
            elif edges: # add to graph
                source = line[0]
                target = line[1]
                group = line[pos]
                group = group.split()[0]
                if group not in G_dict:
                    G_dict[group] = nx.Graph()
                G_dict[group].add_node(source)
                G_dict[group].add_node(target)
                G_dict[group].add_edge(source, target)
    return G_dict
import requests
import re
import sys
from SPARQLWrapper import SPARQLWrapper, JSON
import json
import mwapi
import os
import networkx as nx
import matplotlib.pyplot as plt


def color_for_input(nodes, center, input_num):
    colors_g1 = {}
    for node in nodes:
        if node == center:
            colors_g1[node] = 'red'
        else:
            if input_num == 1:
                colors_g1[node] = 'blue'
            else:
                colors_g1[node] = 'green'

    colors_list_g1 = []
    for node in nodes:
        colors_list_g1.append(colors_g1[node])

    return colors_list_g1

def assign_colors_to_combinedKG(list1, list2):
    # Create a dictionary to store the colors for each value
    colors = {}

    # Iterate through the first list and assign a unique color to each value
    for value in list1:
        if value not in colors:
            colors[value] = "blue"

    # Iterate through the second list and assign a unique color to each value
    for value in list2:
        if value not in colors:
            colors[value] = "green"
        else:
            colors[value] = "orange"

    return colors


def plot_knowledge_graph(G, pos, color_list, input_name):
    fig = plt.figure(1, figsize=(20,15), dpi=60)
    plt.title("KG for {}".format(input_name), size=20)

    if pos == None:
        nx.draw_networkx(G, with_labels=True, node_size=1000, node_color=color_list, arrowsize=50, alpha=0.9)
    else:
        nx.draw_networkx(G, pos, with_labels=True, node_size=1000, node_color=color_list, arrowsize=50, alpha=0.9)

    output_folder = 'output_folder/'
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # adding the name of the figure to the created output folder
    plt.savefig(output_folder + '{}.png'.format(input_name))
    #plt.savefig('output_figures/{}.png'.format(input_name))

import requests
import re
import sys
from SPARQLWrapper import SPARQLWrapper, JSON
import json
import mwapi
from sys import argv
from functions import *
from output_file_generator import *

class KG():
    def __init__(self, url1, url2, counter_limit):
        self.url1 = url1
        self.url2 = url2
        self.counter_limit = counter_limit
    
    def get_recommendation(self):
        print('Knowledge Graph generation starts')
        print(self.counter_limit)
        G1, Q1, pos1, all_unique_nodes1 = get_graph(self.url1, self.counter_limit)
        print('here')
        G2, Q2, pos2, all_unique_nodes2 = get_graph(self.url2, self.counter_limit)
        
        colors = assign_colors(all_unique_nodes1, all_unique_nodes2)
        
        F = merge_graph(G1,G2)
        shortest_path_text, shortest_path_qcode = get_shortest_path(F, Q1, Q2)

        output_descriptions = [get_description(node) for node in shortest_path_qcode]
        print('Here is your recommendations !\n')
        for ix, node in enumerate(shortest_path_text):
            print('{} : {}\n'.format(node, output_descriptions[ix]))
        
        return shortest_path_text, shortest_path_qcode, G1, pos1, G2, pos2, F, colors

if __name__ == "__main__":
    INPUT1, INPUT2, counter_limit = argv[1], argv[2], argv[3]
    model = KG(url1 = INPUT1, url2 = INPUT2, counter_limit = counter_limit)
    recommendations, recommendations_qcodes, G1, pos1, G2, pos2, combinedG, colors = model.get_recommendation()

    colors_list_g1 = color_for_input(list(G1.nodes), get_identifier_from_url(INPUT1), 1)
    colors_list_g2 = color_for_input(list(G2.nodes), get_identifier_from_url(INPUT2), 2)

    plot_knowledge_graph(G1, pos1, colors_list_g1, INPUT1.split('/')[-1])
    plot_knowledge_graph(G2, pos2, colors_list_g2, INPUT2.split('/')[-1])

    # For combined graph figures
    colors = assign_colors(G1.nodes, G2.nodes)
    combined_colors_list = []
    for node in list(combinedG.nodes):
        combined_colors_list.append(colors[node])
    plot_knowledge_graph(combinedG, None, combined_colors_list, str(INPUT1.split('/')[-1] + 'and' + INPUT2.split('/')[-1]))
import requests
import re
import sys
from SPARQLWrapper import SPARQLWrapper, JSON
import json
import mwapi
import networkx as nx


endpoint_url = "https://query.wikidata.org/sparql"

#-------------------- FUNCTIONS --------------------
import requests
import re
import sys
from SPARQLWrapper import SPARQLWrapper, JSON
import json
import math
import mwapi
import networkx as nx
import json
import os

endpoint_url = "https://query.wikidata.org/sparql"


# -------------------- FUNCTIONS --------------------
def get_identifier_from_url(url):
    '''
    Returns the Q identifier for given wikipedia link.

    Inputs:
        url (str): Wikipedia url

    Returns:
        qid (str): Q identifier string
    '''

    page_title = url.split("/")[-1]

    session = mwapi.Session("https://en.wikipedia.org")
    response = session.get(action="query", prop="pageprops", ppprop="wikibase_item", format="json", titles=page_title)
    pages = response["query"]["pages"]
    for page in pages.values():
        qid = page["pageprops"]["wikibase_item"]

    return qid


def get_results(endpoint_url, query):
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    # TODO adjust user agent; see https://w.wiki/CX6
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()


def get_instanceOf(identifier):
    '''
    Returns the instanceOf properties for given Q identifier.

    Inputs:
        identifier (str): Q identifier of input

    Returns:
        instanceof_list (list): Python list that contains the instanceOf properties
        instanceof_qcode_list (list): Python list that contains the Q identifier of instanceOf properties
    '''

    query = f"""
    SELECT ?instanceOf ?instanceOfLabel WHERE {{
        wd:{identifier} wdt:P31 ?instanceOf.
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}"""
    query_result = get_results(endpoint_url, query)
    results = query_result["results"]["bindings"]

    instanceof_list = []
    instanceof_qcode_list = []
    for result in results:
        result_identifier = re.findall("\/entity\/(.*)", result["instanceOf"]["value"])[0]
        result_value = result["instanceOfLabel"]["value"]

        if (result_value.find('order') == -1) and (result_value.find('concept') == -1) and (
                result_value.find('metaclass') == -1):
            instanceof_list.append(result_value)
            instanceof_qcode_list.append(result_identifier)

    return instanceof_list, instanceof_qcode_list


def get_subClassOf(identifier):
    '''
    Returns the subclassOf properties for given Q identifier.

    Inputs:
        identifier (str): Q identifier of input

    Returns:
        subclassOf_list (list): Python list that contains the subclassOf properties
        subclassOf_qcode_list (list): Python list that contains the Q identifier of subclassOf properties
    '''

    query = f"""
    SELECT ?subClassOf ?subClassOfLabel WHERE {{
        wd:{identifier} wdt:P279 ?subClassOf.
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}"""
    query_result = get_results(endpoint_url, query)
    results = query_result["results"]["bindings"]

    subclassOf_list = []
    subclassOf_qcode_list = []
    for result in results:
        result_identifier = re.findall("\/entity\/(.*)", result["subClassOf"]["value"])[0]
        result_value = result["subClassOfLabel"]["value"]

        if (result_value.find('order') == -1) and (result_value.find('concept') == -1) and (
                result_value.find('metaclass') == -1):
            subclassOf_list.append(result_value)
            subclassOf_qcode_list.append(result_identifier)

    return subclassOf_list, subclassOf_qcode_list


def get_imageURL(identifier):
    '''
    Returns the image url for given input if there exist in Wikidata as property

    Inputs:
        identifier (str): Q identifier of input

    Returns:
        image_url (str): Image url if exist in Wikidata, otherwise returns default url
    '''

    query = f"""
            SELECT ?imageLabel 
            WHERE {{
                wd:{identifier} wdt:P18 ?image.
              SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
            }}"""
    query_result = get_results(endpoint_url, query)
    results = query_result["results"]["bindings"]

    if len(results) == 0:
        # If there is not image property in Wikidata, return default url empty image url
        image_url = 'https://www.shutterstock.com/image-vector/empty-set-null-slashed-zero-600w-2106956618.jpg'
    else:
        # Otherwise, return image url from Wikidata
        image_url = results[0]["imageLabel"]["value"]
    return image_url


def get_itemLabel(identifier):
    '''
    Returns the wikidata label for given Q identifier

    Inputs:
        identifier (str): Q identifier of input

    Returns:
        label (str): Wikidata label of Q identifier
    '''

    query = f"""
            SELECT ?itemLabel
            WHERE
            {{
              wd:{identifier} rdfs:label ?itemLabel
              FILTER (LANG(?itemLabel) = "en")
            }}"""
    query_result = get_results(endpoint_url, query)
    results = query_result["results"]["bindings"]

    if len(results) == 0:
        item_label = 'No Label'
    else:
        item_label = results[0]['itemLabel']['value']
    return item_label


def get_description(identifier):
    '''
    Returns the Wikidata description of input

    Inputs:
        identifier (str): Q identifier of input

    Returns:
        description (str): Description text in Wikidata
    '''

    query = f"""
    PREFIX bd: <http://www.bigdata.com/rdf#> 
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
    PREFIX schema: <http://schema.org/> 
    PREFIX wd: <http://www.wikidata.org/entity/> 
    PREFIX wikibase: <http://wikiba.se/ontology#> 

    SELECT ?description
    WHERE {{
      SERVICE wikibase:label {{
        bd:serviceParam wikibase:language "en" .
        wd:{identifier} schema:description ?description .}}
    }}
      """
    query_result = get_results(endpoint_url, query)
    results = query_result["results"]["bindings"]

    if (len(results) == 0) or (results[0] == {}):
        description = 'No description'
    else:
        description = results[0]['description']['value']

    return description


def get_unique(inputList):
    '''
    Eliminate the duplicate element from the list and return list that contains unique element

    Inputs:
        inputList (list): Input list

    Returns:
        unique_set (list): List containing unique elements
    '''

    unique_set = set()
    unique_set = [x for x in inputList if x not in unique_set and (unique_set.add(x) or True)]

    return unique_set


def update_edge_list(adjacency_matrix, edgelist, dictionary_map, relation_type):
    '''
    Returns adjacency list and edge list for visualization of graphs

    Inputs:
        dictionary_map (dict): Dictionary that contains node and corresponding property values
        relation_type (str): Relation type between two nodes. (instance_of or subclass_of)

    Returns:
        adjacency_matrix (list): List containing each unique node pairs
        edgelist (dict): Dictionary whose key is two nodes with interaction and
                            their values are a list showing the relationship between two nodes
                            Ex: 'node1-node2':[node1, node2, relation_type]
    '''

    for key, value in dictionary_map.items():
        for val in value:
            if key != val:
                dict_id = key + '-' + val
                edge = []
                edge.append(key)
                edge.append(val)
                edge.append(relation_type)

                edgelist[dict_id] = edge
                adjacency_matrix.append(tuple([key, val]))
            else:
                pass

    return adjacency_matrix, edgelist


def draw_graph(adjacency_list, number_of_nodes):
    '''
    Returns adjacency list and edge list for visualization of graphs

    Inputs:
        adjacency_list (list): List containing each unique pair of nodes in graphs
        number_of_nodes (str): The number of unique node

    Returns:
        G (networkx.classes.graph.Graph): Networkx Graph object containing the nodes and edges
        pos (dict): Dictionary that contains the position of nodes
    '''

    G = nx.Graph()
    G.add_edges_from(adjacency_list)
    pos = nx.spring_layout(G, k=2 / math.sqrt(number_of_nodes))

    nx.draw_networkx(G, pos)
    return G, pos


def print_shortest_path(shortest_path):
    '''
    Function that print the shortest path in given list of nodes

    Inputs:
        shortest_path (list): list of ordered nodes that make up the shortest path

    Returns:
        path_str (str): String that shows the shortest path
    '''

    path_str = ''
    length_of_shortest_path = len(shortest_path)

    for k in range(length_of_shortest_path):
        path_str = path_str + shortest_path[k]

        if k != length_of_shortest_path - 1:
            path_str += ' -> '
        else:
            break

    return path_str


def get_other_properties(unique_node_list, input_text, q_code):
    '''
    Returns the required properties for each nodes in graphs

    Inputs:
        unique_node_list (list): List of unique nodes in graph
        input_text (str): The label name of given input (center of graph)
        q_code (str): The Q identifier of given input (center of graph)

    Returns:
        input_to_imageurl (dict): Dictionary whose keys are Q identifier and values are image url
        input_to_description (dict): Dictionary whose keys are Q identifier and values are description of input
        qcode_to_input (dict): Dictionary whose keys are Q identifier and values are corresponding wikidata label
    '''

    input_to_imageurl = {}
    input_to_description = {}
    qcode_to_input = {}

    qcode_to_input[q_code] = input_text

    for node in unique_node_list:
        input_to_imageurl[node] = get_imageURL(node)
        input_to_description[node] = get_description(node)
        qcode_to_input[node] = get_itemLabel(node)

    return input_to_imageurl, input_to_description, qcode_to_input


def metrics_json_maker(G, pos, input_to_imageurl, input_to_description, qcode_to_input):
    '''
    Returns json for metrics.json file which contains the various metrics for each node

    Inputs:
        G (networkx.Graph): Networkx.Graph object
        pos (dict): Dictionary whose keys are node (Q identifier) and values are the position in networkx.Graph object
        input_to_imageurl (dict): Dictionary whose keys are Q identifier and values are image url
        input_to_description (dict): Dictionary whose keys are Q identifier and values are description of input
        qcode_to_input (dict): Dictionary whose keys are Q identifier and values are corresponding wikidata label

    Returns:
        metrics_json_dict (dict): Dictionary whose keys are Q identifier and values are metrics
    '''

    metrics_json_dict = {}
    for key, values in pos.items():
        info = {"qCode": key,
                'name': qcode_to_input[key],
                'img': input_to_imageurl[key],
                'description': input_to_description[key]}

        try:
            dijkstra_path = [qcode_to_input[x] for x in nx.shortest_path(G, q_code, key)]
        except:
            dijkstra_path = ['No Path']

        try:
            eccentricity_score = nx.eccentricity(G, key)
        except:
            eccentricity_score = 'Found infinite path length because the graph is not connected'

        metrics = {'dijkstra': print_shortest_path(dijkstra_path),
                   'eccentricity': eccentricity_score}
        items = {"x": values[0], 'y': values[1]}

        items['info'] = info
        items['metrics'] = metrics

        metrics_json_dict[key] = items

    return metrics_json_dict


def assign_colors(list1, list2):
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


def save_results(metrics_dict, edge_list, all_unique_nodes, q_code, input_text):
    '''
    Functions that saves the results in the input format that the frontend needs

    Inputs:
        metrics_dict (dict): Dictionary that constains metric values. It is the output of metrics_json_maker function
        edge_list (dict): Dict that contains the node pairs and corresponding relation. It is one of the output of update_edge_list function
        all_unique_nodes (list): List that contains the unique nodes. It comes from get_unique function
        q_code (dict): Q identifier of initial search input
        input_text (str): The label of the given Wikipedia url (as known as the name of page)

    Returns:
        Necessary json files in current directory
    '''

    # Open folder for each search
    os.makedirs(f'SSW_Project/{input_text}', exist_ok=True)

    with open(f'SSW_Project/{input_text}/nodes.json', 'w') as nodesJson:
        variable_str = str('const nodesJSON = ')
        nodesJson.write(variable_str)
        json.dump(metrics_dict, nodesJson)
        nodesJson.close()

    with open(f'SSW_Project/{input_text}/edge_list.json', 'w') as edgesJson:
        variable_str = str('const edgesJSON = ')
        edgesJson.write(variable_str)
        json.dump(edge_list, edgesJson)
        edgesJson.close()

    with open(f'SSW_Project/{input_text}/metrics.json', 'w') as countnodesJson:
        metrics = {}
        metrics['nodeCount'] = len(all_unique_nodes)
        metrics['initialNode'] = q_code

        variable_str = str('const metricsJSON = ')
        countnodesJson.write(variable_str)
        json.dump(metrics, countnodesJson)
        countnodesJson.close()


def get_graph(url, counter_limit):
    input_to_instanceOf_QCode, input_to_subclassOf_QCode, all_unique_nodes, q_code = run_system(url, counter_limit)

    edgelist = {}
    adjacency_matrix = []

    adjacency_matrix, edge_list = update_edge_list(adjacency_matrix, edgelist, input_to_subclassOf_QCode, 'subclass_of')
    adjacency_matrix, edge_list = update_edge_list(adjacency_matrix, edgelist, input_to_instanceOf_QCode, 'instance_of')

    # Calculates the total number of unique nodes in the graph
    all_unique_nodes = get_unique(all_unique_nodes)

    # Draw the graph and get the graph object and position of nodes
    G, pos = draw_graph(adjacency_matrix, len(all_unique_nodes))

    return G, q_code, pos, all_unique_nodes


def merge_graph(G1, G2):
    return nx.compose(G1, G2)


def get_shortest_path(G, q_identifier_1, q_identifier_2):
    path = nx.shortest_path(G, q_identifier_1, q_identifier_2)  # George Floyd - United States
    text_path = [get_itemLabel(x) for x in path]

    return text_path, path


def run_system(url, counter_limit):
    # The input wikipedia url link is given here
    INPUT_URL = url  # Wikipedia link
    COUNTER_LIMIT = int(counter_limit)  # How many loops does algorithm takes

    # We obtain the initial label and corresponding Q identifier
    input_text = INPUT_URL.split('/')[-1]
    q_code = get_identifier_from_url(INPUT_URL)

    # Define variables
    input_to_instanceOf = {}
    input_to_subclassOf = {}
    input_to_instanceOf_QCode = {}
    input_to_subclassOf_QCode = {}
    all_possible_identifiers = []
    all_possible_identifiers_qcode = []
    all_unique_nodes = []
    edgelist = {}
    adjacency_matrix = []

    # Add first element (which is given input) into our variables
    all_possible_identifiers.append(input_text)
    all_possible_identifiers_qcode.append(q_code)
    all_unique_nodes.append(q_code)

    counter = 0
    while len(all_possible_identifiers_qcode) != 0:
        # print(all_possible_identifiers[0])

        current_Qcode = all_possible_identifiers_qcode[0]

        # instanceOf
        output_identifiers, outputIdentifiers_qcode = get_instanceOf(current_Qcode)
        # print(output_identifiers,outputIdentifiers_qcode)

        if len(output_identifiers) != 0:  # If there is an instaceOf properties returned
            all_possible_identifiers.extend(output_identifiers)
            all_possible_identifiers_qcode.extend(outputIdentifiers_qcode)
            all_unique_nodes.extend(outputIdentifiers_qcode)

            all_possible_identifiers = get_unique(all_possible_identifiers)
            all_possible_identifiers_qcode = get_unique(all_possible_identifiers_qcode)

            input_to_instanceOf[all_possible_identifiers[0]] = output_identifiers
            input_to_instanceOf_QCode[current_Qcode] = outputIdentifiers_qcode

        output_identifiers, outputIdentifiers_qcode = get_subClassOf(current_Qcode)
        if len(output_identifiers) != 0:
            all_possible_identifiers.extend(output_identifiers)
            all_possible_identifiers_qcode.extend(outputIdentifiers_qcode)
            all_unique_nodes.extend(outputIdentifiers_qcode)

            all_possible_identifiers = get_unique(all_possible_identifiers)
            all_possible_identifiers_qcode = get_unique(all_possible_identifiers_qcode)

            input_to_subclassOf[all_possible_identifiers[0]] = output_identifiers
            input_to_subclassOf_QCode[current_Qcode] = outputIdentifiers_qcode

        all_possible_identifiers.pop(0)
        all_possible_identifiers_qcode.pop(0)
        # print(all_possible_identifiers)

        counter = counter + 1
        # If counter exceeds the desired limit, then elements are deleted from q code list to stop while loop
        if counter == COUNTER_LIMIT:
            all_possible_identifiers_qcode = []

    return input_to_instanceOf_QCode, input_to_subclassOf_QCode, all_unique_nodes, q_code



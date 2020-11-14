from time import sleep
import json
from py2neo import Graph, Node, Relationship, NodeMatcher
from dotenv import load_dotenv
from os import environ

load_dotenv()
graph_url = environ.get("NEO4J_HOST")
graph_login = environ.get("NEO4J_LOGIN")
graph_pass = environ.get("NEO4J_PASSWORD")

while True:
    try:
        g = Graph(graph_url, name=graph_login, password=graph_pass)
        break
    except ConnectionRefusedError:
        sleep(1)

"""
Parameters:

    json:  Json with triplets
    
    json = {
        "triplets":[{
        "node1":{
            "name":"name1",
            "label":"node_label",
            ... # another params
        },
        "node2":{
            "name":"name1",
            "label":"node_label",
            ... # another params
        },
        "relation":{
        "name":"rel_type"
        }
        },...],
    }
"""


def add_triplets_to_db(json):
    tx = g.begin()
    for triplet in json["triplets"]:
        a = Node(triplet["node1"]['label'], **triplet["node1"])
        b = Node(triplet["node2"]['label'], **triplet["node2"])
        rel = Relationship.type(triplet["relation"]["name"])
        g.merge(rel(a, b), a.get("label"), "name")
    tx.commit()


"""
Parameters:

    node:  json or dict with  node info
    node = {
    "name":"name",
    ...
    }
RETURNS:
    result: json triplets
"""


def get_query_item(node):
    result = {
        "triplets": []
    }
    node_matcher = NodeMatcher(g)
    node = node_matcher.match(**node).first()
    items = g.run("MATCH (n{name:$name})-[r]-() RETURN r", name=node["name"])
    items_data = items.data()
    for item in items_data:
        data = item["r"]
        node1, node2 = data.nodes
        data["name"] = type(data).__name__
        rel = dict(data)
        result["triplets"].append({"node1": dict(node1), "node2": dict(node2), "relation": rel})
    return result


"""
Parameters:

    node1:  json or dict with 2 node info
    nodes = {
        "node1":{
            "name":"name",
        ...
        },
        "node2":{
            "name":"name",
        ...
        },
        "label_1":"LABEL", #(optional)
        "label_2":"LABEL"  #(optional)
    }
RETURNS:
    result: json triplets
"""


def shortest_way_label(nodes, label_1=None, label_2=None):
    query = "MATCH (a {name: $name_a}), (b {name: $name_b}), path = shortestpath((a)-[*]-(b))"
    result = {
        "triplets": []
    }

    if label_1 and label_2 is not None:
        query += "WHERE "
        if label_1 is not None:
            query += "$Label_1 IN LABELS(a) "
            if label_2 is not None:
                query += " AND "
        if label_2 is not None:
            query += "$Label_2 IN LABELS(b)"

    query += ' RETURN path'

    try:
        items = g.run(
            query,
            name_a=nodes['node1']['name'], name_b=nodes['node2']['name'],
            Label_1=label_1, Label_2=label_2
        )
    except TypeError:
        return None
    items_data = items.data()
    if not items_data:
        return result

    for triplet in items_data[0]['path']:
        node1, node2 = triplet.nodes
        rel = list(triplet.types())[0]
        result["triplets"].append({"node1": dict(node1), "node2": dict(node2), "relation": {"name": rel}})
    return result

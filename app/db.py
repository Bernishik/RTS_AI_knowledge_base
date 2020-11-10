from time import sleep

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
    }
    }
RETURNS:
    result: json triplets
"""


def shortest_way(nodes):
    result = {
        "triplets": []
    }
    node_matcher = NodeMatcher(g)
    node1 = node_matcher.match(**nodes["node1"]).first()
    node2 = node_matcher.match(**nodes["node2"]).first()
    try:
        items = g.run("MATCH path = shortestpath((a)-[*]->(b)) WHERE a.name=$node1 AND b.name=$node2 RETURN path",
                      node1=node1["name"], node2=node2["name"])
    except TypeError:
        return None
    items_data = items.data()
    for triplet in items_data[0]['path']:
        node1, node2 = triplet.nodes
        rel = list(triplet.types())[0]
        result["triplets"].append({"node1": dict(node1), "node2": dict(node2), "relation": {"name": rel}})
    return result
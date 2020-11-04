from py2neo import Graph, Node, Relationship, NodeMatcher
from dotenv import load_dotenv
from os import environ

load_dotenv()
graph_url = environ.get("NEO4J_HOST")
graph_login = environ.get("NEO4J_LOGIN")
graph_pass = environ.get("NEO4J_PASSWORD")

g = Graph(graph_url,name=graph_login,password=graph_pass)

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
        g.merge(rel(a, b), "node_lab", "name")
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

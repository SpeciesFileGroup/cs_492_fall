from extract_data import extract_data
import matplotlib.pyplot as plt
import networkx as nx
from networkx.readwrite import json_graph
import difflib, json

def generate_graph():
	X, y = extract_data()
	G = nx.Graph()

	X, y = X[:200], y[:200]
	for i in range(len(X)):
		G.add_node(i, journal = X[i], num_pages = y[i])

	for node1 in G.nodes(data=True):
		for node2 in G.nodes(data=True):
			if difflib.SequenceMatcher(None, node1[1]['journal'], node2[1]['journal']).ratio() > 0.8 and node1 != node2:
				G.add_edge(node1[0], node2[0])

	graph_data = json_graph.node_link_data(G)
	with open('graph.json', 'w') as f:
		json.dump(graph_data, f, indent=4)

if __name__ == '__main__':
	generate_graph()
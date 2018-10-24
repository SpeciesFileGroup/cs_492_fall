from extract_data import extract_data
import matplotlib.pyplot as plt
import networkx as nx
import difflib

def visualize():
	X, y = extract_data()
	G = nx.Graph()

	for i in range(len(X)):
		G.add_node(X[i], num_pages = y[i])

	for node1 in G.nodes():
		for node2 in G.nodes():
			if difflib.SequenceMatcher(None, node1, node2).ratio() > 0.8:
				G.add_edge(node1, node2)

	print(list(nx.connected_components(G)))
	node_labels = {node: node for node in G.nodes()}

	pos = nx.spring_layout(G)
	nx.draw_networkx_nodes(G, pos, cmap = plt.get_cmap('jet'), node_size = 100)
	nx.draw_networkx_edges(G, pos, edgelist = G.edges(), edge_color = 'black')
	plt.show()

if __name__ == '__main__':
	visualize()
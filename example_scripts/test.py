from RePoE import mods


class Node():
    def __init__(self, content):
        self.content = content
        self.outward_edge_neighbors = set()
    
    def add_outward_edge_neightbor(self, node):
        self.outward_edge_neighbors.add(node)


#checking if dag?
seen_tags = {}

for mod in mods.values():
    nodes = []
    for spawn_weight in mod["spawn_weights"]:
        tag = spawn_weight["tag"]
        if spawn_weight["tag"] not in seen_tags:
            seen_tags[tag] = Node(tag)
        
        for before_node in nodes:
            before_node.add_outward_edge_neightbor(seen_tags[tag])
        nodes.append(seen_tags[tag])

import networkx as nx 

G = nx.DiGraph() 

edges = []
for node_name, node_value in seen_tags.items():
    src_node = node_name
    G.add_node(src_node) 
    for target_node in node_value.outward_edge_neighbors:
        edges.append((src_node, target_node.content))
 
G.add_edges_from(edges)
nx.draw_networkx(G, with_label = True) 


for component in nx.algorithms.components.weakly_connected_components(G):
    print(component)
# import matplotlib.pyplot as plt
# plt.show()

import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import time
import numpy as np

# Import the custom edge and edge label drawing functions
import my_networkx as my_nx



file_path = 'data/task_graph/multiple_demos/task_graph.txt'
delay = 2

def parse_graph(file_path):
    graph = nx.DiGraph()
    with open(file_path, 'r') as file:
        current_node = None
        neighbors = []
        weights = []

        for line in file:
            if 'name:' in line:
                if current_node and neighbors:
                    for neighbor, weight in zip(neighbors, weights):
                        graph.add_edge(current_node, neighbor, weight=weight)
                current_node = line.split(':')[1].strip()
                neighbors = []
                weights = []
            elif 'neighbors[' in line and current_node:
                if ':' in line:
                    neighbor = line.split(':')[1].strip()
                    neighbors.append(neighbor)
            elif 'weights[' in line and current_node:
                if ':' in line:
                    weight = int(line.split(':')[1].strip())
                    weights.append(weight)

        if current_node and neighbors:
            for neighbor, weight in zip(neighbors, weights):
                graph.add_edge(current_node, neighbor, weight=weight)

    return graph


def build_graph_dynamically(graph, delay):
    dynamic_graph = nx.DiGraph()
    for node in graph.nodes:
        if node not in dynamic_graph:
            dynamic_graph.add_node(node)
            draw_graph(dynamic_graph, highlight=[node], update=True)
            time.sleep(delay)

        for neighbor in graph.neighbors(node):
            if neighbor not in dynamic_graph:
                dynamic_graph.add_edge(
                    node, neighbor, weight=graph[node][neighbor]['weight'])
                dynamic_graph.add_node(neighbor)
                draw_graph(dynamic_graph, highlight=[
                           (node, neighbor), neighbor], update=True)
                time.sleep(delay)
            elif (node, neighbor) not in dynamic_graph.edges:
                dynamic_graph.add_edge(
                    node, neighbor, weight=graph[node][neighbor]['weight'])
                draw_graph(dynamic_graph, highlight=[
                           (node, neighbor), neighbor], update=True)
                time.sleep(delay)
    draw_graph(dynamic_graph, update=True)
    messagebox.showinfo("Info", "Graph construction complete.")


def draw_graph(graph, highlight=None, update=False):
    ax.clear()
    node_size = 600
    nx.draw_networkx_nodes(graph, pos, node_size=node_size, node_color='skyblue', ax=ax)
    nx.draw_networkx_labels(graph, pos, ax=ax)

    edge_weights = nx.get_edge_attributes(graph, 'weight')
    curved_edges = [edge for edge in graph.edges() if reversed(edge) in graph.edges() and edge in edge_weights]
    straight_edges = list(set(graph.edges()) - set(curved_edges))

    nx.draw_networkx_edges(graph, pos, ax=ax, edgelist=straight_edges, edge_color='gray', width=2, arrowstyle='-|>', arrowsize=15)
    arc_rad = 0.1
    nx.draw_networkx_edges(graph, pos, ax=ax, edgelist=curved_edges, connectionstyle=f'arc3, rad = {arc_rad}', edge_color='gray', width=2, arrowstyle='-|>', arrowsize=15)

    if highlight:
        for item in highlight:
            if isinstance(item, tuple):
                if item in curved_edges or (item[1], item[0]) in curved_edges:
                    nx.draw_networkx_edges(graph, pos, edgelist=[item], edge_color='red', width=3,
                                           arrowstyle='-|>', arrowsize=20, ax=ax, connectionstyle=f'arc3, rad = {arc_rad}')
                else:
                    nx.draw_networkx_edges(graph, pos, edgelist=[item], edge_color='red', width=3,
                                           arrowstyle='-|>', arrowsize=20, ax=ax)
            else:  # This is a node
                nx.draw_networkx_nodes(graph, pos, nodelist=[item], node_size=node_size, node_color='green', ax=ax)

    curved_edge_labels = {edge: edge_weights.get(edge) for edge in curved_edges}
    straight_edge_labels = {edge: edge_weights.get(edge) for edge in straight_edges}
    my_nx.my_draw_networkx_edge_labels(graph, pos, ax=ax, edge_labels=curved_edge_labels, font_size=12, rotate=False, rad=arc_rad)
    nx.draw_networkx_edge_labels(graph, pos, ax=ax, edge_labels=straight_edge_labels, font_size=12, rotate=False)

    if start_node is not None:
        nx.draw_networkx_nodes(graph, pos, nodelist=[start_node], node_size=node_size, node_color='red', ax=ax)
    if end_node is not None:
        nx.draw_networkx_nodes(graph, pos, nodelist=[end_node], node_size=node_size, node_color='blue', ax=ax)

    canvas.draw()
    if update:
        root.update()


def on_click(event):
    global start_node, end_node
    if event.xdata is None or event.ydata is None:
        return
    for node, node_pos in pos.items():
        distance = (
            (event.xdata - node_pos[0]) ** 2 + (event.ydata - node_pos[1]) ** 2) ** 0.5
        if distance < 0.1:
            if start_node is None:
                start_node = node
                messagebox.showinfo("Info", f"Start node set to {node}")
            elif end_node is None and node != start_node:
                end_node = node
                messagebox.showinfo("Info", f"End node set to {node}")
            else:
                return
            draw_graph(G)
            return
    messagebox.showinfo("Info", "No node was clicked.")


root = tk.Tk()
root.wm_title("Visualization")
fig, ax = plt.subplots(figsize=(10, 7))
canvas = FigureCanvasTkAgg(fig, master=root)
G = parse_graph(file_path)
pos = nx.spring_layout(G)

start_node = None
end_node = None

canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
canvas.mpl_connect("button_press_event", on_click)

root.after(1000, lambda: build_graph_dynamically(G, delay))
tk.mainloop()


def nx_to_matrix(graph):
    # Function to convert a NetworkX graph to an adjacency matrix
    nodes = list(graph.nodes())
    num_nodes = len(nodes)
    node_to_index = {node: index for index, node in enumerate(nodes)}

    matrix = np.zeros((num_nodes, num_nodes))

    for edge in graph.edges(data=True):
        source, target, data = edge
        source_index = node_to_index[source]
        target_index = node_to_index[target]
        matrix[source_index][target_index] = data['weight']

    return matrix


print(nx_to_matrix(G))

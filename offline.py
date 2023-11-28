import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import time
import numpy as np

file_path = 'data/task_graph/multiple_demos/task_graph.txt'
delay = 1

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
                           (node, neighbor)], update=True)
                time.sleep(delay)
            elif (node, neighbor) not in dynamic_graph.edges:
                dynamic_graph.add_edge(
                    node, neighbor, weight=graph[node][neighbor]['weight'])
                draw_graph(dynamic_graph, highlight=[
                           (node, neighbor)], update=True)
                time.sleep(delay)
    draw_graph(dynamic_graph, update=True)
    messagebox.showinfo("Info", "Graph construction complete.")


def draw_graph(graph, highlight=None, update=False):
    ax.clear()
    node_size = 600
    nx.draw_networkx_nodes(graph, pos, node_size=node_size, node_color='skyblue', ax=ax)
    nx.draw_networkx_labels(graph, pos, ax=ax)

    edge_weights = nx.get_edge_attributes(graph, 'weight')

    for edge in graph.edges():
        if graph.has_edge(edge[1], edge[0]):
            connectionstyle = 'arc3,rad=0.1'
        else:
            connectionstyle = 'arc3,rad=0'

        nx.draw_networkx_edges(graph, pos, edgelist=[edge], connectionstyle=connectionstyle,
                               edge_color='gray', width=2, arrowstyle='-|>', arrowsize=15, ax=ax)
        lable_position = get_curved_edge_midpoint(pos, edge, connectionstyle=connectionstyle, rad=0.1)
        edge_label = edge_weights[edge]
        ax.text(lable_position[0], lable_position[1], edge_label, style='italic', fontsize=8, bbox={
                'facecolor': 'white', 'edgecolor': 'black', 'boxstyle': 'circle', 'pad': 0.5}, zorder=3)

    if highlight:
        if isinstance(highlight[0], tuple):
            nx.draw_networkx_edges(graph, pos, edgelist=highlight, connectionstyle=connectionstyle, edge_color='red', width=2,
                                   arrowstyle='-|>', arrowsize=20, ax=ax)
            target_nodes = [edge[1] for edge in highlight]
            nx.draw_networkx_nodes(
                graph, pos, nodelist=target_nodes, node_size=node_size, node_color='green', ax=ax)
        else:
            nx.draw_networkx_nodes(
                graph, pos, nodelist=highlight, node_size=node_size, node_color='green', ax=ax)

    if start_node is not None:
        nx.draw_networkx_nodes(graph, pos, nodelist=[
                               start_node], node_size=node_size, node_color='red', ax=ax)
    if end_node is not None:
        nx.draw_networkx_nodes(graph, pos, nodelist=[
                               end_node], node_size=node_size, node_color='blue', ax=ax)
    canvas.draw()
    if update:
        root.update()


def get_curved_edge_midpoint(pos, edge, connectionstyle, rad=0.1):
    src_pos = np.array(pos[edge[0]])
    dst_pos = np.array(pos[edge[1]])

    mid_point = (src_pos + dst_pos) / 2

    edge_vec = dst_pos - src_pos
    perp_vec = np.array([-edge_vec[1], edge_vec[0]])
    perp_vec = perp_vec / np.linalg.norm(perp_vec)

    edge_length = np.linalg.norm(edge_vec)
    adjusted_rad = rad * edge_length * 0.5

    if connectionstyle == 'arc3,rad=0.1':
        mid_point += perp_vec * adjusted_rad

    return mid_point


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


import numpy as np
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import random
import my_networkx as my_nx


def parse_graph(file_path):
    # Function to parse a graph from file and return a NetworkX graph object
    graph = nx.DiGraph()
    current_node, neighbors, weights = None, [], []

    with open(file_path, 'r') as file:
        for line in file:
            if 'name:' in line:
                if current_node and neighbors:
                    graph.add_edges_from((current_node, neighbor, {'weight': weight}) for neighbor, weight in zip(neighbors, weights))
                current_node, neighbors, weights = line.split(':')[1].strip(), [], []
                graph.add_node(str(current_node), name=str(current_node))
            elif 'neighbors[' in line and current_node:
                if ':' in line:
                    neighbors.append(line.split(':')[1].strip())
            elif 'weights[' in line and current_node:
                if ':' in line:
                    weights.append(int(line.split(':')[1].strip()))

        if current_node and neighbors:
            graph.add_edges_from((current_node, neighbor, {'weight': weight}) for neighbor, weight in zip(neighbors, weights))
            graph.add_node(str(current_node), name=str(current_node))

    return graph


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

def draw_graph(ax, pos, start_node, end_node, widest_path=None):
    # Function to draw the graph using Matplotlib
    ax.clear()
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_size=300, node_color='skyblue', ax=ax)
    labels = nx.get_node_attributes(G, 'name')
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=10, font_color='black', ax=ax)

    # Draw start and end nodes
    if start_node is not None:
        nx.draw_networkx_nodes(G, pos, nodelist=[start_node], node_size=800, node_color='red', ax=ax)
    if end_node is not None:
        nx.draw_networkx_nodes(G, pos, nodelist=[end_node], node_size=800, node_color='blue', ax=ax)

    # Draw edges with labels and arrows
    curved_edges = [edge for edge in G.edges() if reversed(edge) in G.edges()]
    straight_edges = list(set(G.edges()) - set(curved_edges))
    nx.draw_networkx_edges(G, pos, ax=ax, edgelist=straight_edges, arrows=True)
    arc_rad = 0.25
    nx.draw_networkx_edges(G, pos, ax=ax, edgelist=curved_edges, connectionstyle=f'arc3, rad = {arc_rad}', arrows=True)

    # Create edge_weights considering both directions of edges
    edge_weights = nx.get_edge_attributes(G, 'weight')
    edge_weights.update({(edge[1], edge[0]): weight for edge, weight in edge_weights.items()})
    curved_edge_labels = {edge: edge_weights[edge] for edge in curved_edges}
    straight_edge_labels = {edge: edge_weights[edge] for edge in straight_edges}
    my_nx.my_draw_networkx_edge_labels(G, pos, ax=ax, edge_labels=curved_edge_labels, rotate=False, rad=arc_rad)
    nx.draw_networkx_edge_labels(G, pos, ax=ax, edge_labels=straight_edge_labels, rotate=False)

    canvas.draw()
    
def draw_path(G, path, ax, pos):
    # Draw the widest path on the existing graph
    edges = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
    nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color='orange', width=3, ax=ax)


def on_click(event, pos, ax):
    # Function to handle mouse clicks on the graph
    global start_node, end_node
    if event.xdata is None or event.ydata is None:
        return

    clicked_node = next((node for node, node_pos in pos.items() if ((event.xdata - node_pos[0]) ** 2 + (event.ydata - node_pos[1]) ** 2) ** 0.5 < 0.1), None)

    if clicked_node:
        if start_node is None:
            start_node = clicked_node
            messagebox.showinfo("Info", f"Start node set to {start_node}")
            draw_graph(ax, pos, start_node, end_node)
        elif end_node is None and clicked_node != start_node:
            end_node = clicked_node
            messagebox.showinfo("Info", f"End node set to {end_node}")
            draw_graph(ax, pos, start_node, end_node)

        if start_node and end_node:
            # Run widest path search
            widest_path, widest_min_width = monte_carlo_widest_path(G, start_node, end_node)
            if widest_path:
                draw_path(G, widest_path, ax, pos)
                canvas.draw()
                print("Widest Path:", widest_path, "with widest minimum width:", widest_min_width)


def monte_carlo_widest_path(graph, start_node, end_node, iterations=3000, randomness_factor=0.2):
    # Find the widest path using Monte Carlo simulation
    best_path = None
    best_min_width = -np.inf

    for _ in range(iterations):
        path = [start_node]
        current_node = start_node
        min_width = np.inf

        while current_node != end_node:
            # Retrieve the weights from the edge attributes
            next_nodes = [n for n, d in graph[current_node].items() if 'weight' in d]
            if len(next_nodes) == 0:
                break

            if random.random() < randomness_factor:
                chosen_node = random.choice(next_nodes)
            else:
                widths = [graph[current_node][n]['weight'] for n in next_nodes]
                max_width_index = np.argmax(widths)
                chosen_node = next_nodes[max_width_index]

            if chosen_node in path:
                break

            # Update the minimum width of the current path
            min_width = min(min_width, graph[current_node][chosen_node]['weight'])
            current_node = chosen_node
            path.append(current_node)

        if current_node == end_node and min_width > best_min_width:
            best_path = path
            best_min_width = min_width

    return best_path, best_min_width


file_path = 'log_2023-11-21_101155/task_graph2.txt'
G = parse_graph(file_path)

root = tk.Tk()
root.wm_title("Visualization")

fig, ax = plt.subplots(figsize=(10, 7))
canvas = FigureCanvasTkAgg(fig, master=root)

# Circular layout of the graph
pos = nx.circular_layout(G)

# Draw the initial graph
start_node, end_node = None, None
draw_graph(ax, pos, start_node, end_node)

# Set up the canvas
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Connect the click event to the on_click function
canvas.mpl_connect("button_press_event", lambda event: on_click(event, pos, ax))

# Run the Tkinter main loop
tk.mainloop()




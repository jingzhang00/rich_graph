import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import time

file_path = 'log_2023-11-21_101155/task_graph.txt'
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
                dynamic_graph.add_edge(node, neighbor, weight=graph[node][neighbor]['weight'])
                draw_graph(dynamic_graph, highlight=[(node, neighbor)], update=True)
                time.sleep(delay)
                dynamic_graph.add_node(neighbor)
                draw_graph(dynamic_graph, highlight=[neighbor], update=True)
                time.sleep(delay)
            elif (node, neighbor) not in dynamic_graph.edges:
                dynamic_graph.add_edge(node, neighbor, weight=graph[node][neighbor]['weight'])
                draw_graph(dynamic_graph, highlight=[(node, neighbor)], update=True)
                time.sleep(delay)

    messagebox.showinfo("Notification", "Graph construction complete.")


def draw_graph(graph, highlight=None, update=False):
    ax.clear()
    nx.draw(graph, pos, with_labels=True, node_size=2000, node_color='skyblue', edge_color='gray', ax=ax)
    if highlight:
        if isinstance(highlight[0], tuple):
            nx.draw_networkx_edges(graph, pos, edgelist=highlight, edge_color='red', width=2, ax=ax)
        else:
            nx.draw_networkx_nodes(graph, pos, nodelist=highlight, node_size=2500, node_color='green', ax=ax)
    if start_node is not None:
        nx.draw_networkx_nodes(graph, pos, nodelist=[start_node], node_size=2500, node_color='red', ax=ax)
    if end_node is not None:
        nx.draw_networkx_nodes(graph, pos, nodelist=[end_node], node_size=2500, node_color='blue', ax=ax)
    canvas.draw()
    if update:
        root.update()


def on_click(event):
    global start_node, end_node
    if event.xdata is None or event.ydata is None:
        return
    for node, node_pos in pos.items():
        distance = ((event.xdata - node_pos[0]) ** 2 + (event.ydata - node_pos[1]) ** 2) ** 0.5
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

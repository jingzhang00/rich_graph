import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import time
import numpy as np
import my_networkx as my_nx
import random
from pre_eff import ActivityProcessor


def refine(effect, precondition):
    for key, value in precondition.items():
        if key not in effect or effect[key] != value:
            return False
    return True


def match(precondition, effect):
    for key, precondition_values in precondition.items():
        if key in effect:
            effect_values = effect[key]
            if not any(value in effect_values for value in precondition_values):
                return False
        else:
            return False
    return True


def parse_graph(file_path, rich_info):
    graph = nx.DiGraph()
    with open(file_path, 'r') as file:
        current_node = None
        neighbors = []
        weights = []

        for line in file:
            if 'name:' in line:
                if current_node and neighbors:
                    for neighbor, weight in zip(neighbors, weights):
                        eff = rich_info[current_node]['effect']
                        pre = rich_info[current_node]['precondition']
                        if match(pre, eff):
                            graph.add_edge(current_node, neighbor, weight=weight)
                        else:
                            print("Remove edge: \n")
                            print("Current node: ", current_node)
                            print("effect: ", eff)
                            print("neighbor: ", neighbor)
                            print("precondition: ", pre)
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



def build_graph(graph, delay):
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
    nx.draw_networkx_nodes(graph, pos, node_size=node_size, node_color=node_color, ax=ax)
    nx.draw_networkx_labels(graph, pos, ax=ax)

    edge_weights = nx.get_edge_attributes(graph, 'weight')
    curved_edges = [edge for edge in graph.edges() if reversed(edge) in graph.edges() and edge in edge_weights]
    straight_edges = list(set(graph.edges()) - set(curved_edges))

    nx.draw_networkx_edges(graph, pos, ax=ax, edgelist=straight_edges, edge_color=edge_color, width=2, arrowstyle='-|>', arrowsize=15)
    arc_rad = 0.1
    nx.draw_networkx_edges(graph, pos, ax=ax, edgelist=curved_edges, connectionstyle=f'arc3, rad = {arc_rad}', edge_color=edge_color, width=2, arrowstyle='-|>', arrowsize=15)

    if highlight:
        for item in highlight:
            if isinstance(item, tuple):
                if item in curved_edges or (item[1], item[0]) in curved_edges:
                    nx.draw_networkx_edges(graph, pos, edgelist=[item], edge_color=highlight_color, width=3,
                                           arrowstyle='-|>', arrowsize=20, ax=ax, connectionstyle=f'arc3, rad = {arc_rad}')
                else:
                    nx.draw_networkx_edges(graph, pos, edgelist=[item], edge_color=highlight_color, width=3,
                                           arrowstyle='-|>', arrowsize=20, ax=ax)
            else:
                nx.draw_networkx_nodes(graph, pos, nodelist=[item], node_size=node_size, node_color=highlight_color, ax=ax)

    curved_edge_labels = {edge: edge_weights.get(edge) for edge in curved_edges}
    straight_edge_labels = {edge: edge_weights.get(edge) for edge in straight_edges}
    my_nx.my_draw_networkx_edge_labels(graph, pos, ax=ax, edge_labels=curved_edge_labels, font_size=12, rotate=False, rad=arc_rad)
    nx.draw_networkx_edge_labels(graph, pos, ax=ax, edge_labels=straight_edge_labels, font_size=12, rotate=False)

    if start_node is not None:
        nx.draw_networkx_nodes(graph, pos, nodelist=[start_node], node_size=node_size, node_color=start_color, ax=ax)
    if end_node is not None:
        nx.draw_networkx_nodes(graph, pos, nodelist=[end_node], node_size=node_size, node_color=end_color, ax=ax)

    canvas.draw()
    if update:
        root.update()


def draw_path(G, path, ax, pos):
    edges = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
    arc_rad = 0.1

    for edge in edges:
        if (edge[1], edge[0]) in G.edges():
            nx.draw_networkx_edges(G, pos, edgelist=[edge], edge_color=highlight_color, width=3,
                                   ax=ax, connectionstyle=f'arc3, rad = {arc_rad}')
        else:
            nx.draw_networkx_edges(G, pos, edgelist=[edge], edge_color=highlight_color, width=3, ax=ax)


def nx_to_matrix(graph):
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


def monte_carlo_widest_path(graph, start_node, end_node, iterations=3000, randomness_factor=0.2):
    best_path = None
    best_min_width = -np.inf
    for _ in range(iterations):
        path = [start_node]
        visited = set([start_node])
        current_node = start_node
        min_width = np.inf

        while current_node != end_node:
            next_nodes = [n for n, d in graph[current_node].items() if 'weight' in d and n not in visited]
            if len(next_nodes) == 0:
                break
            if random.random() < randomness_factor:
                chosen_node = random.choice(next_nodes)
            else:
                widths = [graph[current_node][n]['weight'] for n in next_nodes]
                max_width_index = np.argmax(widths)
                chosen_node = next_nodes[max_width_index]
            min_width = min(min_width, graph[current_node][chosen_node]['weight'])
            current_node = chosen_node
            path.append(current_node)
            visited.add(current_node)

        if current_node == end_node and min_width > best_min_width:
            best_path = path
            best_min_width = min_width
    return best_path, best_min_width


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
                draw_graph(G, highlight=[start_node])
                canvas.draw()
                messagebox.showinfo("Info", f"Start node set to {node}")
            elif end_node is None and node != start_node:
                end_node = node
                draw_graph(G, highlight=[start_node, end_node])
                canvas.draw()
                messagebox.showinfo("Info", f"End node set to {node}")
                widest_path, widest_min_width = monte_carlo_widest_path(G, start_node, end_node)
                if widest_path:
                    draw_path(G, widest_path, ax, pos)
                    canvas.draw()
                    print("Widest Path:", widest_path, "with widest minimum width:", widest_min_width)
                    start_node, end_node = None, None
            return
    messagebox.showinfo("Info", "No node was clicked.")


def modify_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    corrected_lines = []
    for line in lines:
        if 'GranularActivity_' in line:
            parts = line.split('GranularActivity_')
            identifier = 'GranularActivity_' + parts[1].split(' ')[0]
            new_line = parts[0] + identifier + '\n'
            corrected_lines.append(new_line)
        else:
            corrected_lines.append(line)
    with open(file_path, 'w') as file:
        file.writelines(corrected_lines)


def clear_highlight():
    global start_node, end_node
    start_node, end_node = None, None
    draw_graph(G)
    canvas.draw()


if __name__ == "__main__":
    file_path = 'data/task_graph/multiple_demos/task_graph.txt'
    # modify_file(file_path)
    delay = 0.5
    threshold = 30
    node_color = '#4f5d75'
    highlight_color = '#ffc857'
    edge_color = '#bfc0c0'
    start_color = '#db3a34'
    end_color = '#177e89'
    path = 'data/task_graph/multiple_demos'
    root = tk.Tk()
    root.wm_title("Visualization")
    fig, ax = plt.subplots(figsize=(10, 7), dpi=100)
    canvas = FigureCanvasTkAgg(fig, master=root)
    processor = ActivityProcessor(path, threshold)
    rich_info = processor.rich_info
    G = parse_graph(file_path, rich_info)
    # pos = nx.circular_layout(G)
    pos = nx.spring_layout(G)

    start_node = None
    end_node = None

    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    canvas.mpl_connect("button_press_event", on_click)

    clear_button = tk.Button(root, text="Clear", command=clear_highlight, font=("Helvetica", 12))
    clear_button.pack(side=tk.BOTTOM, padx=20, pady=10)

    root.after(1000, lambda: build_graph(G, delay))
    tk.mainloop()
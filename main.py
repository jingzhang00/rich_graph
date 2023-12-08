import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import my_networkx as my_nx
import time
from pre_eff import ActivityProcessor
import utils
import os
from tkinter import filedialog


node_color = '#4f5d75'
highlight_color = '#ffc857'
edge_color = '#bfc0c0'
start_color = '#db3a34'
end_color = '#177e89'


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


def build_graph(graph, delay=0.5):
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



def on_click(event):
    global start_node, end_node
    if event.xdata is None or event.ydata is None:
        return
    for node, node_pos in pos.items():
        distance = ((event.xdata - node_pos[0]) ** 2 + (event.ydata - node_pos[1]) ** 2) ** 0.5
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
                widest_path, widest_min_width = utils.monte_carlo_widest_path(G, start_node, end_node)
                if widest_path:
                    draw_path(G, widest_path, ax, pos)
                    canvas.draw()
                    print("Widest Path:", widest_path, "with widest minimum width:", widest_min_width)
                    start_node, end_node = None, None
            return
    messagebox.showinfo("Info", "No node was clicked.")


def draw_graph(graph, highlight=None, update=False):
    ax.clear()
    node_size = 600
    nx.draw_networkx_nodes(graph, pos, node_size=node_size, node_color=node_color, ax=ax)
    nx.draw_networkx_labels(graph, pos, ax=ax)

    edge_weights = nx.get_edge_attributes(graph, 'weight')
    curved_edges = [edge for edge in graph.edges() if reversed(edge) in graph.edges() and edge in edge_weights]
    straight_edges = list(set(graph.edges()) - set(curved_edges))

    nx.draw_networkx_edges(graph, pos, ax=ax, edgelist=straight_edges, edge_color=edge_color, width=2, arrowstyle='-|>',
                           arrowsize=15)
    arc_rad = 0.1
    nx.draw_networkx_edges(graph, pos, ax=ax, edgelist=curved_edges, connectionstyle=f'arc3, rad = {arc_rad}',
                           edge_color=edge_color, width=2, arrowstyle='-|>', arrowsize=15)

    if highlight:
        for item in highlight:
            if isinstance(item, tuple):
                if item in curved_edges or (item[1], item[0]) in curved_edges:
                    nx.draw_networkx_edges(graph, pos, edgelist=[item], edge_color=highlight_color, width=3,
                                           arrowstyle='-|>', arrowsize=20, ax=ax,
                                           connectionstyle=f'arc3, rad = {arc_rad}')
                else:
                    nx.draw_networkx_edges(graph, pos, edgelist=[item], edge_color=highlight_color, width=3,
                                           arrowstyle='-|>', arrowsize=20, ax=ax)
            else:
                nx.draw_networkx_nodes(graph, pos, nodelist=[item], node_size=node_size, node_color=highlight_color,
                                       ax=ax)

    curved_edge_labels = {edge: edge_weights.get(edge) for edge in curved_edges}
    straight_edge_labels = {edge: edge_weights.get(edge) for edge in straight_edges}
    my_nx.my_draw_networkx_edge_labels(graph, pos, ax=ax, edge_labels=curved_edge_labels, font_size=12, rotate=False,
                                       rad=arc_rad)
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


def clear_highlight():
    global start_node, end_node
    start_node, end_node = None, None
    draw_graph(G)
    canvas.draw()


def refine_button():
    global G
    G = utils.refine_graph(G, rich_info)
    draw_graph(G)


def recover():
    global G
    G = parse_graph(task_graph)
    draw_graph(G)


def save_graph():
    filepath = filedialog.asksaveasfilename(defaultextension='.png',
                                            filetypes=[("PNG files", "*.png"), ("All Files", "*.*")])
    if filepath:
        try:
            fig.savefig(filepath, dpi=300)
            messagebox.showinfo("Save Graph", f"Graph saved successfully at\n{filepath}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save graph.\n{e}")


if __name__ == "__main__":
    task_graph = 'data/13_demos/task_graph.txt'
    # modify_file(file_path)
    info_path = 'data/13_demos'
    root = tk.Tk()
    root.wm_title("Visualization")
    fig, ax = plt.subplots(figsize=(10, 7), dpi=100)
    fig.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
    canvas = FigureCanvasTkAgg(fig, master=root)
    processor = ActivityProcessor(info_path)
    rich_info = processor.rich_info
    G = parse_graph(task_graph)
    # pos = nx.circular_layout(G)
    pos = nx.spring_layout(G)

    start_node = None
    end_node = None

    style = ttk.Style()
    style.configure('TButton', font=('Helvetica', 12))

    outer_frame = tk.Frame(root)
    outer_frame.pack(side=tk.RIGHT, fill=tk.Y, expand=False)

    button_frame = tk.Frame(outer_frame)
    button_frame.pack(side=tk.TOP, expand=True)

    clear = ttk.Button(button_frame, text="Clear", command=clear_highlight)
    clear.pack(padx=10, pady=10)

    refine = ttk.Button(button_frame, text="Refine", command=refine_button)
    refine.pack(padx=10, pady=10)

    recover = ttk.Button(button_frame, text="Recover", command=recover)
    recover.pack(padx=10, pady=10)

    save_button = ttk.Button(button_frame, text="Save", command=save_graph)
    save_button.pack(padx=10, pady=10)

    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    canvas.mpl_connect("button_press_event", on_click)

    root.after(1000, lambda: build_graph(G))
    tk.mainloop()

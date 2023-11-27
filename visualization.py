import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx


file_path = 'data/task_graph/multiple_demos/task_graph.txt'


def parse_graph(file_path):
    graph = nx.DiGraph()
    current_node = None
    neighbors = []
    weights = []

    with open(file_path, 'r') as file:
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


G = parse_graph(file_path)

root = tk.Tk()
root.wm_title("Visualization")

fig, ax = plt.subplots(figsize=(10, 7))
canvas = FigureCanvasTkAgg(fig, master=root)

start_node = None
end_node = None
pos = nx.spring_layout(G)


def draw_graph():
    ax.clear()

    nx.draw(G, pos, with_labels=True, node_size=2000, node_color='skyblue', ax=ax)

    if start_node is not None:
        nx.draw_networkx_nodes(G, pos, nodelist=[start_node], node_size=2500, node_color='red', ax=ax)
    if end_node is not None:
        nx.draw_networkx_nodes(G, pos, nodelist=[end_node], node_size=2500, node_color='blue', ax=ax)

    canvas.draw()


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
            draw_graph()
            return

    messagebox.showinfo("Info", "No node was clicked.")


draw_graph()

canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
canvas.mpl_connect("button_press_event", on_click)

tk.mainloop()

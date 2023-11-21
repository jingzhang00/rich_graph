import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import tkinter as tk
from tkinter import messagebox


class TaskNode:
    def __init__(self, name, preconditions=None, effects=None):
        self.name = name
        self.preconditions = preconditions if preconditions is not None else {}
        self.effects = effects if effects is not None else {}

    def __repr__(self):
        return self.name


def is_transition_valid(effect, precondition):
    for key, value in effect.items():
        if key in precondition and precondition[key] != value:
            return False
    return True


def refine_graph(G):
    H = G.copy()
    for node in list(H.nodes):
        if node.preconditions == {"None": None} or node.effects == {"None": None}:
            H.remove_node(node)
    for (u, v, data) in list(G.edges(data=True)):
        if not is_transition_valid(u.effects, v.preconditions):
            H.remove_edge(u, v)
    isolated = list(nx.isolates(H))
    for node in isolated:
        H.remove_node(node)
    return H

G = nx.DiGraph()
preconditions = {
    "Pour": {"open_gripper": False, "graspable": True, "above_sink": True},
    "Reach": {"on_table": True, "graspable": False, "above_sink": False},
    "Grasp": {"on_table": True, "open_gripper": True, "graspable": True, "above_sink": False},
    "Put": {"graspable": True, "above_sink": False},
    "New": {"None": None},  # manually marked as wrong skill
}

effects = {
    "Pour": {"on_table": True, "open_gripper": True, "graspable": False, "above_sink": False},
    "Reach": {"on_table": True, "graspable": True, "above_sink": False},
    "Grasp": {"open_gripper": False, "graspable": True, "above_sink": False},
    "Put": {"open_gripper": False, "graspable": True, "above_sink": True},
    "New": {"None": None},
}

task_nodes = {name: TaskNode(name, preconditions[name], effects[name]) for name in preconditions}
for task_node in task_nodes.values():
    G.add_node(task_node)

edges = [
    ("Pour", "Reach"),
    ("Pour", "New"),
    ("Reach", "Pour"),
    ("Reach", "Grasp"),
    ("Reach", "Put"),
    ("Grasp", "Reach"),
    ("Grasp", "New"),
    ("Grasp", "Put"),
    ("New", "Put"),
    ("New", "Pour"),
    ("New", "Grasp"),
    ("New", "Reach"),
    ("Put", "New"),
    ("Put", "Pour")
]

for edge in edges:
    G.add_edge(task_nodes[edge[0]], task_nodes[edge[1]], weight=1)

H = refine_graph(G)

root = tk.Tk()
root.wm_title("UI")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
canvas = FigureCanvasTkAgg(fig, master=root)

start_node = None
end_node = None


def draw_graphs():
    ax1.clear()
    ax2.clear()

    nx.draw(G, pos, with_labels=True, node_size=2000, node_color='skyblue', ax=ax1)
    nx.draw(H, pos, with_labels=True, node_size=2000, node_color='lightgreen', ax=ax2)

    if start_node is not None:
        nx.draw_networkx_nodes(G, pos, nodelist=[start_node], node_size=2500, node_color='red', ax=ax1)
        nx.draw_networkx_nodes(H, pos, nodelist=[start_node], node_size=2500, node_color='red', ax=ax2)
    if end_node is not None:
        nx.draw_networkx_nodes(G, pos, nodelist=[end_node], node_size=2500, node_color='blue', ax=ax1)
        nx.draw_networkx_nodes(H, pos, nodelist=[end_node], node_size=2500, node_color='blue', ax=ax2)

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
            draw_graphs()
            return

    messagebox.showinfo("Info", "No node was clicked.")


pos = nx.spring_layout(G)
draw_graphs()

canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
canvas.mpl_connect("button_press_event", on_click)

tk.mainloop()

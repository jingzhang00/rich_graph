import networkx as nx
import matplotlib.pyplot as plt


class TaskNode:
    def __init__(self, name, preconditions=None, effects=None):
        self.name = name
        self.preconditions = preconditions if preconditions is not None else {}
        self.effects = effects if effects is not None else {}

    def __repr__(self):
        return self.name


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


H = refine_graph(G)

plt.figure(figsize=(15, 7))
plt.subplot(1, 2, 1)
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, arrows=True, node_size=2000, node_color='skyblue', edge_color='gray', width=2)
plt.title('Original Graph')
plt.subplot(1, 2, 2)
nx.draw(H, pos, with_labels=True, arrows=True, node_size=2000, node_color='lightgreen', edge_color='gray', width=2)
plt.title('Refined Graph')
plt.tight_layout()
plt.show()

import networkx as nx
import numpy as np
import random

def match(precondition, effect):
    for key in precondition:
        if not isinstance(precondition[key], list):
            precondition[key] = [precondition[key]]
    for key in effect:
        if not isinstance(effect[key], list):
            effect[key] = [effect[key]]

    for key, precondition_values in precondition.items():
        if key in effect:
            effect_values = effect[key]
            if not any(value in effect_values for value in precondition_values):
                return False
        else:
            return False
    return True


def refine_graph(graph, rich_info):
    refined_graph = nx.DiGraph()
    for node in graph.nodes:
        refined_graph.add_node(node)

    for u, v, data in graph.edges(data=True):
        if u in rich_info and v in rich_info:
            if 'effect' in rich_info[u] and 'precondition' in rich_info[v]:
                eff = rich_info[u]['effect']
                pre = rich_info[v]['precondition']
                if match(pre, eff):
                    refined_graph.add_edge(u, v, weight=data['weight'])
                else:
                    print("=======================================")
                    print("Remove edge due to mismatch")
                    print("Current node: ", u)
                    print("effect: ", eff)
                    print("neighbor: ", v)
                    print("precondition: ", pre)
                    print("=======================================")
        else:
            print(f"Removing edge ({u}, {v}) as one or both nodes are not in rich_info.")
    return refined_graph



def refine(effect, precondition):
    for key, value in precondition.items():
        if key not in effect or effect[key] != value:
            return False
    return True


def modify_file(file_path):
    # run once to remove the suffix part of granular activity
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
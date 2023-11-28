import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import time
import numpy as np

file_path = 'data/task_graph/2023-11-27-15-09-22/task_graph.txt'
delay = 3

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


# def build_graph_dynamically(graph, delay):
#     dynamic_graph = nx.DiGraph()
#     for node in graph.nodes:
#         if node not in dynamic_graph:
#             dynamic_graph.add_node(node)
#             draw_graph(dynamic_graph, highlight=[node], update=True)
#             time.sleep(delay)

#         for neighbor in graph.neighbors(node):
#             if neighbor not in dynamic_graph:
#                 dynamic_graph.add_edge(node, neighbor, weight=graph[node][neighbor]['weight'])
#                 draw_graph(dynamic_graph, highlight=[(node, neighbor)], update=True)
#                 time.sleep(delay)
#                 dynamic_graph.add_node(neighbor)
#                 draw_graph(dynamic_graph, highlight=[neighbor], update=True)
#                 time.sleep(delay)
#             elif (node, neighbor) not in dynamic_graph.edges:
#                 dynamic_graph.add_edge(node, neighbor, weight=graph[node][neighbor]['weight'])
#                 draw_graph(dynamic_graph, highlight=[(node, neighbor)], update=True)
#                 time.sleep(delay)

#     messagebox.showinfo("Info", "Graph construction complete.")
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
                # draw_graph(dynamic_graph, highlight=[neighbor], update=True)
                time.sleep(delay)
            elif (node, neighbor) not in dynamic_graph.edges:
                dynamic_graph.add_edge(
                    node, neighbor, weight=graph[node][neighbor]['weight'])
                draw_graph(dynamic_graph, highlight=[
                           (node, neighbor)], update=True)
                time.sleep(delay)

    messagebox.showinfo("Info", "Graph construction complete.")


def draw_graph(graph, highlight=None, update=False):
    ax.clear()

    # 可以尝试调整节点大小
    node_size = 700  # 减小节点大小
    # nx.draw(graph, pos, with_labels=True, node_size=2000, node_color='skyblue', edge_color='gray', ax=ax)
    nx.draw_networkx_nodes(graph, pos, node_size=node_size,
                           node_color='skyblue', ax=ax)
    nx.draw_networkx_labels(graph, pos, ax=ax)
    # 自定义绘制每一条边
    
    edge_weights = nx.get_edge_attributes(graph, 'weight')

    for edge in graph.edges():
        # 如果存在反向边，则稍微弯曲
        if graph.has_edge(edge[1], edge[0]):
            connectionstyle = 'arc3,rad=0.1'
        else:
            connectionstyle = 'arc3,rad=0'

        # # 调整箭头样式和大小
        nx.draw_networkx_edges(graph, pos, edgelist=[edge], connectionstyle=connectionstyle,
                               edge_color='gray', width=2, arrowstyle='->', arrowsize=20, ax=ax)
        lable_position=get_curved_edge_midpoint(pos, edge, connectionstyle=connectionstyle, rad=0.1)
        edge_label = edge_weights[edge]  # 假设这是您的边权重
        # ax.text(lable_position[0], lable_position[1], edge_label, style='italic', bbox={'facecolor': 'red', 'alpha': 0.5, 'pad': 10})
        ax.text(lable_position[0], lable_position[1], edge_label, style='italic', fontsize=8, bbox={
                'facecolor': 'white', 'edgecolor': 'black', 'boxstyle': 'circle', 'pad': 0.5}, zorder=3)
        # print(edge_weights[edge])
        # nx.draw_networkx_edge_labels(graph, pos, edge_labels={edge: edge_weights[edge]}, label_pos=0.38, ax=ax)


    # 高亮处理
    if highlight:
        if isinstance(highlight[0], tuple):
            # 高亮显示边和相应的目标节点
            nx.draw_networkx_edges(graph, pos, edgelist=highlight, connectionstyle=connectionstyle, edge_color='red', width=2,
                                   arrowstyle='->', arrowsize=20, ax=ax)
            target_nodes = [edge[1] for edge in highlight]
            nx.draw_networkx_nodes(
                graph, pos, nodelist=target_nodes, node_size=node_size, node_color='green', ax=ax)
        else:
            # 高亮显示节点
            nx.draw_networkx_nodes(
                graph, pos, nodelist=highlight, node_size=node_size, node_color='green', ax=ax)

    # 特殊节点的颜色处理
    if start_node is not None:
        nx.draw_networkx_nodes(graph, pos, nodelist=[
                               start_node], node_size=node_size, node_color='red', ax=ax)
    if end_node is not None:
        nx.draw_networkx_nodes(graph, pos, nodelist=[
                               end_node], node_size=node_size, node_color='blue', ax=ax)

    canvas.draw()
    if update:
        root.update()


# def get_curved_edge_midpoint(pos, edge, connectionstyle, rad=0.1):
#     """
#     估算弯曲边的中点。
#     pos: 节点位置字典
#     edge: 边的元组 (u, v)
#     rad: 弯曲半径
#     """
#     src_pos = np.array(pos[edge[0]])
#     dst_pos = np.array(pos[edge[1]])

#     # 计算边的中心点
#     mid_point = (src_pos + dst_pos) / 2

#     # 如果边是弯曲的，则进行相应的调整
#     if connectionstyle == 'arc3,rad=0.1':
#         edge_vec = dst_pos - src_pos
#         edge_length = np.linalg.norm(edge_vec)
#         perp_vec = np.array([-edge_vec[1], edge_vec[0]])
#         perp_vec = perp_vec / np.linalg.norm(perp_vec)  # 单位化

#         # 估算弯曲边的圆弧半径
#         arc_radius = edge_length / (2 * rad)

#         # 估算弯曲边的圆弧中点偏移
#         mid_offset = np.sqrt(arc_radius**2 - (edge_length / 2)**2)
#         mid_point += perp_vec * mid_offset

#     return mid_point


def get_curved_edge_midpoint(pos,edge,connectionstyle,rad=0.1):
    """
    近似计算弯曲边的中点。
    pos: 节点位置字典
    edge: 边的元组 (u, v)
    rad: 弯曲半径
    """
    src_pos = np.array(pos[edge[0]])
    dst_pos = np.array(pos[edge[1]])

    # 计算边的中心点
    mid_point = (src_pos + dst_pos) / 2

    # 计算边向量和垂直向量
    edge_vec = dst_pos - src_pos
    perp_vec = np.array([-edge_vec[1], edge_vec[0]])
    perp_vec = perp_vec / np.linalg.norm(perp_vec)  # 单位化

    # 根据弯曲半径和方向调整中点位置
    if connectionstyle == 'arc3,rad=0.1':  # 对于双向边，向一个方向偏移
        mid_point += perp_vec * rad

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

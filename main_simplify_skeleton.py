import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import networkx as nx
from collections import deque


def load_ply_as_graph(file_path):
    """
    Loads a PLY file and returns a graph (NetworkX object) and vertex coordinates.

    Args:
        file_path (str): The path to the PLY file.

    Returns:
        tuple: A tuple containing a NetworkX graph object and a numpy array
               of vertex coordinates.
    """
    with open(file_path, 'r') as f:
        lines = f.readlines()

    # Find the end of the header
    header_end_index = lines.index('end_header\n') + 1

    # Get vertex and edge counts from header
    vertex_count = 0
    edge_count = 0
    for line in lines[:header_end_index]:
        if 'element vertex' in line:
            vertex_count = int(line.split()[-1])
        elif 'element edge' in line:
            edge_count = int(line.split()[-1])

    # Parse vertex data (x, y, z coordinates)
    vertex_data = np.loadtxt(lines[header_end_index:header_end_index + vertex_count])
    if vertex_data.shape[1] > 3:
        # Some PLY files may have other properties like normals or color,
        # we'll just take the first three (x, y, z)
        vertex_data = vertex_data[:, :3]

    # Parse edge data (vertex indices)
    edge_data = np.loadtxt(lines[header_end_index + vertex_count:header_end_index + vertex_count + edge_count],
                           dtype=int)

    # Create a NetworkX graph from the edges
    graph = nx.Graph()
    graph.add_edges_from(edge_data)

    return graph, vertex_data


def display_graph_3d(graph, vertex_coords):
    """
    Displays a graph in a 3D plot using matplotlib.

    Args:
        graph (networkx.Graph): The graph to display.
        vertex_coords (numpy.ndarray): The 3D coordinates of the vertices.
    """
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Create a dictionary to map vertex indices to their 3D positions
    pos = {i: coord for i, coord in enumerate(vertex_coords)}

    # Plot the vertices
    for i, (x, y, z) in pos.items():
        ax.scatter(x, y, z, c='b', marker='o', s=10)  # 's' is marker size

    # Plot the edges
    for edge in graph.edges():
        start_node, end_node = edge
        x_coords = [pos[start_node][0], pos[end_node][0]]
        y_coords = [pos[start_node][1], pos[end_node][1]]
        z_coords = [pos[start_node][2], pos[end_node][2]]
        ax.plot(x_coords, y_coords, z_coords, color='k', linewidth=0.5)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('3D Graph Visualization')

    # Set the aspect ratio to 'auto' or 'equal' to prevent distortion
    # ax.set_aspect('equal')
    ax.set_box_aspect([np.ptp(vertex_coords[:, 0]), np.ptp(vertex_coords[:, 1]), np.ptp(vertex_coords[:, 2])])

    plt.show()


def find_tree_diameter_path(graph):
    """
    Finds the longest simple path in a tree, which corresponds to its diameter.
    This path is treated as the "main stem" of the tree.

    Args:
        graph (networkx.Graph): A connected graph that is a tree.

    Returns:
        list: A list of nodes representing the main stem.
    """
    # Find one endpoint of the diameter by running BFS from an arbitrary node (0)
    bfs_result = nx.single_source_shortest_path_length(graph, 0)
    farthest_node, _ = max(bfs_result.items(), key=lambda item: item[1])

    # Find the other endpoint of the diameter by running BFS from the first farthest node
    bfs_result_2 = nx.single_source_shortest_path_length(graph, farthest_node)
    farthest_node_2, _ = max(bfs_result_2.items(), key=lambda item: item[1])

    # Get the path between the two farthest nodes
    return nx.shortest_path(graph, source=farthest_node, target=farthest_node_2)


def compute_depths_from_stem(graph, stem_nodes):
    """
    Computes the depth of each vertex relative to the main stem.
    Stem nodes are at depth 0. All other nodes have a depth equal to their
    shortest distance to any node on the stem.

    Args:
        graph (networkx.Graph): The input graph (tree).
        stem_nodes (list): A list of nodes that constitute the main stem.

    Returns:
        dict: A dictionary mapping each vertex to its depth.
    """
    depths = {node: 0 for node in stem_nodes}
    queue = deque([(node, 0) for node in stem_nodes])

    while queue:
        current_node, current_depth = queue.popleft()

        for neighbor in graph.neighbors(current_node):
            if neighbor not in depths:
                depths[neighbor] = current_depth + 1
                queue.append((neighbor, current_depth + 1))

    return depths

def trim_graph_by_depth(graph, depths, max_depth):
    """
    Removes vertices and edges from a graph that are beyond a specified maximum depth.

    Args:
        graph (networkx.Graph): The original graph.
        depths (dict): The dictionary of vertex depths.
        max_depth (int): The maximum allowed depth.

    Returns:
        networkx.Graph: A new graph containing only the vertices and edges within the max depth.
    """
    trimmed_graph = nx.Graph()
    for u, v in graph.edges():
        if u in depths and v in depths:
            if depths[u] <= max_depth and depths[v] <= max_depth:
                trimmed_graph.add_edge(u, v)
    return trimmed_graph


def save_graph_as_ply(file_path, graph, vertex_coords):
    """
    Saves a graph and its corresponding vertex coordinates to a PLY file in ASCII format.

    Args:
        file_path (str): The path to save the new PLY file.
        graph (networkx.Graph): The graph to save.
        vertex_coords (numpy.ndarray): The 3D coordinates of the original vertices.
    """
    # Create a mapping from old node indices to new sequential indices for the edge list
    old_to_new_index = {node: i for i, node in enumerate(graph.nodes())}

    # Get the vertex coordinates for the nodes in the trimmed graph
    trimmed_vertices = [vertex_coords[node] for node in graph.nodes()]

    with open(file_path, 'w') as f:
        # Write PLY header
        f.write("ply\n")
        f.write("format ascii 1.0\n")
        f.write(f"element vertex {len(trimmed_vertices)}\n")
        f.write("property double x\n")
        f.write("property double y\n")
        f.write("property double z\n")
        f.write(f"element edge {graph.number_of_edges()}\n")
        f.write("property int vertex1\n")
        f.write("property int vertex2\n")
        f.write("end_header\n")

        # Write vertex data
        for x, y, z in trimmed_vertices:
            f.write(f"{x} {y} {z}\n")

        # Write edge data using the new sequential indices
        for u, v in graph.edges():
            new_u = old_to_new_index[u]
            new_v = old_to_new_index[v]
            f.write(f"{new_u} {new_v}\n")

    print(f"Graph saved to '{file_path}' successfully.")


# Main execution block
if __name__ == "__main__":
    file_path = '/home/miguelangel/exports/output/topology-2025-07-11-tree-02-a.ply'
    output_path = '/home/miguelangel/exports/output/trimmed_graph.ply'

    try:
        # Load the initial graph and vertex positions
        graph, vertex_positions = load_ply_as_graph(file_path)
        print(f"Loaded {len(vertex_positions)} vertices and {graph.number_of_edges()} edges.")

        # Find the main stem of the tree
        if not nx.is_connected(graph):
            print("Warning: The graph is not connected. This script assumes a single tree structure.")
            # For non-connected graphs, we can find the longest path in the largest component
            largest_component = max(nx.connected_components(graph), key=len)
            subgraph = graph.subgraph(largest_component)
            stem_nodes = find_tree_diameter_path(subgraph)
        else:
            stem_nodes = find_tree_diameter_path(graph)

        print(f"Identified a main stem with {len(stem_nodes)} nodes. These are considered to be at depth 0.")

        # Compute depths relative to the main stem
        depths = compute_depths_from_stem(graph, stem_nodes)

        # Get user input for max depth
        max_depth_input = input("Enter a maximum depth to trim the graph to: ")

        try:
            max_depth = int(max_depth_input)

            # Trim the graph based on the max depth
            trimmed_graph = trim_graph_by_depth(graph, depths, max_depth)

            print(f"Displaying graph trimmed to a max depth of {max_depth}.")
            print(
                f"The trimmed graph has {trimmed_graph.number_of_nodes()} nodes and {trimmed_graph.number_of_edges()} edges.")

            # Display the trimmed graph
            display_graph_3d(trimmed_graph, vertex_positions)

            # Save the trimmed graph to a new PLY file
            save_graph_as_ply(output_path, trimmed_graph, vertex_positions)
        except ValueError:
            print("Error: Invalid input. Please enter an integer for the max depth.")

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found. Please ensure it is in the same directory as the script.")
    except Exception as e:
        print(f"An error occurred: {e}")
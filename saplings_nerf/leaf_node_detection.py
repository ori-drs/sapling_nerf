import numpy as np
import networkx as nx
from plyfile import PlyData
import open3d as o3d

def detect_leaf_nodes(topology_path, leaf_nodes_out):
    """
    Extract the terminal nodes in the topology graph. These nodes are considered
    leafs, and will be used for leaf segmentation.
        - Inputs: paths to files.
        - Outputs: terminal nodes saved to file.
    """

    ply = PlyData.read(topology_path)
    vertex_data = ply['vertex'].data
    points = np.vstack([vertex_data['x'], vertex_data['y'], vertex_data['z']]).T

    edge_data = ply['edge'].data
    edges = np.vstack([edge_data['vertex1'], edge_data['vertex2']]).T

    G = nx.Graph()
    G.add_edges_from(edges)

    leaf_nodes = [n for n in G.nodes if G.degree[n] == 1]
    leaf_points = points[leaf_nodes]

    leaf_pcd = o3d.geometry.PointCloud()
    leaf_pcd.points = o3d.utility.Vector3dVector(leaf_points)
    leaf_pcd.paint_uniform_color([0.1, 0.6, 0.1])

    o3d.io.write_point_cloud(leaf_nodes_out, leaf_pcd)
    print(f"Saved {len(leaf_points)} leaf nodes to: {leaf_nodes_out}")

    return

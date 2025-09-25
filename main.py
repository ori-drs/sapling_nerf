# main.py

import yaml
import os
from saplings_nerf.skeleton_extraction import extract_skeleton
from saplings_nerf.leaf_node_detection import detect_leaf_nodes
from saplings_nerf.leaf_region_segmentation import segment_leaf_region
from saplings_nerf.density_analysis import plot_leaf_density

# Load configuration
with open("config/config.yaml", "r") as f:
    config = yaml.safe_load(f)

input_folder = config["input_folder"]
output_folder = config["output_folder"]
input_file = config["input_file"]
down_sample = config.get("down_sample", 0.001)
radius = config.get("radius", 0.008)
run_skeleton = config.get("run_skeleton", True)
run_leaf_nodes = config.get("run_leaf_nodes", True)
run_leaf_region = config.get("run_leaf_region", True)
run_density_plot = config.get("run_density_plot", True)

# Step 1: Extract skeleton and topology
if run_skeleton:
    skeleton_file, topology_file = extract_skeleton(input_folder, output_folder, input_file, down_sample)
else:
    topology_file = os.path.join(output_folder, f"topology-{input_file.replace('.pcd', '.ply')}")
    skeleton_file = os.path.join(output_folder, f"skeleton-{input_file.replace('.pcd', '.pcd')}")

# Step 2: Detect leaf nodes from topology
if run_leaf_nodes:
    leaf_nodes_file = detect_leaf_nodes(topology_file, output_folder)
else:
    leaf_nodes_file = os.path.join(output_folder, "leaf-nodes.pcd")

# Step 3: Segment leaf region from full point cloud
if run_leaf_region:
    leaf_region_file, rest_region_file = segment_leaf_region(
        os.path.join(input_folder, input_file), leaf_nodes_file, output_folder, radius)
else:
    leaf_region_file = os.path.join(output_folder, f"leaf-region-{input_file.replace('.pcd', '')}.pcd")
    rest_region_file = os.path.join(output_folder, f"rest-region-{input_file.replace('.pcd', '')}.pcd")

# Step 4: Plot density distribution
if run_density_plot:
    plot_leaf_density(leaf_region_file, rest_region_file, output_folder)

print("\nPipeline complete.")
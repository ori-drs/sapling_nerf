# main.py

import yaml
import os
from saplings_nerf.skeleton_extraction import extract_skeleton
from saplings_nerf.leaf_node_detection import detect_leaf_nodes
from saplings_nerf.leaf_region_segmentation import segment_leaf_region

# Load configuration
with open("config/config.yaml", "r") as f:
    config = yaml.safe_load(f)

input_folder = config["input_folder"]
output_folder = config["output_folder"]
input_file = config["input_file"]
down_sample = config.get("down_sample", 0.001)
radius = config.get("radius", 0.008)

# Step 1: Extract skeleton and topology
skeleton_file, topology_file = extract_skeleton(input_folder, output_folder, input_file, down_sample)

# Step 2: Detect leaf nodes from topology
leaf_nodes_file = detect_leaf_nodes(topology_file, output_folder)

# Step 3: Segment leaf region from full point cloud
leaf_region_file, rest_region_file = segment_leaf_region(
    os.path.join(input_folder, input_file), leaf_nodes_file, output_folder, radius)

print("\nPipeline complete.")

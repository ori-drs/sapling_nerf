# saplings_nerf/skeleton_extraction.py

import open3d as o3d
import numpy as np
from pc_skeletor import LBC
import warnings

warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)

def extract_skeleton(input_path, output_path, filename, down_sample):
    pcd_file = f"{input_path}/{filename}"
    pcd = o3d.io.read_point_cloud(pcd_file)
    print("Loaded point cloud:", pcd)

    lbc = LBC(point_cloud=pcd, down_sample=down_sample)
    lbc.extract_skeleton()
    lbc.extract_topology()

    skeleton_out = f"{output_path}/skeleton-{filename}"
    topology_out = f"{output_path}/topology-{filename.replace('.pcd', '.ply')}"

    o3d.io.write_point_cloud(skeleton_out, lbc.contracted_point_cloud)
    o3d.io.write_line_set(topology_out, lbc.topology)

    print(f"Skeleton saved to: {skeleton_out}")
    print(f"Topology saved to: {topology_out}")

    return skeleton_out, topology_out

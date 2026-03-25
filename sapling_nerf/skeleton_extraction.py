import open3d as o3d
import numpy as np
from pc_skeletor import LBC
import warnings

warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)

def extract_skeleton(input_path, output_path, skeleton_out, topology_out, down_sample):
    """
    Extract skeleton and topology from pc-skeletor module
    from a provided point cloud (expected from NeRF/3DGS).
        - Inputs: paths to files.
        - Outputs: skeleton and topology saved to file.
    """

    pcd = o3d.io.read_point_cloud(input_path)
    print("Loaded point cloud:", pcd)

    lbc = LBC(point_cloud=pcd, down_sample=down_sample)
    lbc.extract_skeleton()
    lbc.extract_topology()

    o3d.io.write_point_cloud(skeleton_out, lbc.contracted_point_cloud)
    o3d.io.write_line_set(topology_out, lbc.topology)

    print(f"Skeleton saved to: {skeleton_out}")
    print(f"Topology saved to: {topology_out}")

    return

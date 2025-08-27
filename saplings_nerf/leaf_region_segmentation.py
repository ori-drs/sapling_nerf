# saplings_nerf/leaf_region_segmentation.py

import open3d as o3d
import numpy as np
import os

def segment_leaf_region(full_pcd_path, leaf_nodes_path, output_path, radius):
    original_pcd = o3d.io.read_point_cloud(full_pcd_path)
    original_points = np.asarray(original_pcd.points)

    leaf_pcd = o3d.io.read_point_cloud(leaf_nodes_path)
    leaf_points = np.asarray(leaf_pcd.points)

    leaf_tree = o3d.geometry.KDTreeFlann(leaf_pcd)
    mask = np.zeros(len(original_points), dtype=bool)

    for i, point in enumerate(original_points):
        [_, idxs, _] = leaf_tree.search_radius_vector_3d(point, radius)
        if len(idxs) > 0:
            mask[i] = True

    leaf_region = original_pcd.select_by_index(np.where(mask)[0])
    rest_region = original_pcd.select_by_index(np.where(mask)[0], invert=True)

    leaf_region.paint_uniform_color([0.1, 0.8, 0.1])
    rest_region.paint_uniform_color([0.5, 0.5, 0.5])

    base_name = os.path.basename(full_pcd_path).replace('.pcd', '')
    leaf_out = os.path.join(output_path, f"leaf-region-{base_name}.pcd")
    rest_out = os.path.join(output_path, f"rest-region-{base_name}.pcd")

    o3d.io.write_point_cloud(leaf_out, leaf_region)
    o3d.io.write_point_cloud(rest_out, rest_region)

    print(f"Saved leaf region to: {leaf_out}")
    print(f"Saved rest region to: {rest_out}")

    return leaf_out, rest_out

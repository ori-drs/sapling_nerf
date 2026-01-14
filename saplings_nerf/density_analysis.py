# saplings_nerf/density_analysis.py

import open3d as o3d
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from scipy.stats import gaussian_kde
from matplotlib import cm
from matplotlib.colors import Normalize
from matplotlib import rcParams

def plot_leaf_density(leaf_pcd_path, rest_region_path, output_path, num_bins=50):
    # Load segmented leaf point cloud
    leaf_pcd = o3d.io.read_point_cloud(leaf_pcd_path)
    leaf_points = np.asarray(leaf_pcd.points)

    # Load rest region point cloud
    rest_pcd = o3d.io.read_point_cloud(rest_region_path)
    rest_points = np.asarray(rest_pcd.points)

    # Basic sanity checks
    if leaf_points.size == 0:
        raise ValueError("Leaf point cloud has no points.")
    if rest_points.size == 0:
        raise ValueError("Rest-region point cloud has no points.")

    print(f"Leaf-Wood Ratio (LWR) = {leaf_points.size / rest_points.size}")

    # Extract Z coordinates (height) and rebase them so min across BOTH PCs is 0
    leaf_z = leaf_points[:, 2]
    rest_z = rest_points[:, 2]
    global_min_z = float(min(leaf_z.min(), rest_z.min()))
    # Rebased height for leaves
    z_coords = leaf_z - global_min_z

    # --- Plot A: KDE curve with heat coloring under the curve ---
    kde = gaussian_kde(z_coords)
    z_range = np.linspace(z_coords.min(), z_coords.max(), 500)
    density = kde(z_range)

    norm = Normalize(vmin=float(np.min(density)), vmax=float(np.max(density)))
    colors = cm.YlGn(norm(density))

    rcParams['font.size'] = 22

    plt.figure(figsize=(6, 8))
    for i in range(len(z_range) - 1):
        plt.fill_betweenx(
            [z_range[i], z_range[i+1]],
            [density[i], density[i+1]],
            color=colors[i],
            linewidth=0
        )
    # Helpful labels for the rebased axis
    # plt.xlabel("Estimated density")
    # plt.ylabel("Height (Z, rebased; min=0)")
    plt.xlim(0, 9.5)  # Limit density axis from 0 to 7
    plt.grid(True)
    plt.tight_layout()

    kde_path = os.path.join(
        output_path,
        f"leaf-density-kde-{os.path.basename(leaf_pcd_path).replace('.pcd', '.png')}"
    )
    plt.savefig(kde_path, dpi=150)
    plt.close()
    print(f"Saved KDE plot to: {kde_path}")

    # --- Plot B: Vertical heatmap (histogram along rebased Z) ---
    counts, _ = np.histogram(z_coords, bins=num_bins)
    heat = np.expand_dims(counts, axis=1)  # shape (bins, 1)

    plt.figure(figsize=(2, 8))
    sns.heatmap(
        heat[::-1],  # flip to match Z axis from bottom to top
        cmap="YlGnBu",
        cbar=True,
        xticklabels=False,
        yticklabels=False,
        linewidths=0.5,
        linecolor="gray"
    )
    plt.title("Vertical Leaf Heatmap (rebased)")
    plt.tight_layout()

    heatmap_path = os.path.join(
        output_path,
        f"leaf-density-heatmap-{os.path.basename(leaf_pcd_path).replace('.pcd', '.png')}"
    )
    plt.savefig(heatmap_path, dpi=150)
    plt.close()
    print(f"Saved heatmap to: {heatmap_path}")

    return kde_path, heatmap_path



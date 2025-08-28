# saplings_nerf/density_analysis.py

import open3d as o3d
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from scipy.stats import gaussian_kde
from matplotlib import cm
from matplotlib.colors import Normalize

def plot_leaf_density(leaf_pcd_path, output_path, num_bins=50):
    # Load segmented leaf point cloud
    leaf_pcd = o3d.io.read_point_cloud(leaf_pcd_path)
    leaf_points = np.asarray(leaf_pcd.points)

    # Extract Z coordinates (height)
    z_coords = leaf_points[:, 2]

    # --- Plot A: KDE curve with heat coloring under the curve ---
    kde = gaussian_kde(z_coords)
    z_range = np.linspace(z_coords.min(), z_coords.max(), 500)
    density = kde(z_range)

    norm = Normalize(vmin=min(density), vmax=max(density))
    colors = cm.YlGn(norm(density))

    plt.figure(figsize=(6, 8))
    for i in range(len(z_range) - 1):
        plt.fill_betweenx(
            [z_range[i], z_range[i+1]],
            [density[i], density[i+1]],
            color=colors[i],
            linewidth=0)

    plt.xlabel("Density estimate")
    plt.ylabel("Height (Z axis)")
    plt.title("Vertical Leaf Density (KDE - Heat Colored)")
    plt.grid(True)
    plt.tight_layout()

    kde_path = os.path.join(output_path, f"leaf-density-kde-{os.path.basename(leaf_pcd_path).replace('.pcd', '.png')}")
    plt.savefig(kde_path)
    plt.close()
    print(f"Saved KDE plot to: {kde_path}")

    # --- Plot B: Vertical heatmap ---
    counts, bin_edges = np.histogram(z_coords, bins=num_bins)
    heat = np.expand_dims(counts, axis=1)  # shape (bins, 1)

    plt.figure(figsize=(2, 8))
    sns.heatmap(
        heat[::-1],  # flip to match Z axis from bottom to top
        cmap="YlGnBu",
        cbar=True,
        xticklabels=False,
        yticklabels=False,
        linewidths=0.5,
        linecolor='gray')
    plt.title("Vertical Leaf Heatmap")
    plt.tight_layout()

    heatmap_path = os.path.join(output_path, f"leaf-density-heatmap-{os.path.basename(leaf_pcd_path).replace('.pcd', '.png')}")
    plt.savefig(heatmap_path)
    plt.close()
    print(f"Saved heatmap to: {heatmap_path}")

    return kde_path, heatmap_path


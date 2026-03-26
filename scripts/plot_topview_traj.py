from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# MATLAB (R2014b+) default color order (normalized RGB)
MATLAB_COLORS = [
    (0.0000, 0.4470, 0.7410),
    (0.8500, 0.3250, 0.0980),
    (0.9290, 0.6940, 0.1250),
    (0.4940, 0.1840, 0.5560),
    (0.4660, 0.6740, 0.1880),
    (0.3010, 0.7450, 0.9330),
    (0.6350, 0.0780, 0.1840),
]

def plot_topview_from_slam(input_csv, output_svg, delimiter, no_legend):
    """
    Plot top-view (XY plane) trajectories from a SLAM poses CSV, coloring each trajectory distinctly.

    Assumptions:
    - The CSV has a header (first line).
    - Column positions are 1-indexed as described:
    * Column 1: Pose ID
    * Column 4: X coordinate
    * Column 5: Y coordinate
    * Column 6: Z coordinate (not used here).
    - Trajectory grouping rule:
    * Trajectory index = floor(PoseID / 1000)
        (e.g., IDs 0-999 -> traj 0, IDs 1000-1999 -> traj 1, etc.)

    The function uses a MATLAB-like default color order to draw each trajectory as a continuous line.
    Output is saved as an SVG file.
    """

    input_path = Path(input_csv)
    output_path = Path(output_svg)

    # --- Read CSV ---
    # Treat the first line as header; we will access columns by position (not names).
    df = pd.read_csv(input_path, delimiter=delimiter, header=0, engine="python", skipinitialspace=True)

    # --- Validate minimum columns ---
    if df.shape[1] < 6:
        raise ValueError("The CSV must have at least 6 columns (ID in col 1, X in col 4, Y in col 5).")

    # --- Extract required columns by position ---
    # Columns are 1-indexed in the problem statement; convert to 0-based indices.
    pose_id = df.iloc[:, 0].astype(int)  # Column 1 -> index 0
    x = df.iloc[:, 3]                    # Column 4 -> index 3
    y = df.iloc[:, 4]                    # Column 5 -> index 4

    data = pd.DataFrame({"pose_id": pose_id, "x": x, "y": y})
    data["traj"] = (data["pose_id"] // 1000).astype(int)

    # --- Plot ---
    fig, ax = plt.subplots(figsize=(7, 7))

    # Group by trajectory and plot each as a continuous line in ID order.
    # Sorting by pose_id ensures lines follow the acquisition order within each trajectory.
    for idx, (traj, grp) in enumerate(sorted(data.groupby("traj"), key=lambda kv: kv[0])):
        grp = grp.sort_values("pose_id")
        color = MATLAB_COLORS[idx % len(MATLAB_COLORS)]
        # Plot a solid line for each trajectory with a consistent width.
        ax.plot(grp["x"].values, grp["y"].values, '-', linewidth=1.6, color=color, label=f"Trajectory {traj}")

    # Equal aspect ratio for true XY geometry
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("Top-View Trajectories (XY)")
    ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.6)

    if not no_legend:
        ax.legend(title="Trajectories", frameon=True)

    # Save as SVG
    fig.tight_layout()
    fig.savefig(output_path, format="svg")
    plt.close(fig)

    print(f"Saved SVG to: {output_path.resolve()}")

if __name__ == "__main__":

    input_csv = "/home/miguelangel/oxford-lab/labrobotics/nerf-logs/2025-08-14-wytham/sapling-03/raw/slam_poses_robotics.csv"
    output_svg = "/home/miguelangel/oxford-lab/labrobotics/nerf-logs/2025-08-14-wytham/sapling-03/raw/slam_poses_robotics.svg"
    delimiter = ","
    no_legend = False

    plot_topview_from_slam(input_csv, output_svg, delimiter, no_legend)

#!/usr/bin/env python3
"""
Plot top-view (XY plane) trajectory from a SLAM poses CSV.

The CSV is expected to have a header row (first line) and at least 6 columns.
Columns are 1-indexed in the problem statement:
- Column 4: x coordinate
- Column 5: y coordinate
- Column 6: z coordinate (not used here)

This script plots a continuous red line for the XY trajectory and saves an SVG.
"""

import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

def main():
    parser = argparse.ArgumentParser(description="Plot top-view XY trajectory from a SLAM pose CSV and save as SVG.")
    parser.add_argument("input_csv", nargs="?", default="slam_poses.csv",
                        help="Path to the input CSV file (default: slam_poses.csv)")
    parser.add_argument("-o", "--output", default="trajectory_top_view.svg",
                        help="Output SVG filename (default: trajectory_top_view.svg)")
    parser.add_argument("--delimiter", default=",",
                        help="CSV delimiter (default: ',')")
    args = parser.parse_args()

    input_path = Path(args.input_csv)
    output_path = Path(args.output)

    # --- Read CSV ---
    # The first line is a header; pandas will treat it as column names by default.
    # We don't rely on column names, only positions (4th and 5th columns, 1-indexed).
    # If the CSV has extra spaces, engine='python' with skipinitialspace can help.
    df = pd.read_csv(input_path, delimiter=args.delimiter, header=0, engine="python", skipinitialspace=True)

    # --- Extract XY columns by position ---
    # 1-indexed columns 4 and 5 correspond to zero-based indices 3 and 4.
    if df.shape[1] < 5:
        raise ValueError("The CSV must have at least 5 columns to extract X (col 4) and Y (col 5).")

    x = df.iloc[:, 3]
    y = df.iloc[:, 4]

    # --- Plot ---
    fig, ax = plt.subplots(figsize=(6, 6))
    # Plot a continuous red line for the trajectory.
    # Using '-' for solid line style and setting the color explicitly to red.
    ax.plot(x, y, '-', color='red', linewidth=1.5)

    # Equal aspect so that units are not distorted in XY.
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("Top-View Trajectory (XY)")
    ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.6)

    # Tight layout and save as SVG
    fig.tight_layout()
    fig.savefig(output_path, format="svg")
    plt.close(fig)

    print(f"Saved SVG to: {output_path.resolve()}")

if __name__ == "__main__":
    main()

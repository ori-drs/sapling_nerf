
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Export camera frustums from transforms.json into a PLY where:
- Cameras point "backwards" (i.e., along -Z) by default.
- Only the image-plane quad is colorized (separate color from side faces).

We build TWO meshes per frustum: one for the side faces (pyramid)
and one for the image plane (quad). They have separate vertex lists,
so vertex colors don't bleed between them in CloudCompare/Meshlab.

CLI:
  --forwards / --backwards (default: backwards)
  --plane-color r g b
  --side-color  r g b
  --depth and --scale as before
  --w2c if poses are world->camera
  --export-centers to also dump centers as PLY points
"""

import json
import argparse
from pathlib import Path
import numpy as np
import open3d as o3d


def load_intrinsics_and_poses(json_path):
    with open(json_path, "r") as f:
        data = json.load(f)
    fx, fy = float(data["fl_x"]), float(data["fl_y"])
    cx, cy = float(data["cx"]),  float(data["cy"])
    w, h  = int(data["w"]),      int(data["h"])
    poses = [np.array(fr["transform_matrix"], dtype=float) for fr in data["frames"]]
    return (fx, fy, cx, cy, w, h), poses


def build_frustum_meshes(K, wh, T_c2w, depth=0.5, backwards=True,
                         plane_color=(1.0, 0.2, 0.2),
                         side_color=(0.7, 0.7, 0.7)):
    """
    Returns (mesh_sides, mesh_plane, cam_center_world).
    - mesh_sides: 4 triangles forming the pyramid sides
    - mesh_plane: 2 triangles forming the image plane (colored)
    """
    fx, fy, cx, cy = K
    w, h = wh

    # Choose z sign so cameras "look" backwards (i.e., -Z) if requested
    z = -abs(depth) if backwards else abs(depth)

    # 4 pixel corners of the image plane
    corners_px = np.array([[0, 0],
                           [w, 0],
                           [w, h],
                           [0, h]], dtype=float)

    # Project pixel corners to camera space at z
    corners_cam = []
    for u, v in corners_px:
        x = (u - cx) / fx * z
        y = (v - cy) / fy * z
        corners_cam.append([x, y, z, 1.0])
    corners_cam = np.stack(corners_cam, axis=0)  # (4,4)

    origin_cam = np.array([[0.0, 0.0, 0.0, 1.0]])  # (1,4)

    # Transform to world
    Pw = (T_c2w @ np.vstack([origin_cam, corners_cam]).T).T[:, :3]  # (5,3)
    O, C1, C2, C3, C4 = 0, 1, 2, 3, 4

    # --- Sides mesh (pyramid)
    # Keep triangles consistent; CC handles both windings, but we try to keep outward normals.
    tri_sides = np.array([
        [O, C2, C1],
        [O, C3, C2],
        [O, C4, C3],
        [O, C1, C4],
    ], dtype=np.int32)
    mesh_sides = o3d.geometry.TriangleMesh()
    mesh_sides.vertices = o3d.utility.Vector3dVector(Pw)
    mesh_sides.triangles = o3d.utility.Vector3iVector(tri_sides)
    mesh_sides.vertex_colors = o3d.utility.Vector3dVector(
        np.tile(np.asarray(side_color, float), (Pw.shape[0], 1))
    )
    mesh_sides.compute_vertex_normals()

    # --- Plane mesh (duplicate vertices so color is independent)
    Pw_plane = Pw.copy()
    tri_plane = np.array([
        [0, 1, 2],  # these indices refer to plane local vertices below
        [0, 2, 3],
    ], dtype=np.int32)

    # For the plane we need vertices C1..C4 only; duplicate so colors don't mix
    plane_vertices = np.vstack([Pw[C1], Pw[C2], Pw[C3], Pw[C4]])
    mesh_plane = o3d.geometry.TriangleMesh()
    mesh_plane.vertices = o3d.utility.Vector3dVector(plane_vertices)
    mesh_plane.triangles = o3d.utility.Vector3iVector(tri_plane)
    mesh_plane.vertex_colors = o3d.utility.Vector3dVector(
        np.tile(np.asarray(plane_color, float), (4, 1))
    )
    mesh_plane.compute_vertex_normals()

    cam_center = Pw[O]
    return mesh_sides, mesh_plane, cam_center


def main():
    ap = argparse.ArgumentParser(
        description="Export backward-looking camera frustums from transforms.json. Only the image-plane is colorized.")
    ap.add_argument("-t", "--transforms", type=str, default="transforms.json",
                    help="Path to transforms.json")
    ap.add_argument("-o", "--out", type=str, default="frustums_backwards.ply",
                    help="Output PLY filename")
    ap.add_argument("-d", "--depth", type=float, default=0.5,
                    help="Frustum depth magnitude (z is negative when --backwards).")
    ap.add_argument("-s", "--scale", type=float, default=1.0,
                    help="Uniform scale for each frustum (applied after building).")
    ap.add_argument("--plane-color", nargs=3, type=float, default=[1.0, 0.2, 0.2],
                    help="RGB (0..1) for the image plane.")
    ap.add_argument("--side-color", nargs=3, type=float, default=[0.7, 0.7, 0.7],
                    help="RGB (0..1) for the pyramid sides.")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--backwards", action="store_true", help="Make cameras point along -Z (default).")
    g.add_argument("--forwards",  action="store_true", help="Make cameras point along +Z.")
    ap.add_argument("--w2c", action="store_true",
                    help="If input poses are world->camera, invert them.")
    ap.add_argument("--export-centers", action="store_true",
                    help="Also export camera centers as centers.ply")
    args = ap.parse_args()

    K, poses = load_intrinsics_and_poses(args.transforms)
    fx, fy, cx, cy, W, H = K
    wh = (W, H)

    # Default to backwards if neither flag provided
    backwards = True if (not args.forwards) else False

    combined = o3d.geometry.TriangleMesh()
    centers = []

    for T in poses:
        T_use = np.linalg.inv(T) if args.w2c else T
        mesh_sides, mesh_plane, c = build_frustum_meshes(
            K=(fx, fy, cx, cy),
            wh=wh,
            T_c2w=T_use,
            depth=args.depth,
            backwards=backwards,
            plane_color=tuple(args.plane_color),
            side_color=tuple(args.side_color),
        )

        if args.scale != 1.0:
            mesh_sides.scale(args.scale, center=(0, 0, 0))
            mesh_plane.scale(args.scale, center=(0, 0, 0))

        combined += mesh_sides
        combined += mesh_plane
        centers.append(c)

    out_path = Path(args.out)
    o3d.io.write_triangle_mesh(str(out_path), combined, write_vertex_colors=True)
    print(f"[OK] Wrote frustums mesh (backwards={backwards}): {out_path.resolve()}")

    if args.export_centers and centers:
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(np.asarray(centers))
        pcd.colors = o3d.utility.Vector3dVector(np.tile([0.1, 0.8, 0.2], (len(centers), 1)))
        centers_path = out_path.with_name("centers.ply")
        o3d.io.write_point_cloud(str(centers_path), pcd, write_ascii=False)
        print(f"[OK] Wrote camera centers: {centers_path.resolve()}")


if __name__ == "__main__":
    main()

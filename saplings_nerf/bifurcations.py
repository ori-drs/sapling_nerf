from collections import Counter
from pathlib import Path
from typing import Tuple, List
from plyfile import PlyData

def _extract_edges_from_edge_element(edge_element) -> List[Tuple[int, int]]:
    """
    Extract edges from a PlyElement named 'edge'.
    Supports:
      - Two scalar properties: 'vertex1', 'vertex2'
      - A list property: 'vertex_indices' (typically length 2)
    """
    props = [p.name for p in edge_element.properties]
    edges: List[Tuple[int, int]] = []

    # Case 1: classic 'vertex1'/'vertex2' integer columns
    if 'vertex1' in props and 'vertex2' in props:
        v1 = edge_element.data['vertex1']
        v2 = edge_element.data['vertex2']
        edges = [(int(a), int(b)) for a, b in zip(v1, v2)]
        return edges

    # Case 2: 'vertex_indices' as a list (each row should contain exactly 2 indices)
    if 'vertex_indices' in props:
        for row in edge_element.data['vertex_indices']:
            pair = list(row)
            # Some exporters may store >2 indices; keep only valid 2-length edges
            if len(pair) == 2:
                edges.append((int(pair[0]), int(pair[1])))
        return edges

    raise ValueError("Unsupported 'edge' encoding: expected 'vertex1'/'vertex2' or 'vertex_indices'.")


def count_bifurcations_from_ply(ply_path: str) -> int:
    """
    Count the number of bifurcation nodes (nodes with degree >= 3)
    in a graph stored as a PLY file with an 'edge' element.

    Notes
    -----
    - Uses ply['edge'] directly (do NOT check membership on ply.elements).
    - Treats the graph as undirected.
    - Self-loops (u == v) are ignored for degree counting.
    """
    p = Path(ply_path)
    if not p.exists():
        raise FileNotFoundError(f"PLY file not found: {p}")

    ply = PlyData.read(str(p))

    # Correct way: access 'edge' via mapping-style API.
    try:
        edge_element = ply['edge']
    except KeyError:
        # Optional: include names present to help debugging
        available = [el.name for el in ply.elements]
        raise ValueError(f"The PLY file does not contain an 'edge' element. Available elements: {available}")

    edges = _extract_edges_from_edge_element(edge_element)
    if not edges:
        raise ValueError("No edges could be extracted from the PLY file.")

    # Compute node degrees
    degree = Counter()
    for u, v in edges:
        if u == v:
            continue  # ignore self-loops
        degree[u] += 1
        degree[v] += 1

    # Count nodes with degree >= 3
    return sum(1 for d in degree.values() if d >= 3)


# (Optional) If you also want the IDs of bifurcation nodes:
def bifurcation_nodes_from_ply(ply_path: str) -> List[int]:
    """
    Return the list of node IDs whose degree is >= 3.
    """
    p = Path(ply_path)
    if not p.exists():
        raise FileNotFoundError(f"PLY file not found: {p}")

    ply = PlyData.read(str(p))
    try:
        edge_element = ply['edge']
    except KeyError:
        available = [el.name for el in ply.elements]
        raise ValueError(f"The PLY file does not contain an 'edge' element. Available elements: {available}")

    edges = _extract_edges_from_edge_element(edge_element)
    if not edges:
        return []

    degree = Counter()
    for u, v in edges:
        if u == v:
            continue
        degree[u] += 1
        degree[v] += 1

    return [n for n, d in degree.items() if d >= 3]



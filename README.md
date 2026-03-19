# Sapling-NeRF Analysis Pipeline

This project contains a complete pipeline for structural analysis of sapling trees. It handles skeleton extraction, leaf segmentation, and density and topology analysis. To avoid repeating processes when not necessary, the pipeline is divided into steps, generating files with predefined names in between.

---

## 📁 Project Structure

```
saplings_nerf/               # Python module with analisys and segmentation functions
├── __init__.py
├── bifurcations.py
├── density_analysis.py
├── leaf_node_detection.py
├── leaf_region_segmentation.py
├── skeleton_extraction.py
config/
├── config.yaml              # Editable configuration file
main.py                      # Main execution script
requirements.txt             # Dependencies
setup.py                     # Package installer
```

---

## ▶️ Requirements

Recommended: Python 3.10

Install dependencies:
```bash
pip install -r requirements.txt
```

Or install as a local editable package:
```bash
pip install -e .
```

---

## ⚙️ Configuration

Edit the file `config/config.yaml` with your paths and parameters:

```yaml
input_folder: /path/to/your/input/pcd/
output_folder: /path/to/output/
input_file: 2025-07-11-tree-02.pcd
down_sample: 0.001         # Downsampling for skeleton extraction
radius: 0.008              # Radius for leaf region segmentation
```

---

## 🚀 Running the Pipeline

Once configured, run the pipeline with:

```bash
python main.py
```

---

## 📦 Output Files

The results will be automatically saved to the `output_folder` with names such as:

- `skeleton-<filename>.pcd`
- `topology-<filename>.ply`
- `leaf-nodes.pcd`
- `leaf-region-<filename>.pcd`
- `rest-region-<filename>.pcd`

---

## ✨ Credits

Built using `Open3D`, `pc-skeletor`, `networkx`, and `plyfile`.

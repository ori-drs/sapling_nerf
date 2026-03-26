# Sapling-NeRF Analysis Pipeline

This project contains a complete pipeline for structural analysis of sapling trees. It handles skeleton extraction, leaf segmentation, and density and topology analysis. To avoid repeating processes when not necessary, the pipeline is divided into steps, generating files with predefined names in between. 

We provide NeRF output [examples](https://drive.google.com/drive/folders/1IBCvfrhGg319DAw0-rJpB7IjInFra9oh?usp=sharing) to run this pipeline. Additionally, the dataset contains raw data and SfM-processed data to run your own NeRF/3DGS model.

---

## 📁 Project Structure

```
sapling_nerf/               # Python module with analisys and segmentation functions
├── __init__.py
├── bifurcations.py
├── density_analysis.py
├── leaf_node_detection.py
├── leaf_region_segmentation.py
├── skeleton_extraction.py
config/
├── config.yaml              # Editable configuration file
scripts/                     # Auxiliary scripts for data treatment
main.py                      # Main execution script
requirements.txt             # Dependencies
setup.py                     # Package installer
```

---

## 📁 Data Structure

```
sapling-xx/                              # Each data batch from sapling with id: xx is stored in a folder
├── processed/
    ├── input_nerf/                      # Input data used for NeRF training (3DGS will requiere points from SfM)
    ├── output_colmap/                   # Output from COLMAP + Umeyama alignment, using data from the "raw/" folder
    ├── output_nerf/                     # Examples of point clouds and videos generated from a NeRF model
├── raw/
    ├── images/cam1/                     # Camera images
    ├── images/cam1-full/                # Optional folder with high frequency images
    ├── slam_poses_robotics.csv          # Reference trajectory to scale and localise recostructions (from multi-session SLAM)
```

---

## ▶️ Requirements

Recommended: Python 3.10 in a Python environment

Environment configuration:
```bash
cd <path>/sapling_nerf/
python3.10 -m venv .venv
source .venv/bin/activate
```

Install as a local editable package:
```bash
pip install -e .
```

---

## ⚙️ Configuration

Edit the file `config/config.yaml` with your paths and parameters:

```yaml
input_folder: /path/to/your/input/pcd/
input_file: sapling-xx.pcd

output_folder: /path/to/output/

down_sample: 0.001      # Pc-skeletor parameter Downsampling for skeleton extraction: 
                        # 0.008 produce downsampling for accurate skeleton extraction
                        # 0.001 produce overskeletonisation (multiple terminal nodes in leaves) fo segmentation purposes
radius: 0.012           # Radius for leaf segmentation around terminal nodes

run_skeleton: true      # Flags to activate each step
run_leaf_nodes: true
run_leaf_region: true
run_density_plot: true
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
- `leaf-nodes-<filename>.pcd`
- `leaf-region-<filename>.pcd`
- `rest-region-<filename>.pcd`

`<filename>` is the value configured `input_file`.

---

## 📖 Citation
```bibtex
@article{munoz2026sapling,
  title={Sapling-NeRF: Geo-Localised Sapling Reconstruction in Forests for Ecological Monitoring},
  author={Mu{\~n}oz-Ba{\~n}{\'o}n, Miguel {\'A}ngel and Chebrolu, Nived and Moorthy, Sruthi M Krishna and Tao, Yifu and Torres, Fernando and Salguero-G{\'o}mez, Roberto and Fallon, Maurice},
  journal={arXiv preprint arXiv:2602.22731},
  year={2026}
}
```

---

## ✨ License and Credits

This work is licensed under a [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-nc-sa/4.0) and is intended for non-commercial academic use. If you are interested in using the dataset for commercial purposes please contact us via [email](mailto:miguelangel.munoz@ua.es).

Built using [pc-skeletor](https://github.com/meyerls/pc-skeletor) as core.
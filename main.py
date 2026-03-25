"""
Sapling-NeRF Analysis Pipeline
Author: Miguel Angel Munoz-Banon
Description: 
    Pipeline for structural analysis of sapling trees.
    It Handles skeleton extraction, leaf segmentation, and density and topology analysis. 
    To avoid repeating processes when not necessary, the pipeline is divided into steps, 
    generating files with conventional names in between.
"""

import yaml
import os
import sys
import logging
from datetime import datetime
from sapling_nerf.skeleton_extraction import extract_skeleton
from sapling_nerf.leaf_node_detection import detect_leaf_nodes
from sapling_nerf.leaf_region_segmentation import segment_leaf_region
from sapling_nerf.density_analysis import plot_leaf_density
from sapling_nerf.bifurcations import count_bifurcations_from_ply

class SaplingAnalysisPipeline:
    def __init__(self, config_path="config/config.yaml"):
        # Setup logging first
        self._setup_logging()
        
        # Load and validate configuration
        self.config = self._load_config(config_path)
        self._validate_initial_paths()
        
        # Mapping config to attributes 
        self.input_folder = self.config["input_folder"]
        self.output_folder = self.config["output_folder"]
        self.input_file = self.config["input_file"]
        self._file_names_convention()
        
        self.down_sample = self.config.get("down_sample", 0.001)
        self.radius = self.config.get("radius", 0.008)
        
        # Run flags 
        self.run_skeleton = self.config.get("run_skeleton", True)
        self.run_leaf_nodes = self.config.get("run_leaf_nodes", True)
        self.run_leaf_region = self.config.get("run_leaf_region", True)
        self.run_density_plot = self.config.get("run_density_plot", True)

    def _setup_logging(self):
        """Initializes logging to both console and a file."""
        log_format = "%(asctime)s [%(levelname)s] %(message)s"
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                # logging.FileHandler(f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
                logging.FileHandler(f"log.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _load_config(self, path):
        """Load YAML config with error handling."""
        if not os.path.exists(path):
            self.logger.error(f"Configuration file missing: {path}")
            sys.exit(1)
        with open(path, "r") as f:
            return yaml.safe_load(f)

    def _validate_initial_paths(self):
        """Verifies input existence before starting."""
        if not os.path.exists(self.config["output_folder"]):
            self.logger.info(f"Creating output directory: {self.config['output_folder']}")
            os.makedirs(self.config["output_folder"], exist_ok=True)
    
    def _file_names_convention(self):
        self.full_input_path = os.path.join(self.input_folder, self.input_file)
        self.topology_file = os.path.join(self.output_folder, f"topology-{self.input_file.replace('.pcd', '.ply')}")
        self.skeleton_file = os.path.join(self.output_folder, f"skeleton-{self.input_file.replace('.pcd', '.pcd')}") 
        pcd_base = self.input_file.replace('.pcd', '')
        self.leaf_nodes_file = os.path.join(self.output_folder, f"leaf-nodes-{pcd_base}.pcd")
        self.leaf_region_file = os.path.join(self.output_folder, f"leaf-region-{pcd_base}.pcd")
        self.rest_region_file = os.path.join(self.output_folder, f"rest-region-{pcd_base}.pcd")

    def _check_file_exists(self, filepath, step_name):
        """Helper to verify internal files exist before proceeding to next step."""
        if not os.path.exists(filepath):
            self.logger.error(f"[{step_name}] Expected file missing: {filepath}")
            self.logger.error(f"[{step_name}] Step skipped")
            return False
        return True

    def run(self):
        """Executes the analysis pipeline steps."""
        self.logger.info(f"Starting pipeline for: {self.input_file}")

        # Step 1: Skeleton Extraction 
        if self.run_skeleton and self._check_file_exists(self.full_input_path, "Skeleton-Topology Step"):
                self.logger.info("Extracting skeleton...")
                extract_skeleton(self.full_input_path, self.output_folder, self.skeleton_file, self.topology_file, self.down_sample)
            
        # Step 2: Leaf Node Detection 
        if self.run_leaf_nodes and self._check_file_exists(self.topology_file, "Leaf Node Step"):
                self.logger.info("Detecting leaf nodes...")
                detect_leaf_nodes(self.topology_file, self.leaf_nodes_file)

        # Step 3: Leaf Region Segmentation 
        if self.run_leaf_region and self._check_file_exists(self.leaf_nodes_file, "Leaf Segmentation Step"):
                self.logger.info("Segmenting leaf regions...")
                segment_leaf_region(self.full_input_path, self.leaf_nodes_file, self.leaf_region_file, self.rest_region_file, self.radius)

        # Step 4: Density Analysis 
        if self.run_density_plot and self._check_file_exists(self.leaf_region_file, "Density Step") and self._check_file_exists(self.topology_file, "Density Step"):
                self.logger.info("Generating density plots and counting bifurcations...")
                lwr = plot_leaf_density(self.leaf_region_file, self.rest_region_file, self.output_folder)
                self.logger.info(f"Leaf-Wood Ratio (LWR): {lwr}")
                n_bif = count_bifurcations_from_ply(self.topology_file)
                self.logger.info(f"Bifurcation count: {n_bif}")

        self.logger.info("Pipeline execution finished successfully.")

if __name__ == "__main__":
    sapling_nerf = SaplingAnalysisPipeline()
    sapling_nerf.run()
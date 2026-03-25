import subprocess
import sys
from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop

def install_legacy_deps():
    """Installs conflicting legacy dependencies before the main process."""
    print("--- Installing legacy dependencies (NumPy, Wheel, Mistree) ---")
    # 1. Ensure basic build tools are present
    subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy<1.24,>=1.23", "wheel"])
    
    # 2. Downgrade setuptools to compile mistree successfully
    subprocess.check_call([sys.executable, "-m", "pip", "install", "setuptools<60.0"])
    
    # 3. Install mistree without build isolation (using the NumPy version just installed)
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-build-isolation", "mistree==1.2.0"])
    
    # 4. Restore setuptools to a modern version for the rest of the setup process
    subprocess.check_call([sys.executable, "-m", "pip", "install", "setuptools>=65"])

class CustomDevelop(develop):
    def run(self):
        install_legacy_deps()
        develop.run(self)

class CustomInstall(install):
    def run(self):
        install_legacy_deps()
        install.run(self)

# Load requirements from file 
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="sapling_nerf",
    version="1.0.0",
    packages=find_packages(),
    install_requires=requirements,
    author="Miguel Angel Munoz-Banon",
    description="Segmentation pipeline for sapling tree skeletons and foliage",
    python_requires=">=3.10",
    cmdclass={
        'develop': CustomDevelop,
        'install': CustomInstall,
    },
)
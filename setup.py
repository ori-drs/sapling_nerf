from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="saplings-nerf",
    version="0.1.0",
    packages=find_packages(),
    install_requires=requirements,
    author="Miguel A. Munoz-Banon",
    description="Segmentation pipeline for sapling tree skeletons and foliage",
    python_requires=">=3.10",
)

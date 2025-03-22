"""Setup script for the hydrograph-seatek-analysis package."""

from setuptools import setup, find_packages

setup(
    name="hydrograph-seatek-analysis",
    version="1.0.0",
    description="Analysis of hydrograph and Seatek sensor data for river morphology studies",
    author="Abhi Mehrotra",
    author_email="abhimhrtr@pm.me",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.5.0",
        "matplotlib>=3.5.0",
        "seaborn>=0.11.0",
        "openpyxl>=3.0.0",
        "numpy>=1.21.0",
        "colorlog>=6.7.0",
        "pyyaml>=6.0.0",
    ],
    entry_points={
        "console_scripts": [
            "seatek-processor=src.hydrograph_seatek_analysis.app:main",
            "validate-data=validate_data:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Hydrology",
    ],
)
#!/usr/bin/env python3
"""
Setup script for PS & DS System Monitor
"""

from setuptools import setup, find_packages
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ps-ds-monitor",
    version="1.0.0",
    author="Adam Grange",
    author_email="adamgrange@proton.me",
    description="Cross-platform process and system status monitoring tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ps-ds-monitor",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "mypy>=0.812",
        ],
    },
    entry_points={
        "console_scripts": [
            "ps-ds-monitor=ps_ds_monitor:main",
        ],
    },
    keywords="process monitor system status ps unix cross-platform",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/ps-ds-monitor/issues",
        "Source": "https://github.com/yourusername/ps-ds-monitor",
        "Documentation": "https://github.com/yourusername/ps-ds-monitor#readme",
    },
)
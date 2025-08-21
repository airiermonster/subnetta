#!/usr/bin/env python3
"""
Setup script for Subnetta - IPv4 Subnetting Tool
"""

from setuptools import setup, find_packages
import os

# Read README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Subnetta - IPv4 Subnetting Tool"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="subnetta",
    version="1.0.0",
    author="Maximillian Urio",
    author_email="",
    description="A cross-platform IPv4 subnetting tool with interactive CLI",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/maximillian-urio/subnetta",
    py_modules=["subnetta"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Education",
        "Topic :: System :: Networking",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "subnetta=subnetta:main",
        ],
    },
    keywords=[
        "networking", "subnetting", "ipv4", "subnet", "calculator", 
        "cli", "network", "administration", "cidr", "subnet-mask"
    ],
    project_urls={
        "Bug Reports": "https://github.com/maximillian-urio/subnetta/issues",
        "Source": "https://github.com/maximillian-urio/subnetta",
    },
)
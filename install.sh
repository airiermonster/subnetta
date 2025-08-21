#!/bin/bash
# Subnetta Installation Script for Linux/Unix
# This script installs Subnetta globally on your system

echo ""
echo "================================================================"
echo "                 Subnetta Installer for Linux"
echo "================================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ using your package manager:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  CentOS/RHEL:   sudo yum install python3 python3-pip"
    echo "  Fedora:        sudo dnf install python3 python3-pip"
    echo "  Arch:          sudo pacman -S python python-pip"
    echo ""
    exit 1
fi

# Display Python version
echo "Detected Python version:"
python3 --version
echo ""

# Check Python version
echo "Checking Python version compatibility..."
python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" &> /dev/null
if [ $? -ne 0 ]; then
    echo "ERROR: Python 3.8 or higher is required"
    echo "Please upgrade your Python installation"
    echo ""
    exit 1
fi

echo "✓ Python version is compatible"
echo ""

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "ERROR: pip is not installed"
    echo "Please install pip using your package manager:"
    echo "  Ubuntu/Debian: sudo apt install python3-pip"
    echo "  CentOS/RHEL:   sudo yum install python3-pip"
    echo "  Fedora:        sudo dnf install python3-pip"
    echo "  Arch:          sudo pacman -S python-pip"
    echo ""
    exit 1
fi

# Install Subnetta
echo "Installing Subnetta..."
pip3 install -e . --user
if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Failed to install Subnetta"
    echo "Trying with sudo permissions..."
    sudo pip3 install -e .
    if [ $? -ne 0 ]; then
        echo "ERROR: Installation failed. Please check your pip installation and try again"
        echo ""
        exit 1
    fi
fi

echo ""
echo "================================================================"
echo "                 Installation Successful!"
echo "================================================================"
echo ""
echo "Subnetta has been installed successfully!"
echo ""
echo "To run Subnetta, simply type 'subnetta' in any terminal:"
echo "  subnetta"
echo ""
echo "If the command is not found, you may need to add the Python"
echo "user bin directory to your PATH:"
echo "  export PATH=\$PATH:\$HOME/.local/bin"
echo ""
echo "For help, use:"
echo "  subnetta --help"
echo ""
echo "Happy subnetting! 🌐"
echo ""
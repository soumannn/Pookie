#!/bin/bash

# Exit if any command fails
set -e

echo "Deactivating virtual environment if active..."
deactivate 2>/dev/null || echo "No active virtual environment found."

echo "Removing existing virtual environment..."
rm -rf venv

echo "Creating a new virtual environment with system site packages..."
python3 -m venv venv --system-site-packages

echo "Activating the virtual environment..."
source venv/bin/activate
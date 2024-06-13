#!/bin/bash

#Install first time python files.
# sudo apt-get install python3-pip python3.10-venv python3-tk

# Create a new virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies from requirements.txt file
pip install -r requirements.txt

# Run the python script
python3 ski_gpu_gui.py

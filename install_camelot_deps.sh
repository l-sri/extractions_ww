#!/bin/bash

# install other dependancies for camelot on ubuntu
sudo apt update && sudo apt upgrade
sudo apt install ghostscript python3-tk
sudo apt-get install libgl1-mesa-glx
pip install PyMuPDF

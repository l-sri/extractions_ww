#!/bin/bash

# install other dependancies for camelot/poppler/pdf2image on ubuntu
sudo apt-get install poppler-utils
sudo apt update && sudo apt upgrade
sudo apt install ghostscript python3-tk
sudo apt-get install libgl1-mesa-glx
pip install PyMuPDF

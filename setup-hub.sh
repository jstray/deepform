#!/bin/sh
sudo pip install pdfplumber
sudo apt-get update
sudo apt-get install libmagickwand-dev
sudo cp policy.xml /etc/ImageMagick-6/

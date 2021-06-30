#!/bin/bash
wget https://chromedriver.storage.googleapis.com/91.0.4472.19/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo chmod +x chromedriver
sudo mv chromedriver /usr/bin/
rm chromedriver_linux64.zip

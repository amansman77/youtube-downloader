#!/bin/bash

PYTHON_PATH="/mnt/c/Users/amans/AppData/Local/Programs/Python/Python312/python.exe"

echo "Downloading ffmpeg..."
wget -O ffmpeg.zip https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip
unzip -j ffmpeg.zip */bin/ffmpeg.exe
rm ffmpeg.zip

# ffmpeg.exe가 존재하는지 확인
if [ ! -f ffmpeg.exe ]; then
    echo "Error: ffmpeg.exe not found!"
    exit 1
fi
echo "ffmpeg.exe successfully extracted"

echo "Installing required packages..."
"$PYTHON_PATH" -m pip install --upgrade pip
"$PYTHON_PATH" -m pip install pyinstaller
"$PYTHON_PATH" -m pip install -r requirements.txt

echo "Creating Windows executable..."
"$PYTHON_PATH" -m PyInstaller --onefile --clean --add-data "ffmpeg.exe;." youtube_downloader.py

# spec 파일 확인
echo "Checking spec file for ffmpeg..."
cat youtube_downloader.spec

# dist 폴더의 내용물 확인
echo "Checking dist folder contents..."
ls -l dist/

echo "Cleaning up..."
rm ffmpeg.exe

echo "Build completed! The executable is in the dist folder." 
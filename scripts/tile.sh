#!/usr/bin/env bash

WORK_DIR=./montage_resized
rm -rf "$WORK_DIR"
mkdir -p "$WORK_DIR"
find . -maxdepth 1 -name "*.png" -exec convert -resize 50% {} "$WORK_DIR"/{} \;
montage -background '#000000' -geometry +1+1 "$WORK_DIR"/*.png montage.jpg

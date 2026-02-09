#!/bin/bash
# Helper script to run Demeter Docker Image with GUI support

IMAGE_NAME="ghcr.io/danielmf31/proyecto_demeter:latest"

echo "🚀 Pulling latest image..."
docker pull $IMAGE_NAME

echo "🎨 Granting X11 permissions..."
xhost +local:docker

echo "▶️ Running Demeter..."
docker run -it --rm \
  --net=host \
  --env="DISPLAY" \
  --volume="$HOME/.Xauthority:/root/.Xauthority:rw" \
  $IMAGE_NAME

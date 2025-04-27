#!/bin/bash

# Set your container and image names
container_name="lucent-server-fastapi"
image_name="lucent-server:latest"

# Remove any existing container
if docker ps -a --format '{{.Names}}' | grep -q "^${container_name}$"; then
    echo "Removing existing container..."
    docker rm -f ${container_name}
fi

# Build the image from your Dockerfile
echo "Building Docker image from Dockerfile..."
docker build -t ${image_name} .

# Create and start container
echo "Creating container..."
docker run -d --name ${container_name} \
    -p 8000:8000 \
    -v $(pwd):/app \
    ${image_name}

# Install dependencies inside the container
echo "Installing dependencies..."
docker exec ${container_name} pip install -r /app/requirements.txt

# Show running container
echo "Container started:"
docker ps --filter name=${container_name}

# Show logs
echo "Container logs (Ctrl+C to exit):"
docker logs -f ${container_name}
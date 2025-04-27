# Set your container and image names
$container_name = "lucent-server-fastapi"
$image_name = "lucent-server:latest"

# Remove any existing container
if (docker ps -a --format '{{.Names}}' | Select-String -Pattern "^${container_name}$") {
    Write-Host "Removing existing container..."
    docker rm -f ${container_name}
}

# Build the image from your Dockerfile
Write-Host "Building Docker image from Dockerfile..."
docker build -t ${image_name} .

# Create and start container
Write-Host "Creating container..."
docker run -d --name ${container_name} `
    -p 8000:8000 `
    -v "${PWD}:/app" `
    ${image_name}

# Show running container
Write-Host "Container started:"
docker ps --filter name=${container_name}

# Show logs
Write-Host "Container logs (Ctrl+C to exit):"
docker logs -f ${container_name}
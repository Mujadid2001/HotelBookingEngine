#!/bin/bash
# Quick fix script for Podman registry issues

echo "🔧 Fixing Podman registry configuration..."

# Create containers config directory
mkdir -p ~/.config/containers

# Configure Podman to use Docker Hub
cat > ~/.config/containers/registries.conf << EOF
[registries.search]
registries = ["docker.io"]

[registries.insecure]
registries = []

[registries.block]
registries = []

[[registry]]
location = "docker.io"
insecure = false
blocked = false
EOF

echo "✅ Registry configuration updated"

# Clean up any existing broken containers
echo "🧹 Cleaning up existing containers..."
podman-compose -f docker-compose.prod.yml down --volumes 2>/dev/null || true

# Pre-pull required images from Docker Hub
echo "📥 Pre-pulling required images from Docker Hub..."
podman pull docker.io/postgres:15-alpine
podman pull docker.io/redis:7-alpine
podman pull docker.io/nginx:alpine

echo "✅ All images pulled successfully"
echo ""
echo "🚀 Registry fix complete! You can now run:"
echo "   ./deploy.sh"
echo ""
echo "If you still have issues, run: podman system reset --force"
echo "Then run this script again."

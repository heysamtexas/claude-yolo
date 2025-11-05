#!/bin/bash
# Post-build hook
# This script runs after docker build
#
# Use cases:
# - Tag images for registries
# - Push to container registry
# - Run image security scans
# - Send notifications

set -e

echo "Running post-build hook..."

# Add your custom post-build logic here
# Example: docker tag $IMAGE_NAME myregistry/myimage:latest

echo "Post-build hook completed successfully"

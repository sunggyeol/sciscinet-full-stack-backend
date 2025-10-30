#!/bin/bash
# Script to install and start Redis on Ubuntu/Debian

echo "Installing Redis..."
sudo apt-get update
sudo apt-get install -y redis-server

echo "Starting Redis service..."
sudo systemctl start redis-server
sudo systemctl enable redis-server

echo "Testing Redis connection..."
redis-cli ping

echo "Redis setup complete!"
echo "If you see 'PONG' above, Redis is ready to use."

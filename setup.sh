#!/bin/bash

# Exit on error
set -e

echo "Setting up WSL environment..."

# Update package lists
echo "Updating package lists..."
sudo apt-get update

# Install MongoDB
echo "Installing MongoDB..."
sudo apt-get install -y gnupg curl
curl -fsSL https://pgp.mongodb.com/server-7.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg \
   --dearmor
echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] http://repo.mongodb.org/apt/debian bookworm/mongodb-org/7.0 main" | \
   sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org

# Start MongoDB service
echo "Starting MongoDB service..."
sudo systemctl start mongod || {
    echo "Failed to start MongoDB with systemctl, trying to create data directory and start manually..."
    sudo mkdir -p /data/db
    sudo chmod 777 /data/db
    mongod --fork --logpath /var/log/mongodb.log
}

# Wait for MongoDB to start
echo "Waiting for MongoDB to start..."
sleep 5

# Install essential packages
echo "Installing essential packages..."
sudo apt-get install -y \
    python3-full \
    python3-venv \
    python3-pip \
    python3-dev \
    build-essential \
    python3-setuptools \
    python3-wheel \
    pipx \
    curl

# Ensure pipx is on PATH
export PATH="$PATH:$HOME/.local/bin"

# Create a directory in WSL filesystem for the virtual environment
VENV_PATH="$HOME/.venvs/internship_portal_venv"
PROJECT_VENV=".venv_linux"

# Remove existing venv if it exists
if [ -d "$VENV_PATH" ]; then
    echo "Removing existing virtual environment..."
    rm -rf "$VENV_PATH"
fi

if [ -d "$PROJECT_VENV" ]; then
    echo "Removing existing virtual environment link..."
    rm -rf "$PROJECT_VENV"
fi

# Create new virtual environment without pip in WSL filesystem
echo "Creating new virtual environment..."
mkdir -p "$HOME/.venvs"
python3 -m venv "$VENV_PATH" --without-pip

# Create symbolic link in project directory
ln -s "$VENV_PATH" "$PROJECT_VENV"

# Activate the virtual environment
echo "Activating virtual environment..."
. "$VENV_PATH/bin/activate"

# Bootstrap pip in the virtual environment
echo "Installing pip in virtual environment..."
curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py --force-reinstall
rm get-pip.py

# Install dependencies in the virtual environment
echo "Installing dependencies..."
# Using the virtual environment's pip directly
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Initialize the database
echo "Initializing database..."
if [ -f "scripts/initialize_db.py" ]; then
    python scripts/initialize_db.py
fi

# Start gunicorn
echo "Starting gunicorn server..."
echo "You can access the application at http://localhost:10000"
echo "Press Ctrl+C to stop the server"
"$VENV_PATH/bin/gunicorn" wsgi:application --bind 0.0.0.0:10000 --reload

# Create upload directories
mkdir -p /opt/render/project/src/app/uploads/announcements
mkdir -p /opt/render/project/src/app/uploads/certifications
mkdir -p /opt/render/project/src/app/uploads/cv

# Set permissions
chmod -R 755 /opt/render/project/src/app/uploads 
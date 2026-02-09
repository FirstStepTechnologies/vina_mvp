#!/bin/bash
# Initialize Render persistent disk with data from Git

DISK_PATH="/opt/render/project/src/data"
GIT_DATA_PATH="/opt/render/project/src_backup/data"

# Check if disk is empty (no vina.db or vina.db is very small)
if [ ! -f "$DISK_PATH/vina.db" ] || [ $(stat -f%z "$DISK_PATH/vina.db" 2>/dev/null || echo 0) -lt 1000000 ]; then
    echo "🔄 Initializing persistent disk with data from Git..."
    
    # Copy data directory before disk mount shadows it
    # We need to copy from the build directory
    if [ -d "/opt/render/project/src/data" ]; then
        # Temporarily move mounted disk content
        mkdir -p /tmp/render_data_backup
        cp -r $DISK_PATH/* /tmp/render_data_backup/ 2>/dev/null || true
        
        # Copy from git (this won't work because disk is already mounted)
        # We need a different approach
        echo "⚠️  Disk already mounted. Please use manual copy method."
    fi
else
    echo "✅ Database already exists on disk ($(stat -f%z "$DISK_PATH/vina.db" 2>/dev/null || echo 0) bytes)"
fi

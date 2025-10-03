#!/bin/bash

# Script: clean-node-modules.sh
# Purpose: Delete all node_modules folders recursively
# Usage: Run from the project root with: ./clean-node-modules.sh

echo "Searching for node_modules folders..."

# Find all node_modules directories (ignores symlinks) and remove them
find . -type d -name "node_modules" -prune -print | while read dir; do
    echo "Deleting: $dir"
    rm -rf "$dir"
done

echo "Cleanup complete."

#!/bin/bash

# Create target directory
mkdir -p .docs-content/docs

# Copy all files and directories from parent, excluding config/
for item in ../*; do
    if [[ "$(basename "$item")" != "config" ]]; then
        cp -r "$item" .docs-content/docs/
    fi
done

# Copy examples
cp -r ../../examples .docs-content/
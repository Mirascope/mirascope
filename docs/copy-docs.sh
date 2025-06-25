#!/bin/bash

# Create target directory
mkdir -p .docs-content/docs
mkdir -p .docs-content/typescript/examples

# Copy docs content
cp -r content/* .docs-content/docs/

# Copy examples
cp -r ../examples .docs-content/

# Copy TypeScript examples excluding specific files/directories
for item in ../typescript/examples/*; do
    basename_item="$(basename "$item")"
    case "$basename_item" in
        node_modules|bun.lock|package.json|tsconfig.json)
            # Skip these items
            ;;
        *)
            cp -r "$item" .docs-content/typescript/examples/
            ;;
    esac
done


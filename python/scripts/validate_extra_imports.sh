#!/bin/bash
# Validate that EXTRA_IMPORTS in _stubs.py matches what would be generated

set -e

GENERATED=$(uv run python scripts/generate_extra_imports.py)

# Extract the JSON representation from _stubs.py
CURRENT=$(python -c "
import sys
sys.path.insert(0, 'mirascope')
from _stubs import EXTRA_IMPORTS
import json
print(json.dumps(EXTRA_IMPORTS, indent=2))
")

if [ "$GENERATED" = "$CURRENT" ]; then
    exit 0
else
    echo "✗ EXTRA_IMPORTS is out of sync"
    echo ""
    echo "Generated:"
    echo "$GENERATED"
    echo ""
    echo "Current:"
    echo "$CURRENT"
    echo ""
    echo "To fix, run: uv run python scripts/generate_extra_imports.py --overwrite"
    exit 1
fi

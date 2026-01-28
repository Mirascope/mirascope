#!/usr/bin/env bash

# validate-snippets.sh
# Validates Python code snippets in .extracted-snippets/
# Runs both type checking (pyright) and style checking (ruff)
# Uses uv for dependency management

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Parse arguments
VERBOSE=false
SPECIFIC_PATH=""

for arg in "$@"; do
  case $arg in
    --verbose)
      VERBOSE=true
      shift
      ;;
    --path=*)
      SPECIFIC_PATH="${arg#*=}"
      shift
      ;;
    --help)
      echo "Usage: $0 [options]"
      echo ""
      echo "Options:"
      echo "  --verbose        Show more detailed output including uv and tool logs"
      echo "  --path=<path>    Check only a specific file or directory (relative to cloud/)"
      echo "  --help           Show this help message"
      echo ""
      echo "Examples:"
      echo "  $0                                           # Validate all snippets"
      echo "  $0 --path=.extracted-snippets/blog/my-post/  # Validate specific post"
      echo "  $0 --verbose                                 # Show detailed output"
      exit 0
      ;;
  esac
done

# Function to log with timestamp and color
log() {
  local color=$1
  local message=$2
  echo -e "${color}[$(date +'%Y-%m-%d %H:%M:%S')] ${message}${NC}"
}

# Function to verify if a command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Check if uv is installed
if ! command_exists uv; then
  log $RED "Error: 'uv' is not installed. Please install it first: https://github.com/astral-sh/uv"
  exit 1
fi

# Change to python directory for uv commands
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLOUD_DIR="$(dirname "$SCRIPT_DIR")"
REPO_ROOT="$(dirname "$CLOUD_DIR")"
PYTHON_DIR="$REPO_ROOT/python"

# Determine target path
if [ -n "$SPECIFIC_PATH" ]; then
  # Resolve path relative to cloud directory
  if [[ "$SPECIFIC_PATH" = /* ]]; then
    TARGET_PATH="$SPECIFIC_PATH"
  else
    TARGET_PATH="$CLOUD_DIR/$SPECIFIC_PATH"
  fi

  if [ ! -f "$TARGET_PATH" ] && [ ! -d "$TARGET_PATH" ]; then
    log $RED "Error: The specified path '$SPECIFIC_PATH' does not exist."
    exit 1
  fi
  log $YELLOW "Checking only path: $SPECIFIC_PATH"
else
  TARGET_PATH="$CLOUD_DIR/.extracted-snippets"
  if [ ! -d "$TARGET_PATH" ]; then
    log $RED "Error: No .extracted-snippets directory found. Run 'bun run generate:snippets' first."
    exit 1
  fi
fi

# Count Python files to check
if [ -d "$TARGET_PATH" ]; then
  TOTAL_FILES=$(find "$TARGET_PATH" -name "*.py" | wc -l | tr -d ' ')
else
  TOTAL_FILES=1
fi

log $YELLOW "Found $TOTAL_FILES Python file(s) to validate"

if [ "$TOTAL_FILES" -eq 0 ]; then
  log $GREEN "No Python files found to validate"
  exit 0
fi

# Install dependencies with uv (from python directory)
log $YELLOW "Ensuring dependencies are installed..."
cd "$PYTHON_DIR"
if [ "$VERBOSE" = true ]; then
  uv sync
else
  uv sync > /dev/null 2>&1
fi
log $GREEN "Dependencies ready"

# Run pyright
log $YELLOW "Running pyright type checking..."
PYRIGHT_OK=true
TEMP_OUTPUT=$(mktemp)

cd "$PYTHON_DIR"
if uv run pyright "$TARGET_PATH" 2>&1 | tee "$TEMP_OUTPUT"; then
  log $GREEN "Type checking passed"
else
  # Count errors
  ERROR_COUNT=$(grep -c "error:" "$TEMP_OUTPUT" 2>/dev/null || echo "0")
  WARNING_COUNT=$(grep -c "warning:" "$TEMP_OUTPUT" 2>/dev/null || echo "0")

  log $RED "Type checking failed with $ERROR_COUNT error(s) and $WARNING_COUNT warning(s)"
  PYRIGHT_OK=false
fi
rm "$TEMP_OUTPUT"

# Run ruff
log $YELLOW "Running ruff code style checking..."
RUFF_OK=true

cd "$PYTHON_DIR"
if uv run ruff check "$TARGET_PATH"; then
  log $GREEN "Code style checking passed"
else
  log $RED "Code style checking failed"
  RUFF_OK=false
fi

# Final result
if [ "$PYRIGHT_OK" = true ] && [ "$RUFF_OK" = true ]; then
  log $GREEN "All checks passed"
  exit 0
else
  [ "$PYRIGHT_OK" = false ] && log $RED "Type checking failed"
  [ "$RUFF_OK" = false ] && log $RED "Code style checking failed"
  exit 1
fi

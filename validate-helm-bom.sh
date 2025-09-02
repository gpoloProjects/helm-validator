#!/bin/bash
# Helm Variable Reference Checker with BOM - Linux/macOS Shell Script
# Usage: ./validate-helm-bom.sh [bom-file] [values-file]
# Example: ./validate-helm-bom.sh ./example-bom.yaml ./values-dev.yaml

if [ $# -ne 2 ]; then
    echo "Usage: ./validate-helm-bom.sh [bom-file] [values-file]"
    echo "Example: ./validate-helm-bom.sh ./example-bom.yaml ./values-dev.yaml"
    echo ""
    echo "For single chart usage, use validate-helm.sh instead"
    exit 1
fi

BOM_FILE="$1"
VALUES_FILE="$2"

echo "Running Helm Variable Checker with BOM..."
echo "BOM File: $BOM_FILE"
echo "Values File: $VALUES_FILE"
echo ""

# Try python3 first, then python, then py (for Windows compatibility)
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
elif command -v py &> /dev/null; then
    PYTHON_CMD="py"
else
    echo "ERROR: No Python interpreter found. Please install Python."
    exit 1
fi

$PYTHON_CMD helm_variable_checker.py --bom-file "$BOM_FILE" --values-file "$VALUES_FILE"
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo "ERROR: Validation failed! Some variables are missing."
    exit $EXIT_CODE
else
    echo ""
    echo "SUCCESS: All variables validated!"
    exit 0
fi

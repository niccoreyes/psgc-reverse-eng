#!/bin/bash

# PSGC to FHIR Converter Script
# This script converts PSGC Excel data to FHIR JSON CodeSystem format
# aligned with the tx.fhirlab.net server format

set -e  # Exit immediately if a command exits with a non-zero status

# Colors for output formatting
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
INPUT_FILE="PSGC-3Q-2025-Publication-Datafile.xlsx"
OUTPUT_FILE="psgc_fhir_output.json"

# Check if Python environment is available
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python is not installed or not in PATH$NC" >&2
    exit 1
fi

# Determine which Python command to use
PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

# Check if the virtual environment exists and use it
VENV_PYTHON="./.venv/bin/python"
if [ -f "$VENV_PYTHON" ]; then
    PYTHON_CMD="$VENV_PYTHON"
fi

# Check if the converter script exists
if [ ! -f "psgc_fhir_converter.py" ]; then
    echo -e "${RED}Error: psgc_fhir_converter.py script not found in current directory$NC" >&2
    exit 1
fi

echo -e "${GREEN}PSGC to FHIR JSON CodeSystem Converter${NC}"
echo -e "${YELLOW}=====================================${NC}"
echo "Input file: $INPUT_FILE"
echo "Output file: $OUTPUT_FILE"
echo "Python command: $PYTHON_CMD"
echo ""

# Run the conversion
echo -e "${YELLOW}Starting conversion...$NC"
start_time=$(date +%s)
if $PYTHON_CMD psgc_fhir_converter.py --input "$INPUT_FILE" --output "$OUTPUT_FILE"; then
    end_time=$(date +%s)
    elapsed=$((end_time - start_time))
    echo ""
    echo -e "${GREEN}Conversion completed successfully!$NC"
    echo -e "${GREEN}Output saved to: $OUTPUT_FILE$NC"
    echo -e "${GREEN}Time elapsed: $elapsed seconds$NC"
    
    # Show basic information about the output
    if command -v jq &> /dev/null; then
        echo ""
        echo -e "${YELLOW}Output Summary:$NC"
        echo "File size: $(ls -lh "$OUTPUT_FILE" | awk '{print $5}')"
        echo "Entry count: $(jq '.count' "$OUTPUT_FILE" 2>/dev/null || echo 'N/A')"
        echo "Version: $(jq -r '.version' "$OUTPUT_FILE" 2>/dev/null || echo 'N/A')"
        echo "Status: $(jq -r '.status' "$OUTPUT_FILE" 2>/dev/null || echo 'N/A')"
    fi
else
    echo ""
    echo -e "${RED}Conversion failed!$NC"
    exit 1
fi
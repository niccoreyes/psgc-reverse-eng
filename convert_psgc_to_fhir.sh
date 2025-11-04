#!/bin/bash
# PSGC to FHIR Converter Script
# Converts Philippine Standard Geographic Code (PSGC) data to FHIR JSON CodeSystem format

# Default input and output file paths
DEFAULT_INPUT="PSGC-3Q-2025-Publication-Datafile.xlsx"
DEFAULT_OUTPUT="psgc_fhir_output.json"

# Check if python virtual environment is active, if not activate it
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Activating Python virtual environment..."
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        echo "Error: venv directory not found. Please create a virtual environment first."
        exit 1
    fi
fi

# Set input and output file paths based on command line arguments or use defaults
INPUT_FILE="${1:-$DEFAULT_INPUT}"
OUTPUT_FILE="${2:-$DEFAULT_OUTPUT}"

# Check if input file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo "Error: Input file '$INPUT_FILE' not found."
    exit 1
fi

echo "Starting PSGC to FHIR conversion..."
echo "Input file: $INPUT_FILE"
echo "Output file: $OUTPUT_FILE"

# Run the conversion
python psgc_fhir_converter.py --input "$INPUT_FILE" --output "$OUTPUT_FILE"

# Check if the conversion was successful
if [ $? -eq 0 ]; then
    echo "Conversion completed successfully!"
    echo "Output saved to: $OUTPUT_FILE"
    
    # Show basic information about the generated file
    if [ -f "$OUTPUT_FILE" ]; then
        echo "Output file size: $(wc -c < "$OUTPUT_FILE") bytes"
        echo "Number of lines in output: $(wc -l < "$OUTPUT_FILE")"
    fi
else
    echo "Error: Conversion failed!"
    exit 1
fi
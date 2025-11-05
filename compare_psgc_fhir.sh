#!/bin/bash

# Script to compare PSGC output with FHIRLab CodeSystem
# This script runs the validation comparing psgc_fhir_output.json and tx_fhirlab_codesystem.json

echo "Starting PSGC output vs FHIRLab CodeSystem validation..."

# Check if required files exist
if [ ! -f "/home/deck/Github/psgc-script/psgc_fhir_output.json" ]; then
    echo "Error: psgc_fhir_output.json not found!"
    exit 1
fi

if [ ! -f "/home/deck/Github/psgc-script/tx_fhirlab_codesystem.json" ]; then
    echo "Error: tx_fhirlab_codesystem.json not found!"
    exit 1
fi

# Run the validation script
python3 /home/deck/Github/psgc-script/validate_psgc_conformance.py \
    --fhir-codesystem /home/deck/Github/psgc-script/tx_fhirlab_codesystem.json \
    --psgc-output /home/deck/Github/psgc-script/psgc_fhir_output.json \
    --output validation_report_$(date +%Y%m%d_%H%M%S).txt

echo "Validation completed. Report saved with timestamp."
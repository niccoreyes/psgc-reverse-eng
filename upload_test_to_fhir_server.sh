#!/bin/bash

# Pre-upload script to modify PSGC FHIR CodeSystem for test environment
# Updates the ID, URLs, and other identifiers to avoid conflicts
# Default input file is psgc_fhir_output.json
# Default server URL is https://tx.fhirlab.net/fhir

set -e  # Exit immediately if a command exits with a non-zero status

# Default values
INPUT_FILE="psgc_fhir_output.json"
SERVER_URL="https://tx.fhirlab.net/fhir"
VALUESETS_DIR=""
DEFAULT_TEST_ID="test-PSGC"  # Fixed ID to always overwrite the same test version
TEST_ID="$DEFAULT_TEST_ID"
DEFAULT_URI="https://ontoserver.upmsilab.org/psgc"  # Original URI
TEMP_FILE="temp_psgc_test_output.json"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --input)
            INPUT_FILE="$2"
            shift 2
            ;;
        --server-url)
            SERVER_URL="$2"
            shift 2
            ;;
        --test-id)
            TEST_ID="$2"
            shift 2
            ;;
        --valuesets-dir)
            VALUESETS_DIR="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN="--dry-run"
            shift
            ;;
        --verbose|-v)
            VERBOSE="--verbose"
            shift
            ;;
        --help)
            echo "Usage: $0 [--input INPUT_FILE] [--server-url SERVER_URL] [--test-id TEST_ID] [--valuesets-dir DIR] [--dry-run] [--verbose|-v]"
            echo ""
            echo "Pre-upload script to modify PSGC FHIR CodeSystem for test environment"
            echo "Updates the ID, URLS, and other identifiers to avoid conflicts"
            echo ""
            echo "Options:"
            echo "  --input INPUT_FILE    Input FHIR CodeSystem JSON file (default: psgc_fhir_output.json)"
            echo "  --server-url SERVER_URL   FHIR server URL (default: https://tx.fhirlab.net/fhir)"
            echo "  --test-id TEST_ID     Test ID to use (default: test-PSGC - overwrites existing)"
            echo "  --valuesets-dir DIR   Directory with ValueSet-*.json files to upload after CodeSystem"
            echo "  --dry-run             Perform a dry run without actually uploading"
            echo "  --verbose, -v         Enable verbose logging"
            echo "  --help                Show this help message"
            echo ""
            echo "Environment variables:"
            echo "  FHIR_SERVER_API_KEY   API key for authentication (required)"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Check if API key is set and warn if not (only required for servers that need authentication)
if [ -z "$FHIR_SERVER_API_KEY" ]; then
    echo "Warning: FHIR_SERVER_API_KEY environment variable is not set"
    echo "This is OK if your FHIR server (e.g., tx.fhirlab.net) does not require authentication"
    echo "If your server requires authentication, set it: export FHIR_SERVER_API_KEY='your_api_key_here'"
fi

# Check if the input file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo "Error: Input file does not exist: $INPUT_FILE"
    echo "Please ensure the PSGC FHIR CodeSystem file exists."
    exit 1
fi

echo "Preparing test version of $INPUT_FILE to overwrite any existing test version..."
echo "Using fixed test ID: $TEST_ID (will overwrite existing test version)"
echo "Using original URI: $DEFAULT_URI (the upload script will append -test to make it unique)"

# Activate virtual environment if it exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

# Create a modified version with fixed identifiers
python -c "
import json
import sys

with open('$INPUT_FILE', 'r') as f:
    data = json.load(f)

data['id'] = '$TEST_ID'
data['name'] = 'PsgcTest'
data['title'] = '[TEST] PSGC'

with open('$TEMP_FILE', 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f'Prepared FHIR CodeSystem for test upload and saved to $TEMP_FILE')
"

echo "Upload test version with fixed ID to $SERVER_URL"

python upload_test_script.py \
    --input "$TEMP_FILE" \
    --server-url "$SERVER_URL" \
    --test-id "$TEST_ID" \
    ${VALUESETS_DIR:+--valuesets-dir "$VALUESETS_DIR"} \
    $DRY_RUN $VERBOSE

# Clean up temporary file
if [ -f "$TEMP_FILE" ] && [ -z "$DRY_RUN" ]; then
    rm "$TEMP_FILE"
    echo "Cleaned up temporary file: $TEMP_FILE"
fi

echo "Upload test completed (existing test version overwritten)."
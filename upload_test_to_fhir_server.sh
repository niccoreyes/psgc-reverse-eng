#!/bin/bash

# Upload PSGC FHIR CodeSystem to server with test ID
# Default input file is psgc_fhir_output.json
# Default server URL is https://tx.fhirlab.net/fhir

set -e  # Exit immediately if a command exits with a non-zero status

# Default values
INPUT_FILE="psgc_fhir_output.json"
SERVER_URL="https://tx.fhirlab.net/fhir"
TEST_ID="test-psgc-geographic-codes"

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
        --dry-run)
            DRY_RUN="--dry-run"
            shift
            ;;
        --verbose|-v)
            VERBOSE="--verbose"
            shift
            ;;
        --help)
            echo "Usage: $0 [--input INPUT_FILE] [--server-url SERVER_URL] [--test-id TEST_ID] [--dry-run] [--verbose|-v]"
            echo ""
            echo "Upload PSGC FHIR CodeSystem to server with test ID"
            echo ""
            echo "Options:"
            echo "  --input INPUT_FILE    Input FHIR JSON file (default: psgc_fhir_output.json)"
            echo "  --server-url SERVER_URL   FHIR server URL (default: https://tx.fhirlab.net/fhir)"
            echo "  --test-id TEST_ID     Test ID to use (default: test-psgc-geographic-codes)"
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

echo "Uploading $INPUT_FILE to $SERVER_URL with test ID: $TEST_ID"

# Activate virtual environment if it exists
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

# Run the Python upload test script
python upload_test_script.py \
    --input "$INPUT_FILE" \
    --server-url "$SERVER_URL" \
    --test-id "$TEST_ID" \
    $DRY_RUN $VERBOSE

echo "Upload test completed."
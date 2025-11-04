#!/bin/bash

# Undo/rollback uploaded PSGC FHIR CodeSystem from server
# Default server URL is https://tx.fhirlab.net/fhir

set -e  # Exit immediately if a command exits with a non-zero status

# Default values
SERVER_URL="https://tx.fhirlab.net/fhir"
CODESYSTEM_ID="psgc-geographic-codes"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --server-url)
            SERVER_URL="$2"
            shift 2
            ;;
        --codesystem-id)
            CODESYSTEM_ID="$2"
            shift 2
            ;;
        --no-prompt)
            NO_PROMPT="--no-prompt"
            shift
            ;;
        --verbose|-v)
            VERBOSE="--verbose"
            shift
            ;;
        --help)
            echo "Usage: $0 [--server-url SERVER_URL] [--codesystem-id CODESYSTEM_ID] [--no-prompt] [--verbose|-v]"
            echo ""
            echo "Undo/rollback uploaded PSGC FHIR CodeSystem from server"
            echo ""
            echo "Options:"
            echo "  --server-url SERVER_URL    FHIR server URL (default: https://tx.fhirlab.net/fhir)"
            echo "  --codesystem-id CODESYSTEM_ID   ID of the CodeSystem to delete (default: psgc-geographic-codes)"
            echo "  --no-prompt                Skip confirmation prompt (same as --confirm)"
            echo "  --verbose, -v              Enable verbose logging"
            echo "  --help                     Show this help message"
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

echo "Attempting to delete CodeSystem with ID: $CODESYSTEM_ID from $SERVER_URL"

# Activate virtual environment if it exists
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

# Run the Python undo script
python undo_script.py \
    --server-url "$SERVER_URL" \
    --codesystem-id "$CODESYSTEM_ID" \
    $NO_PROMPT $VERBOSE

echo "Undo operation completed."
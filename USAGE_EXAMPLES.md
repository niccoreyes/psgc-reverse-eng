# PSGC FHIR CodeSystem - Usage Examples

This document provides detailed examples for using the PSGC to FHIR CodeSystem converter and upload scripts.

## Basic Conversion

Convert PSGC Excel data to FHIR JSON CodeSystem:

```bash
python psgc_fhir_converter.py --input PSGC-3Q-2025-Publication-Datafile.xlsx --output psgc_fhir_output.json
```

## Upload Scripts Usage

### 1. Test Upload Script

Upload the CodeSystem with a test ID for safe testing purposes:

```bash
# Set your API key (only required if your FHIR server needs authentication)
export FHIR_SERVER_API_KEY="your_api_key_here"  # Skip this if tx.fhirlab.net doesn't need authentication

# Upload with test ID
python upload_test_script.py --input psgc_fhir_output.json --server-url https://tx.fhirlab.net/fhir --test-id test-psgc-geographic-codes
```

With dry-run mode (no actual upload, just validation):
```bash
python upload_test_script.py --input psgc_fhir_output.json --server-url https://tx.fhirlab.net/fhir --test-id test-psgc-geographic-codes --dry-run
```

With verbose logging:
```bash
python upload_test_script.py --input psgc_fhir_output.json --server-url https://tx.fhirlab.net/fhir --test-id test-psgc-geographic-codes --verbose
```

### 2. Production Upload Script

Upload the CodeSystem with the original ID for production use:

```bash
# Set your API key (only required if your FHIR server needs authentication)
export FHIR_SERVER_API_KEY="your_api_key_here"  # Skip this if tx.fhirlab.net doesn't need authentication

# Upload with original ID (with confirmation prompt)
python upload_production_script.py --input psgc_fhir_output.json --server-url https://tx.fhirlab.net/fhir

# Upload with original ID (skip confirmation prompt)
python upload_production_script.py --input psgc_fhir_output.json --server-url https://tx.fhirlab.net/fhir --confirm
```

With dry-run mode:
```bash
python upload_production_script.py --input psgc_fhir_output.json --server-url https://tx.fhirlab.net/fhir --dry-run
```

With verbose logging:
```bash
python upload_production_script.py --input psgc_fhir_output.json --server-url https://tx.fhirlab.net/fhir --confirm --verbose
```

### 3. Undo Script

Delete or rollback an uploaded CodeSystem:

```bash
# Set your API key (only required if your FHIR server needs authentication)
export FHIR_SERVER_API_KEY="your_api_key_here"  # Skip this if tx.fhirlab.net doesn't need authentication

# Delete a CodeSystem (with confirmation prompt)
python undo_script.py --server-url https://tx.fhirlab.net/fhir --codesystem-id psgc-geographic-codes

# Delete a CodeSystem (skip confirmation prompt)
python undo_script.py --server-url https://tx.fhirlab.net/fhir --codesystem-id psgc-geographic-codes --no-prompt
```

With verbose logging:
```bash
python undo_script.py --server-url https://tx.fhirlab.net/fhir --codesystem-id psgc-geographic-codes --no-prompt --verbose
```

## Mock FHIR Server for Local Testing

For testing without a real FHIR server, you can run the included mock server:

```bash
# Terminal 1: Start the mock server
python mock_fhir_server.py

# Terminal 2: Use the mock server in your upload scripts
export FHIR_SERVER_API_KEY="mock_key"
python upload_test_script.py --input test_codesystem.json --server-url http://localhost:8000/fhir --test-id test-psgc-codesystem-123
```

## Error Handling Examples

### Common Error Scenarios and Solutions

1. **Authentication Error**
   ```
   ValueError: FHIR_SERVER_API_KEY environment variable is not set
   ```
   Solution: Set the environment variable before running the script:
   ```bash
   export FHIR_SERVER_API_KEY="your_api_key_here"
   ```

2. **Network Error**
   ```
   Request error during upload: Connection refused
   ```
   Solution: Ensure the FHIR server is running and accessible at the specified URL.

3. **Validation Error**
   ```
   FHIR CodeSystem basic structure validation failed
   ```
   Solution: Ensure the input file contains a valid FHIR CodeSystem structure.

4. **File Not Found Error**
   ```
   File not found: psgc_fhir_output.json
   ```
   Solution: Ensure the specified input file exists and the path is correct.

## Complete Workflow Example

1. Convert PSGC Excel to FHIR CodeSystem:
   ```bash
   python psgc_fhir_converter.py --input PSGC-3Q-2025-Publication-Datafile.xlsx --output psgc_fhir_output.json
   ```

2. Test upload with dry-run:
   ```bash
   python upload_test_script.py --input psgc_fhir_output.json --server-url https://tx.fhirlab.net/fhir --test-id test-psgc-geographic-codes --dry-run
   ```

3. Perform actual test upload:
   ```bash
   export FHIR_SERVER_API_KEY="your_api_key_here"
   python upload_test_script.py --input psgc_fhir_output.json --server-url https://tx.fhirlab.net/fhir --test-id test-psgc-geographic-codes
   ```

4. If everything works correctly, upload to production:
   ```bash
   python upload_production_script.py --input psgc_fhir_output.json --server-url https://tx.fhirlab.net/fhir --confirm
   ```

5. If issues arise in production, rollback with the undo script:
   ```bash
   python undo_script.py --server-url https://tx.fhirlab.net/fhir --codesystem-id psgc-geographic-codes --no-prompt
   ```
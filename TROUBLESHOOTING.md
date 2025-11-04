# PSGC FHIR CodeSystem - Troubleshooting Guide

This document provides troubleshooting information for common issues with the PSGC to FHIR CodeSystem converter and upload scripts.

## Authentication Issues

### Problem: "FHIR_SERVER_API_KEY environment variable is not set"

**Symptoms:**
- Script exits with error: `ValueError: FHIR_SERVER_API_KEY environment variable is not set`

**Solution:**
The tx.fhirlab.net server may not require API keys for access. If the server doesn't require authentication, you can ignore this error or set a dummy value for compatibility with the scripts:
```bash
export FHIR_SERVER_API_KEY="dummy"  # Only if required by script but not server
```

Or if your own FHIR server requires authentication:
```bash
export FHIR_SERVER_API_KEY="your_api_key_here"
```

**Prevention:**
Check the server documentation to see if authentication is needed before running the scripts. If tx.fhirlab.net doesn't require authentication, you can run the scripts without setting the FHIR_SERVER_API_KEY variable.

## Network and Connection Issues

### Problem: Connection errors during upload

**Symptoms:**
- Script fails with connection timeouts
- Error messages like "Connection refused" or "Max retries exceeded"

**Solution:**
1. Verify the FHIR server URL is correct and accessible
2. Check network connectivity to the server
3. Ensure firewall rules allow the connection
4. Confirm the server is running and accepting requests

### Problem: SSL/TLS validation errors

**Symptoms:**
- SSL certificate validation errors
- "Certificate verify failed" messages

**Solution:**
Contact the server administrator to ensure proper SSL certificates are in place, or if appropriate for your environment, you can modify the script to disable SSL verification (not recommended for production).

## Validation Issues

### Problem: Invalid FHIR CodeSystem structure

**Symptoms:**
- Validation failure messages when uploading
- Errors about missing required fields like `resourceType`, `id`, `url`, etc.

**Solution:**
1. Ensure you're using the output from the PSGC converter script
2. Verify the input file is in proper FHIR CodeSystem format
3. Check that required fields are present and correctly formatted

### Problem: Invalid CodeSystem ID

**Symptoms:**
- Upload fails with validation errors
- Server rejection of the CodeSystem ID

**Solution:**
- Ensure the ID contains only valid characters (alphanumeric, hyphens, underscores)
- Test with a simple ID first before using complex ones
- For test uploads, use the `--test-id` parameter to specify a valid test ID

## Server Response Issues

### Problem: Server returns HTTP 409 (Conflict)

**Symptoms:**
- Upload fails with HTTP 409 error
- Message indicating resource already exists

**Solution:**
The production upload script should handle this automatically by updating existing resources. If this occurs with the test script, ensure you're using unique test IDs.

### Problem: Server returns HTTP 403 (Forbidden)

**Symptoms:**
- Upload fails with HTTP 403 error
- Access denied message

**Solution:**
1. Verify the API key has the necessary permissions
2. Check that the API key is valid and has not expired
3. Contact the server administrator to confirm your account has upload privileges

## Upload Script Specific Issues

### Problem: Production script prompts for confirmation repeatedly

**Symptoms:**
- Script keeps asking for confirmation even after answering

**Solution:**
Use the `--confirm` flag to bypass the interactive confirmation:
```bash
python upload_production_script.py --input psgc_fhir_output.json --server-url https://tx.fhirlab.net/fhir --confirm
```

### Problem: Undo script fails to delete resource

**Symptoms:**
- Undo script reports the resource doesn't exist
- Error messages about failed deletion

**Solution:**
1. Verify the resource ID is correct
2. Confirm the resource actually exists on the server
3. Check the server URL is correct
4. Ensure you have permissions to delete the resource

## Performance Issues

### Problem: Upload takes a very long time

**Symptoms:**
- Upload process hangs or takes longer than expected

**Solution:**
1. Check your network connection speed
2. Verify the server is responding normally
3. Consider that large CodeSystem files may take longer to process
4. Use the `--verbose` flag to track progress during upload

### Problem: High memory usage during operation

**Symptoms:**
- Script consumes too much memory
- System becomes unresponsive during execution

**Solution:**
The current implementation loads the entire file into memory. For extremely large files, consider modifying the script to process in chunks if your system has memory constraints.

## Testing Issues

### Problem: Mock server doesn't respond as expected

**Symptoms:**
- Test scripts fail when using the mock server
- Connection refused errors when using mock server

**Solution:**
1. Ensure the mock server is running: `python mock_fhir_server.py`
2. Use the correct URL format: `http://localhost:8000/fhir`
3. Set the API key to any value when using the mock server: `export FHIR_SERVER_API_KEY="mock_key"`

## Verification Steps

### To verify your upload worked:

1. Check the server response code (should be 200 or 201)
2. Access the CodeSystem via the server's API:
   ```
   GET /CodeSystem/{your_codesystem_id}
   ```
3. Verify the content matches what you uploaded

### To verify your deletion worked:

1. Check the server response code (should be 204 for successful deletion)
2. Try to access the CodeSystem via the server's API (should return 404)

## NaN (Not a Number) Value Issues

### Problem: "Out of range float values are not JSON compliant: nan"

**Symptoms:**
- Upload scripts fail with error: "Out of range float values are not JSON compliant: nan"
- Error occurs during JSON serialization of FHIR CodeSystem data
- Common when source data (from pandas DataFrames) contains missing numeric values

**Solution:**
The upload scripts now automatically handle NaN values by converting them to null during processing:
- NaN values in numeric fields are converted to null (None in Python)
- This happens automatically during upload processing
- No action required from user - the scripts handle this internally

**Explanation:**
The PSGC to FHIR converter uses pandas for data processing, which naturally represents missing numeric values as NaN (Not a Number). However, JSON specification does not support NaN values, causing serialization errors during upload. The fix ensures all NaN values are safely converted to null before JSON serialization.

## Additional Support

If you continue to experience issues:

1. Enable verbose logging with the `--verbose` flag for more detailed information
2. Check the server's status page or contact the administrator
3. Review the server's API documentation for any specific requirements or limitations
4. Consider testing with the included mock server to isolate client vs server issues
# Change: Upload FHIR Resources to tx.fhirlab.net Server

## Why
The current PSGC to FHIR JSON CodeSystem converter produces JSON output that needs to be uploaded to the tx.fhirlab.net FHIR terminology server for integration with healthcare systems. Currently, there are no scripts available to programmatically upload the generated CodeSystem to the server, which makes deployment and testing cumbersome and error-prone.

We need to develop a set of scripts to:
1. Upload the FHIR CodeSystem with a test ID for safe testing purposes
2. Upload the FHIR CodeSystem with the original ID for production use
3. Provide an undo mechanism to revert changes in case of issues

## What Changes
- Create a test upload script that uploads the FHIR CodeSystem with a test ID (e.g., test-psgc-geographic-codes)
- Create a production upload script that uploads with the original ID (e53319dd-2981-4b8d-8e50-d65dc27ebb2f)
- Create an undo script to rollback changes in case of problems
- Implement proper authentication and API interaction with the tx.fhirlab.net server
- Include validation and error handling for safe operations

## Impact
- Affected specs: New upload capabilities for FHIR resources
- Affected code: New Python scripts for server upload operations
- Infrastructure: Requires access to tx.fhirlab.net server with appropriate credentials
- Testing: Improved ability to test FHIR CodeSystem changes in a live environment
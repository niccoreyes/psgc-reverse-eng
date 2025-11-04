# Change: Fix NaN JSON Compliance in Upload Scripts

## Why
The upload scripts are failing when uploading FHIR CodeSystems that contain NaN (Not a Number) values. This occurs because pandas DataFrames may contain NaN values that are not JSON compliant, causing the upload process to fail with the error "Out of range float values are not JSON compliant: nan". This prevents successful uploads of PSGC FHIR CodeSystems to the FHIR server.

## What Changes
- Update the upload scripts to properly handle NaN values during JSON serialization
- Modify the deep copying mechanism in `modify_codesystem_for_test` function to use a NaN-safe approach
- Ensure all numeric values are properly handled during serialization
- Maintain data integrity while fixing the JSON compliance issue

## Impact
- Affected specs: Updated upload functionality to handle NaN values
- Affected code: upload_test_script.py, potentially other upload scripts
- Improved reliability: Uploads will succeed even when data contains NaN values
- Data integrity: All valid data will be preserved while NaN values are handled appropriately
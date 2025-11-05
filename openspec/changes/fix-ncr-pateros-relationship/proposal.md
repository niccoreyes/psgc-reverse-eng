# Change: Fix NCR-Pateros Parent-Child Relationship

## Why
The PSGC to FHIR converter has an incorrect parent-child relationship for Pateros (code: 1381701000). Currently, Pateros is placed under an intermediate parent code "1381700000" instead of being directly connected to the National Capital Region (NCR, code: 1300000000). This inconsistency affects the geographic hierarchy integrity in the FHIR CodeSystem, where Pateros should be treated similar to other cities directly under NCR, not as a municipality within a province.

## What Changes
- Update the `get_parent_code` function to identify and handle NCR-specific cases like Pateros
- Modify the parent calculation logic to return NCR (1300000000) as the parent for Pateros (1381701000)
- Add special handling for other potential similar cases in NCR
- Ensure the hierarchy properly reflects Pateros as a direct child of NCR

## Impact
- Affected code: psgc_fhir_converter.py in the `get_parent_code` function
- Improved data integrity: Pateros will have correct parent relationship to NCR
- Geographic hierarchy accuracy: Aligns with actual administrative structure of NCR
- FHIR CodeSystem correctness: Matches proper geographic relationship expectations
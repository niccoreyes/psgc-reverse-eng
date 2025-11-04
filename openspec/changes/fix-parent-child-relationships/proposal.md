# Change: Fix Parent-Child Relationship Issues in FHIR CodeSystem Upload

## Why
The FHIR CodeSystem uploads are failing due to parent-child relationship validation errors. The FHIR server reports errors like "Parent code not found: 1903617100", indicating that some concepts have parent references that don't exist in the CodeSystem data. This occurs because the PSGC hierarchy construction in the converter doesn't properly handle cases where:

1. A parent code referenced by a child concept doesn't exist in the dataset
2. The parent code calculation function returns codes that may not be present 
3. The hierarchy building logic doesn't validate that parent codes exist before creating relationships

This prevents successful uploads of PSGC FHIR CodeSystems to the FHIR server, breaking the hierarchical structure that is essential for geographic data representation.

## What Changes
- Update the `get_parent_code` function to cross-validate that calculated parent codes exist in the dataset
- Modify the hierarchy building logic to handle missing parent codes gracefully
- Add validation to ensure parent-child relationships are consistent before upload
- Update the concept conversion to either fix invalid relationships or exclude invalid parent properties

## Impact
- Affected code: psgc_fhir_converter.py, potentially validation functions
- Improved data integrity: All parent-child relationships will be valid in the output
- Successful uploads: No more "Parent code not found" errors during upload
- Preserved hierarchy: Valid geographic relationships will be maintained
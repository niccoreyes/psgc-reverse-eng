# Change: Add PSGC to FHIR JSON CodeSystem Converter

## Why
The project currently processes Philippine Standard Geographic Code (PSGC) data from Excel files but lacks a mechanism to convert this data into FHIR JSON CodeSystem format. This conversion is essential for integration with healthcare and clinical systems that use FHIR standards. The converter will enable the PSGC geographic codes to be represented in a format compatible with FHIR terminology resources.

## What Changes
- Add a new Python script to convert PSGC Excel data to FHIR JSON CodeSystem format
- Implement hierarchical representation of geographic codes (Region → Province/City → Municipality → Barangay) following the "part-of" relationship
- Maintain all properties from the current FHIR JSON CodeSystem structure
- Preserve versioning and metadata required for FHIR compliance
- **BREAKING**: The new conversion script will be the primary method for generating updated FHIR JSON CodeSystems

## Impact
- Affected specs: New data transformation capability required
- Affected code: New conversion script in the project
- New dependencies: Additional libraries for FHIR format generation (json, pandas, openpyxl)
- Integration point: Output will be compatible with FHIR terminology servers like tx.fhirlab.net/fhir
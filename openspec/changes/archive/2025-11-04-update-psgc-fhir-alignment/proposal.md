# Change: Update PSGC FHIR Alignment with tx.fhirlab.net Server

## Why
The current PSGC to FHIR JSON CodeSystem converter produces output that may not perfectly align with the format and structure of the FHIR CodeSystem available on the tx.fhirlab.net FHIR server. This change proposal aims to update our converter to match the version that will become the future version 2 of the FHIR CodeSystem currently available on the fhir ontoserver. Ensuring alignment with the authoritative source will improve compatibility with FHIR-based systems and maintain data consistency across platforms.

## What Changes
- Update the PSGC to FHIR JSON CodeSystem converter to match the structure and properties of the CodeSystem available at tx.fhirlab.net/fhir
- Maintain the same data content while ensuring the JSON structure, properties, and metadata match the server version
- Preserve the hierarchical relationships (Region → Province/City → Municipality → Barangay) with "part-of" meaning
- Update the CodeSystem properties to match: "Geographic Level" property with type "string"
- Ensure the resource structure matches the expected FHIR CodeSystem format
- **BREAKING**: The updated converter will produce JSON output that is structurally identical to the tx.fhirlab.net version

## Impact
- Affected specs: Updated FHIR JSON CodeSystem output format
- Affected code: PSGC to FHIR converter script (psgc_fhir_converter.py)
- Output compatibility: Improved alignment with FHIR terminology servers
- Data integrity: Maintained geographic code accuracy while improving FHIR compliance
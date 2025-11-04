## Context
The PSGC data currently exists in Excel format but needs to be transformed into FHIR JSON CodeSystem format that exactly matches the structure available on the tx.fhirlab.net FHIR server. This conversion requires parsing hierarchical geographic data and preserving relationships in the exact FHIR format used by the server.

## Goals / Non-Goals
- Goals: 
  - Convert PSGC Excel data to FHIR JSON CodeSystem format that matches tx.fhirlab.net server version
  - Preserve hierarchical geographic relationships exactly as represented on the server
  - Generate valid FHIR-compliant JSON matching the server's structure
  - Maintain all geographic codes, names, and properties from the source data
- Non-Goals:
  - Modify existing PSGC processing functionality beyond the output format
  - Implement changes to how data is read from Excel files
  - Make changes to the input data format or validation

## Decisions
- Decision: Update existing conversion logic to match the server's CodeSystem structure exactly
- Decision: Maintain the same data processing pipeline but modify output formatting
- Decision: Use native Python JSON library for consistent output generation
- Alternatives considered: Creating a completely new converter vs. updating existing one; updating existing was chosen to maintain code consistency

## Risks / Trade-offs
- Data integrity risk → Validate against original PSGC structure before conversion
- Compatibility risk → Ensure existing consumers of the JSON can handle changes
- Schema compliance → Validate against FHIR specification

## Migration Plan
- Steps: 1) Update conversion script to match server format 2) Test with current PSGC data 3) Validate output matches server structure 4) Update any dependent systems if needed

## Open Questions
- Should we maintain backward compatibility with current JSON format?
- Are there any specific FHIR server requirements that need to be considered?
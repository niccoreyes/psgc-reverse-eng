# Validate PSGC Output Against FHIR CodeSystem

## Change ID
validate-psgc-output-conformance

## Overview
Create a validation process to verify that the PSGC output conforms to the @tx_fhirlab_codesystem.json format and structure. This involves comparing the generated PSGC FHIR codesystem with the existing codesystem to identify discrepancies in codes, hierarchy relationships, and other structural elements.

## Motivation
The PSGC script generates updated geographic codes from the latest XLSX files, which should align with the existing FHIR codesystem structure. As we're using more updated PSGC codes from the XLSX files compared to the existing @tx_fhirlab_codesystem.json, we need to validate and identify where differences exist to ensure data integrity and compliance with FHIR standards.

## Goals
- Compare PSGC output with existing FHIR codesystem
- Identify codes that exist in one but not the other
- Identify hierarchy differences in parent-child relationships
- Report structural discrepancies
- Maintain compatibility with FHIR terminology server requirements

## Success Criteria
- Validation script successfully compares both files
- Comprehensive report of differences generated
- Both matching and non-matching elements clearly identified
- Performance optimized for large files (using efficient algorithms)
- Output is human-readable for manual verification
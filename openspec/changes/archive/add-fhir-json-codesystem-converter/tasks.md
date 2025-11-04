## 1. Implementation
- [ ] 1.1 Research FHIR JSON CodeSystem format specifications
- [ ] 1.2 Create Python script to read PSGC Excel file (PSGC tab)
- [ ] 1.3 Parse geographic hierarchy (Region → Province/City → Municipality → Barangay)
- [ ] 1.4 Map PSGC codes to FHIR JSON CodeSystem structure
- [ ] 1.5 Implement hierarchical relationships with "part-of" meaning
- [ ] 1.6 Add property for "Geographic Level" as specified
- [ ] 1.7 Generate proper metadata (id, version, URL, etc.)
- [ ] 1.8 Validate generated JSON against FHIR CodeSystem schema
- [ ] 1.9 Add command-line interface to specify input/output files
- [ ] 1.10 Write unit tests for conversion functionality
- [ ] 1.11 Document usage in README

## 2. Validation
- [ ] 2.1 Test with current PSGC-3Q-2025-Publication-Datafile.xlsx
- [ ] 2.2 Verify hierarchical relationships are preserved
- [ ] 2.3 Confirm generated JSON matches expected FHIR structure
- [ ] 2.4 Validate against FHIR terminology server requirements
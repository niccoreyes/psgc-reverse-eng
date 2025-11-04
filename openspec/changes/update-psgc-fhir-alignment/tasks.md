## 1. Analysis
- [ ] 1.1 Analyze the current FHIR CodeSystem structure from tx.fhirlab.net
- [ ] 1.2 Compare with current converter output format
- [ ] 1.3 Identify specific differences in structure and properties
- [ ] 1.4 Document required changes to align with server version

## 2. Implementation
- [ ] 2.1 Update the CodeSystem metadata fields to match server version
- [ ] 2.2 Modify the property definitions to match "Geographic Level" property
- [ ] 2.3 Ensure all concept entries include proper parent relationships
- [ ] 2.4 Preserve hierarchical relationships with "part-of" meaning
- [ ] 2.5 Update resourceType, id, url, version, name, title, and status fields
- [ ] 2.6 Ensure caseSensitive, valueSet, hierarchyMeaning, compositional, versionNeeded, and content fields match
- [ ] 2.7 Update all concepts to include proper display, definition, and property values
- [ ] 2.8 Verify parent-child relationships are properly defined for all geographic levels

## 3. Validation
- [ ] 3.1 Test updated converter with current PSGC Excel data
- [ ] 3.2 Verify output structure matches server version exactly
- [ ] 3.3 Validate hierarchical relationships are preserved
- [ ] 3.4 Ensure all geographic codes and names are correctly mapped
- [ ] 3.5 Run existing test suite to ensure no regressions
- [ ] 3.6 Validate against FHIR CodeSystem schema requirements
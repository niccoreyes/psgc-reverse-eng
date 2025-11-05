# Include Special Geographic Areas in Hierarchy

## Context
The current PSGC to FHIR conversion process excludes special geographic areas that were present in the old FHIR system. These special areas include codes like '1999900000' for "Special Geographic Area" which are present in the Excel source but not being properly handled due to NaN geographic levels.

## Problem
1. Special geographic areas (119 codes) exist in the official PSGC Excel source data
2. These codes are not being included in the FHIR output because they have NaN geographic levels
3. The old FHIR system had 2,024 codes that are now missing from the new system
4. This creates a gap in geographic coverage compared to the previous system

## Goals
- Include all special geographic areas in the converted FHIR CodeSystem
- Maintain backward compatibility with geographic codes from the old system
- Preserve the hierarchical structure for these special areas

## Success Criteria
- All special geographic areas in the Excel source appear in the output
- These areas are properly integrated into the geographic hierarchy
- Validation against FHIR terminology server passes
- No regression in existing functionality
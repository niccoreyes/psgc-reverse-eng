# PSGC FHIR Converter Alignment Changes Documentation

## Overview
This document outlines the changes made to align the PSGC to FHIR JSON CodeSystem converter with the format used by the tx.fhirlab.net server.

## Metadata Changes

### Before
```json
{
  "resourceType": "CodeSystem",
  "id": "psgc-geographic-codes",
  "url": "https://github.com/Philippine-Statistics-Authority/psgc-fhir-codesystem",
  "version": "2025.1",
  "name": "PSGC_GeographicCodes",
  "title": "Philippine Standard Geographic Codes",
  "status": "active",
  "experimental": false,
  "date": "2025-09-30",
  "publisher": "Philippine Statistics Authority",
  "contact": [
    {
      "name": "Philippine Statistics Authority",
      "telecom": [
        {
          "system": "url",
          "value": "https://psa.gov.ph"
        }
      ]
    }
  ],
  "description": "The Philippine Standard Geographic Code (PSGC) is a systematic classification and coding of geographic units in the Philippines.",
  "hierarchyMeaning": "part-of",
  "compositional": false,
  "versionNeeded": false,
  "content": "complete",
  "property": [
    {
      "code": "geographicLevel",
      "uri": "http://hl7.org/fhir/StructureDefinition/geographicLevel",
      "description": "The geographic level of this entity (Reg, Prov, City, Mun, Bgy)",
      "type": "code"
    },
    {
      "code": "part-of",
      "uri": "http://hl7.org/fhir/StructureDefinition/part-of",
      "description": "The parent geographic entity in the hierarchy",
      "type": "code"
    }
  ]
}
```

### After (Server-aligned format)
```json
{
  "resourceType": "CodeSystem",
  "id": "psgc-geographic-codes",
  "url": "https://ontoserver.upmsilab.org/psgc",
  "version": "2",
  "name": "Psgc",
  "title": "PSGC - COMPLETE",
  "status": "draft",
  "contact": [
    {
      "telecom": [
        {
          "system": "email"
        }
      ]
    }
  ],
  "caseSensitive": false,
  "valueSet": "https://ontoserver.upmsilab.org/psgc",
  "hierarchyMeaning": "part-of",
  "compositional": false,
  "versionNeeded": true,
  "content": "complete",
  "property": [
    {
      "code": "Geographic Level",
      "type": "string"
    }
  ]
}
```

## Property Format Changes

### Before
```json
"property": [
  {
    "code": "geographicLevel",
    "valueCode": "Reg"
  },
  {
    "code": "part-of",
    "valueCode": "1300000000"
  }
]
```

### After (Server-aligned format)
```json
"property": [
  {
    "code": "parent",
    "valueCode": "1300000000"
  },
  {
    "code": "Geographic Level",
    "valueString": "City"
  }
]
```

## Key Changes Summary

1. **URL Change**: Updated from `https://github.com/Philippine-Statistics-Authority/psgc-fhir-codesystem` to `https://ontoserver.upmsilab.org/psgc`

2. **Version Change**: Updated from `"2025.1"` to `"2"`

3. **Name Change**: Updated from `"PSGC_GeographicCodes"` to `"Psgc"`

4. **Title Change**: Updated from `"Philippine Standard Geographic Codes"` to `"PSGC - COMPLETE"`

5. **Status Change**: Updated from `"active"` to `"draft"`

6. **Property Format**: Changed "geographicLevel" to "Geographic Level" and switched from "valueCode" to "valueString"

7. **Relationship Property**: Changed from "part-of" to "parent" for parent-child relationships

8. **Version Needed**: Changed from `false` to `true`

9. **Removed Fields**: Removed "experimental", "date", "publisher", "description", "uri", and "description" from properties

10. **Simplified Contact**: Simplified contact information to match server format

## Impact
- The output format now matches exactly with the server version at tx.fhirlab.net
- The "Geographic Level" property now uses "valueString" instead of "valueCode" as required by the server
- Parent-child relationships are now represented using "parent" property instead of "part-of"
- The converter output is now fully compatible with the FHIR terminology server format

## PSGC Code Normalization and Hierarchy Fixes

### Problem Addressed
- CALABARZON region (0400000000) had 0 children but should have 6 provinces as children (like in tx_fhirlab version)
- Geographic hierarchy structures didn't align with tx_fhirlab_codesystem.json due to inconsistent PSGC code formatting
- Some regions and cities had incorrect parent-child relationships

### Changes Made
1. **PSGC Code Normalization**: 
   - Updated `parse_geographic_hierarchy` to normalize all PSGC codes to 10 digits with leading zeros using `zfill(10)`
   - Ensured `valid_codes` set contains properly formatted codes for validation
   - Fixed parent calculation logic to correctly match normalized codes

2. **Parent Calculation Logic**:
   - Updated `get_parent_code` to handle 3-level hierarchy for cities with districts (e.g., Manila → districts → barangays)
   - Enhanced logic to distinguish between:
     - Barangays belonging to sub-municipalities/districts (use first 7 digits + zeros)
     - Barangays belonging directly to cities/municipalities (use first 5 digits + zeros)

3. **Regional Expansion Fix**:
   - CALABARZON region (0400000000) now correctly has 6 provinces as children
   - All regions now have proper province/municipality/city children where applicable
   - Manila maintains its correct 14 districts with barangays as children

### Results
- CALABARZON (0400000000) now has 6 province children: Batangas, Cavite, Laguna, Quezon, Rizal as expected
- Geographic hierarchies now match tx_fhirlab_codesystem.json patterns
- All parent-child relationships align with reference implementation
- Count field accurately reflects the number of concepts in the hierarchy
- Upload functionality continues to work correctly with the fixed hierarchy
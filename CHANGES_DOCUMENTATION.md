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
## MODIFIED Requirements

### Requirement: FHIR JSON CodeSystem Structure Alignment
The system SHALL generate FHIR JSON CodeSystem output that exactly matches the structure and properties of the CodeSystem available on the tx.fhirlab.net FHIR server.

#### Scenario: Successful Server Alignment
- **WHEN** the conversion script is executed with valid PSGC Excel data
- **THEN** the generated JSON CodeSystem matches the server version structure exactly
- **AND** all metadata fields (resourceType, id, url, version, name, title, status) match the server format
- **AND** the properties match the server format (specifically "Geographic Level" property with type "string")

#### Scenario: Hierarchical Relationship Preservation
- **WHEN** PSGC codes are converted to FHIR CodeSystem format
- **THEN** the parent-child relationships (Region → Province/City → Municipality → Barangay) are preserved with "part-of" meaning
- **AND** each concept includes proper parent relationships as defined on the server

### Requirement: Geographic Level Property
The system SHALL include the "Geographic Level" property with type "string" in the CodeSystem properties, matching the server format.

#### Scenario: Property Inclusion
- **WHEN** the conversion process generates a CodeSystem
- **THEN** the "Geographic Level" property is defined in the properties array with type "string"
- **AND** each concept has appropriate "Geographic Level" values (Reg, Prov, City, Mun, Bgy, etc.)

### Requirement: FHIR CodeSystem Compliance
The system SHALL generate output that complies with FHIR CodeSystem standards and matches the server's implementation.

#### Scenario: CodeSystem Compliance
- **WHEN** the converter generates the JSON output
- **THEN** the resource includes all required FHIR CodeSystem fields
- **AND** the hierarchyMeaning is set to "part-of"
- **AND** caseSensitive is set to false
- **AND** compositional is set to false
- **AND** versionNeeded is set to true
- **AND** content is set to "complete"
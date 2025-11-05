## MODIFIED Requirements

### Requirement: PSGC to FHIR Hierarchy Construction
The system SHALL construct the geographic hierarchy based on the official PSGC code structure (positions 1-2=region, 3-5=province, 6-7=municipality/city, 8-10=barangay) with flexibility to handle skipped levels in the hierarchy.

#### Scenario: Standard hierarchy
- **WHEN** a barangay code exists with all parent levels present in the dataset
- **THEN** the system SHALL create the complete hierarchy (region -> province -> municipality -> barangay)

#### Scenario: Skipped hierarchy levels
- **WHEN** a sub-municipality code exists but the parent municipality is missing from the dataset
- **THEN** the system SHALL link the sub-municipality to the next most specific valid parent in the hierarchy (e.g., province or region)

#### Scenario: Special geographic areas
- **WHEN** processing special geographic areas like the City of Isabela that has administrative classification different from geographic location
- **THEN** the system SHALL correctly link to appropriate parent based on administrative classification as specified in official documentation

### Requirement: FHIR CodeSystem Property Preservation
The system SHALL preserve all original dataset properties (Income Classification, Urban/Rural, Population) in the FHIR output as properties.

#### Scenario: Income Classification property
- **WHEN** processing geographic entities with Income Classification data
- **THEN** the system SHALL include this data as a property in the FHIR concept

#### Scenario: Urban/Rural Classification property
- **WHEN** processing geographic entities with Urban/Rural Classification data
- **THEN** the system SHALL include this data as a property in the FHIR concept

#### Scenario: Population property
- **WHEN** processing geographic entities with Population data
- **THEN** the system SHALL include this data as a property in the FHIR concept

### Requirement: Special Case Reduction
The system SHALL reduce hardcoded special cases and instead use algorithmic determination based on PSGC code structure and published guidelines.

#### Scenario: Generalizable parent determination
- **WHEN** determining parent-child relationships
- **THEN** the system SHALL use PSGC code structure patterns rather than hardcoded code values

#### Scenario: Special geographic areas handling
- **WHEN** encountering special geographic areas like sub-municipalities in Manila
- **THEN** the system SHALL handle them based on official geographic level classifications rather than specific code exceptions
# Parent-Child Validation Specification

## Purpose
This specification defines requirements for validating parent-child relationships in PSGC FHIR CodeSystems to ensure all parent codes referenced by child concepts actually exist in the dataset. This prevents "Parent code not found" errors during FHIR server validation.

## Requirements

### Requirement: Valid Parent References
The system MUST ensure all parent codes referenced in concept properties exist in the CodeSystem dataset.

#### Scenario: Valid parent-child relationship
Given a FHIR CodeSystem with parent-child relationships
When the system validates parent references  
Then all parent codes referenced by child concepts must exist as concept codes in the dataset

#### Scenario: Invalid parent reference removal
Given a FHIR CodeSystem where a child concept references a parent code that doesn't exist
When the system processes the parent-child relationships
Then the invalid parent reference should be handled appropriately (either removed or substituted)

### Requirement: Hierarchy Preservation
The system MUST preserve valid geographic hierarchy relationships while fixing invalid ones.

#### Scenario: Hierarchy with missing parent
Given a geographic hierarchy where a mid-level parent code is missing from the dataset
When the system builds the hierarchy
Then it should appropriately connect children to valid ancestors or make them siblings of missing parent

#### Scenario: Data integrity after validation
Given a FHIR CodeSystem with potentially invalid parent-child relationships
When the system applies parent validation
Then the resulting hierarchy should maintain geographic meaning and prevent upload errors
# Include Special Geographic Areas in FHIR Hierarchy

## ADDED Requirements

### Requirement: Special Geographic Area Processing
The system MUST include special geographic areas from the official PSGC Excel source in the FHIR CodeSystem output, even if they have NaN geographic levels.

#### Scenario: Processing Special Geographic Areas
Given a PSGC Excel file containing entries with NaN geographic levels
When the conversion process runs
Then all entries with valid PSGC codes (including special geographic areas) MUST be included in the FHIR output

### Requirement: Default Geographic Level Assignment
For entries with NaN geographic levels, the system MUST assign a default geographic level (e.g., "Special") to enable proper processing and hierarchy creation.

#### Scenario: Handling NaN Geographic Levels
Given an entry with a NaN geographic level such as "Special Geographic Area" (1999900000)
When the conversion process reads this entry
Then the system MUST assign a default geographic level to allow processing

### Requirement: Hierarchical Integration
Special geographic areas MUST be properly integrated into the FHIR CodeSystem hierarchy with appropriate parent-child relationships.

#### Scenario: Special Area Hierarchy Integration
Given a special geographic area with a valid parent code
When the conversion process builds the hierarchy
Then the special area MUST be positioned correctly in the hierarchy relative to its parent

## MODIFIED Requirements

### Requirement: Geographic Level Property Validation
The system MUST handle cases where the geographic level property is missing or NaN by providing an appropriate default.

#### Scenario: Geographic Level Property with NaN Value
Given an entry with a NaN geographic level value
When the FHIR concept is created
Then the system MUST include a valid "Geographic Level" property with a default value
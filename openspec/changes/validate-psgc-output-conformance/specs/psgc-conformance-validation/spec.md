# PSGC Output Conformance Validation Specification

## Capability: PSGC-FHIR Conformance Validation

### ADDED: Code Comparison Capability
The system SHALL provide a validation mechanism to compare PSGC codes between the generated output and the existing FHIR codesystem.

#### Scenario: Validating Code Completeness
Given a PSGC output file and a reference FHIR codesystem file
When the validation process is executed
Then the system shall identify all codes present in one file but missing in the other
And the system shall generate statistics about code coverage

### ADDED: Hierarchy Validation Capability
The system SHALL validate parent-child relationships between geographic entities in both files.

#### Scenario: Validating Hierarchy Consistency
Given a PSGC output file and a reference FHIR codesystem file
When the validation process is executed
Then the system shall identify parent-child relationships that differ between the files
And the system shall report on geographic level assignment differences for matching codes

### ADDED: Validation Reporting Capability
The system SHALL generate comprehensive reports detailing the validation results.

#### Scenario: Generating Validation Report
Given validation results from code and hierarchy comparison
When the reporting function is executed
Then the system shall output a structured report containing:
- Summary statistics of matching and non-matching codes
- Detailed lists of discrepancies
- Quality metrics about data conformance

### ADDED: Large File Performance Capability
The system SHALL handle large JSON files efficiently without excessive memory consumption.

#### Scenario: Processing Large Files
Given a large PSGC output file (>20MB) and a large FHIR codesystem file
When the validation process is executed
Then the system shall process the files without running out of memory
And the process shall complete in reasonable time (less than 5 minutes for 20-30MB files)

### ADDED: Geographic Level Validation Capability
The system SHALL validate that geographic levels (Reg, Prov, City, Mun, Bgy) are consistent between files for matching codes.

#### Scenario: Validating Geographic Levels
Given a PSGC output file and a reference FHIR codesystem file
When the validation process is executed
Then the system shall compare geographic level assignments for codes present in both files
And the system shall report any discrepancies in geographic level assignments

### ADDED: Error Handling Capability
The system SHALL handle file loading errors and malformed data gracefully.

#### Scenario: Handling Missing Files
Given incorrect file paths for validation
When the validation process is executed
Then the system shall provide clear error messages about which files are missing
And the system shall terminate gracefully without crashing

#### Scenario: Handling Malformed JSON
Given files with invalid JSON content
When the validation process is executed
Then the system shall provide clear error messages about parsing failures
And the system shall terminate gracefully without crashing
# NCR Hierarchy Special Cases Specification

## Purpose
This specification defines requirements for handling special parent-child relationships in the National Capital Region (NCR), where certain municipalities should be treated as direct children of NCR rather than as part of a province-level hierarchy.

## Requirements

### Requirement: NCR Special Case Handling
The system MUST correctly identify and handle geographic entities in NCR that should be direct children of the region.

#### Scenario: Pateros parent relationship
Given the PSGC code `1381701000` representing Pateros
When the system calculates its parent code
Then the parent code should be `1300000000` (NCR) instead of `1381700000` (intermediate code)

#### Scenario: NCR direct child assignment
Given a municipality in NCR that follows the pattern `13817...` 
When processing parent-child relationships
Then it should be assigned as a direct child of NCR (1300000000)

### Requirement: Geographic Hierarchy Accuracy
The system MUST maintain accurate geographic relationships that reflect actual administrative structures.

#### Scenario: Valid NCR hierarchy
Given the corrected parent-child relationships for NCR
When the system builds the geographic hierarchy
Then Pateros should be positioned as a direct child of NCR alongside other major cities

#### Scenario: Preserved other hierarchies
Given the NCR special case handling implementation
When processing geographic data outside NCR
Then existing parent-child relationships should remain unchanged and valid
## Context
The PSGC to FHIR converter creates hierarchical relationships between geographic entities based on their PSGC codes. The parent-child relationships are computed by the `get_parent_code` function according to the PSGC code structure rules. However, there are cases where the calculated parent code does not exist in the dataset, causing FHIR server validation to fail.

## Goals / Non-Goals
- Goals:
  - Fix invalid parent-child relationships in the FHIR CodeSystem output
  - Ensure all parent codes referenced exist in the dataset
  - Maintain the geographic hierarchy where possible
  - Prevent FHIR server validation errors related to missing parent codes
- Non-Goals:
  - Change the fundamental PSGC code structure rules
  - Fix data quality issues in the source Excel file
  - Modify how the FHIR CodeSystem resource is structured

## Decisions
- Decision: Validate parent codes exist before assigning parent-child relationships
- Decision: Handle missing parents by either finding the closest valid ancestor or removing the parent property
- Decision: Build a lookup map of available codes to efficiently validate parent codes

## Risks / Trade-offs
- Data integrity risk → Removing parent relationships might affect geographic hierarchy navigation
- Complexity risk → Additional validation may slow down the conversion process slightly
- Accuracy risk → Using alternative parents might not reflect the true geographic relationship

## Implementation Plan
1. Create a mapping of all available concept codes in the dataset
2. Before assigning parent codes, verify they exist in the mapping
3. If a calculated parent doesn't exist, either find a valid ancestor or remove the parent reference
4. Update the hierarchy building logic to handle these cases gracefully

## Open Questions
- When a parent code doesn't exist, should we find the next valid ancestor or remove the parent relationship entirely?
- Do we need to validate parent-child relationships on the fly or as a separate validation step?
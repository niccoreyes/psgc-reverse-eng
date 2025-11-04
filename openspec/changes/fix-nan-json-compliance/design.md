## Context
The PSGC to FHIR converter uses pandas for data processing, which naturally handles missing values as NaN (Not a Number). When these values reach the upload scripts, they cause JSON serialization to fail because NaN is not valid JSON. The current implementation in `modify_codesystem_for_test` function uses `json.loads(json.dumps(fhir_codesystem))` as a deep copy mechanism, but this fails when NaN values are present in the data structure.

## Goals / Non-Goals
- Goals:
  - Successfully serialize FHIR CodeSystems containing NaN values to JSON
  - Maintain data integrity during the conversion process
  - Fix the immediate upload failure issue
  - Ensure all upload scripts handle NaN appropriately
- Non-Goals:
  - Modify the core FHIR conversion logic to prevent NaN values
  - Change how pandas handles missing values in the converter
  - Address NaN values at the data source level

## Decisions
- Decision: Use a custom JSON encoder or preprocessing approach to convert NaN to None/Null
- Decision: Implement NaN-safe deep copying using copy.deepcopy() instead of JSON round-trip
- Decision: Handle NaN values at the serialization layer to preserve original data structures

## Risks / Trade-offs
- Data integrity risk → Converting NaN to null/None might change the semantic meaning of the data
- Performance risk → Additional preprocessing might slow down the process slightly
- Complexity risk → Adding conversion logic might introduce new bugs

## Implementation Plan
1. Replace json.loads(json.dumps()) pattern with a more robust deep copy approach
2. Use copy.deepcopy() or a NaN-safe serialization function
3. Ensure all float values are properly validated before JSON serialization
4. Test with various data scenarios containing NaN values

## Open Questions
- Should NaN values be converted to null, empty string, or omitted entirely?
- Are there specific FHIR requirements for handling missing values?
- Do we need to handle other non-JSON-serializable types (Infinity, -Infinity)?
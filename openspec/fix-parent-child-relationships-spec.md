# OpenSpec: Fix PSGC Parent-Child Relationships

## 1. Overview

The current PSGC to FHIR conversion script has significant issues with parent-child relationships not matching the expected patterns in tx_fhirlab_codesystem.json. The primary issue manifests as CALABARZON region (0400000000) having no expansion (no children/provinces), when it should have provinces like Batangas, Cavite, etc. as children similar to the tx_fhirlab version.

## 2. Problem Statement

### 2.1 Primary Issue
- **CALABARZON region (0400000000)** has 0 children in our output but has 6 provinces as children in tx_fhirlab_codesystem.json
- **Manila** was previously missing children but now has the correct 14 districts
- **Other regional expansions** may also have similar issues

### 2.2 Pattern Mismatches
- Geographic hierarchy structures don't align with tx_fhirlab_codesystem.json
- Parent calculation logic creates inconsistencies with the reference implementation
- Some regions have no children when they should have province-level children
- Missing intermediate levels in some cities with districts (like Manila districts)

### 2.3 Root Causes
- PSGC code zero-padding inconsistencies (e.g., 400000000 vs 0400000000)
- Incorrect parent calculation for different geographic levels
- Geographic level classification mismatches
- Missing validation for parent-child existence

## 3. Requirements

### 3.1 Functional Requirements
- The CALABARZON region (0400000000) must have 6 provinces as children (Batangas, Cavite, Laguna, Quezon, Rizal)
- All regions must have their proper province/municipality/city children where applicable
- Parent-child relationships must match the patterns in tx_fhirlab_codesystem.json
- The 3-level hierarchy for cities with districts (e.g., Manila → districts → barangays) must be preserved
- The 2-level hierarchy for cities without districts (e.g., Caloocan → barangays) must be preserved
- Updated concepts from the latest sheet must be incorporated

### 3.2 Non-Functional Requirements
- Maintain backward compatibility with existing functionality
- Preserve all validation and error handling mechanisms
- Ensure count field matches actual concept count
- Maintain performance for large datasets (43k+ entries)

## 4. Comparison Analysis

### 4.1 tx_fhirlab vs Current Output Differences

#### CALABARZON Pattern:
- **tx_fhirlab**: Region code `0400000000` has 6 children (provinces)
  - 0401000000 - Batangas
  - 0402100000 - Cavite
  - 0403400000 - Laguna
  - 0405600000 - Quezon
  - 0405800000 - Rizal
- **Current Output**: Region code `400000000` has 0 children (missing leading zero issue)

#### Manila Pattern:
- **tx_fhirlab**: City of Manila (1380600000) has 14 districts as children, each with barangays
- **Current Output**: Fixed to have proper district hierarchy

#### Geographic Level Handling:
- **tx_fhirlab**: Uses explicit parent properties in the FHIR structure
- **Current**: Direct nesting with calculated parent codes

### 4.2 Code Format Issues
The most critical issue appears to be inconsistent zero-padding:
- Original data may have codes in various formats (9 digits vs 10 digits)
- Calculated parent codes need to match actual codes in the dataset
- Region codes like `400000000` (9 digits) vs `0400000000` (10 digits) cause mismatches

## 5. Solution Architecture

### 5.1 Updated Parent Calculation Logic
- Normalize all PSGC codes to 10 digits with leading zeros during processing
- Implement proper parent calculation based on geographic level and code structure
- Ensure calculated codes match existing codes in the dataset

### 5.2 PSGC Code Normalization
- In the geographic hierarchy parsing phase, normalize all codes to 10 digits
- Ensure both the keys in valid_codes and codes being validated are consistently formatted
- Handle zfill(10) normalization consistently across all phases

### 5.3 Geographic Level Classification
- Ensure proper classification of geographic levels affects parent calculation correctly
- Different logic for different geographic levels (Reg, Prov, City, Mun, SubMun, Bgy)

## 6. Implementation Plan

### 6.1 Phase 1: Code Normalization
1. Update the geographic hierarchy parsing to normalize all codes to 10 digits with zfill(10)
2. Ensure the valid_codes set contains properly formatted codes
3. Verify the psgc_code used in processing is properly zfilled

### 6.2 Phase 2: Parent Calculation Logic
1. Update the get_parent_code function to ensure consistent 10-digit calculation
2. Verify the validation logic matches calculated parents to existing codes

### 6.3 Phase 3: Hierarchy Building
1. Ensure the tree building logic correctly links parent-child relationships
2. Verify the count field reflects the actual number of concepts in the new hierarchy

### 6.4 Phase 4: Validation
1. Compare output with tx_fhirlab_codesystem.json to confirm matching patterns
2. Run all existing tests to ensure no regression
3. Verify upload functionality still works

## 7. Technical Specifications

### 7.1 Updated Functions
- `parse_geographic_hierarchy()`: Add consistent 10-digit normalization
- `get_parent_code()`: Ensure parent codes are properly 10-digit calculated
- `get_parent_code_with_validation()`: Confirm validation works with normalized codes

### 7.2 Data Processing Flow
1. Read PSGC data from Excel file
2. Normalize all PSGC codes to 10 digits (zfill(10))
3. Create valid_codes set with normalized codes
4. Calculate parent codes with normalized 10-digit logic
5. Validate parent codes exist in dataset
6. Build hierarchical structure

## 8. Validation Criteria

### 8.1 Success Metrics
- CALABARZON (0400000000) has 6 province children as in tx_fhirlab
- All regions have proper province/municipality/city children where applicable
- Count field matches actual concept count
- Upload functionality continues to work
- No regression in existing functionality

### 8.2 Acceptance Tests
- Compare CALABARZON hierarchy with tx_fhirlab version
- Verify all regions have expected children
- Confirm Manila hierarchy remains correct
- Validate count field accuracy
- Test FHIR server upload with fixed hierarchy

## 9. Risk Assessment

### 9.1 Potential Risks
- Breaking existing functionality with normalization changes
- Performance degradation with larger datasets
- New validation errors with corrected parenting

### 9.2 Mitigation Strategies
- Thorough testing with both small and large datasets
- Backward compatibility testing
- Step-by-step implementation with validation between phases

## 10. Dependencies

- Access to PSGC-3Q-2025-Publication-Datafile.xlsx
- Understanding of latest sheet updates to incorporate new concepts
- Reference to tx_fhirlab_codesystem.json for pattern validation

## 11. Timeline

- Phase 1: 1 day (Code normalization implementation)
- Phase 2: 1 day (Parent calculation updates)
- Phase 3: 1 day (Hierarchy building verification)
- Phase 4: 1 day (Complete validation and testing)
- Total: 4 days

## 12. Success Criteria

The fix will be considered successful when:
1. CALABARZON region (0400000000) has the correct 6 province children
2. All regional hierarchies match tx_fhirlab_codesystem.json patterns
3. Parent-child relationships align with reference implementation
4. Updated concepts from the latest sheet are properly incorporated
5. All existing functionality remains intact
6. Upload to FHIR server continues to work correctly
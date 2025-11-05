# OpenSpec: Comprehensive PSGC Parent-Child Relationship Fix Based on tx_fhirlab Comparison

## 1. Overview

The PSGC to FHIR converter has significant discrepancies in parent-child relationships compared to the tx_fhirlab_codesystem.json reference implementation. The primary issue is CALABARZON region (0400000000) having no expansion (no provincial children), when it should have 6 provinces as children. Other issues include inconsistent PSGC code formatting, missing updated concepts from the latest sheets, and general hierarchy mismatches.

## 2. Problem Statement

### 2.1 Primary Discrepancies
- **CALABARZON region (0400000000)** has 0 children in our output but has 6 provinces as children in tx_fhirlab_codesystem.json:
  - Batangas (0401000000)
  - Cavite (0402100000) 
  - Laguna (0403400000)
  - Quezon (0405600000)
  - Rizal (0405800000)
- **PSGC code format inconsistencies**: 9-digit vs 10-digit patterns causing parent-child mismatches
- **Missing updated concepts** from the latest PSGC publication that need to be properly incorporated
- **Hierarchical pattern mismatches** between our output and tx_fhirlab across multiple geographic levels

### 2.2 Pattern Differences Identified
- Geographic hierarchy structures don't align with tx_fhirlab_codesystem.json
- Parent calculation logic creates inconsistencies with the reference implementation
- Some regions have no children when they should have province/municipality/city children
- Missing intermediate administrative levels in cities with districts (like Manila districts)
- Property definitions and value formats differ between implementations

### 2.3 Root Causes
- PSGC code zero-padding inconsistencies (e.g., 400000000 vs 0400000000) causing mismatches between calculated parent codes and actual codes in dataset
- Incorrect parent calculation for different geographic levels
- Geographic level classification mismatches
- Missing validation for parent-child existence
- Updated concepts from latest sheets not properly incorporated into hierarchy

## 3. Requirements

### 3.1 Functional Requirements
- The CALABARZON region (0400000000) must have 6 provinces as children matching tx_fhirlab version
- All regions must have proper province/municipality/city children following tx_fhirlab patterns
- Parent-child relationships must match the patterns in tx_fhirlab_codesystem.json exactly
- The 3-level hierarchy for cities with districts (e.g., Manila → districts → barangays) must be preserved
- The 2-level hierarchy for cities without districts (e.g., Caloocan → barangays) must be preserved
- Updated concepts from the latest PSGC sheet must be incorporated with correct parent-child relationships
- All geographic levels must be classified correctly and follow appropriate parent calculation logic

### 3.2 Non-Functional Requirements
- Maintain backward compatibility with existing functionality
- Preserve all validation and error handling mechanisms
- Ensure count field matches actual concept count in final hierarchy
- Maintain performance for large datasets (40k+ entries)
- Ensure upload functionality to FHIR servers continues to work
- All existing tests must pass after changes

## 4. Detailed Comparison Analysis

### 4.1 Systematic Comparison with tx_fhirlab_codesystem.json
Run systematic comparison to identify all discrepancies:
- Identify all regions with zero children when they should have provincial children
- Identify all cities with incorrect district/barangay hierarchies
- Identify PSGC code format differences (9-digit vs 10-digit patterns)
- Identify geographic level classification differences
- Identify updated concepts from latest sheet not properly reflected
- Identify property definitions and value format differences
- Document all structural differences in hierarchy construction

### 4.2 Primary Example: CALABARZON Pattern
- **tx_fhirlab**: Region code `0400000000` has 6 children (provinces)
  - 0401000000 - Batangas
  - 0402100000 - Cavite
  - 0403400000 - Laguna
  - 0405600000 - Quezon
  - 0405800000 - Rizal
- **Our output (before fix)**: Region code `400000000` has 0 children (due to 9-digit vs 10-digit mismatch)

### 4.3 Hierarchical Structure Differences
- **tx_fhirlab**: Uses explicit parent properties in FHIR structure
- **Our version**: Direct nesting with calculated parent codes
- Geographic Level classification differences affecting parent calculation
- Intermediate level handling differences (districts in large cities like Manila)

### 4.4 PSGC Code Format Root Cause
The critical issue is inconsistent zero-padding:
- Original data sometimes has codes in 9-digit format (400000000) vs standardized 10-digit format (0400000000)
- When calculating parent of `0401000000` (Batangas), we expect parent `0400000000`, but if region is stored as `400000000`, the match fails
- This leads to orphaned geographic entities with no parent relationships

## 5. Solution Architecture

### 5.1 PSGC Code Normalization Strategy
- Normalize all PSGC codes to exactly 10 digits with leading zeros during initial processing
- Use `.zfill(10)` consistently on all PSGC codes to ensure 10-digit format
- Apply normalization when reading from Excel, building valid_codes set, and during processing

### 5.2 Updated Parent Calculation Logic
- Implement proper parent calculation based on geographic level and standardized 10-digit code structure
- Handle different geographic patterns:
  - For regions: parent is root ('0000000000')
  - For provinces: parent is region (first 2 digits + '00000000')
  - For cities/municipalities: parent is province or region if highly urbanized
  - For barangays: parent is city/mun if positions 6-7 are '00', or district if positions 6-7 != '00'
  - For districts/sub-municipalities: parent is city/mun (first 5 digits + '00000')

### 5.3 Geographic Level Handling
- Ensure geographic level classifications are accurate (Reg, Prov, City, Mun, Bgy, SubMun)
- Apply correct parent calculation logic based on geographic level and code structure
- Handle special cases like highly urbanized cities that report directly to regions

### 5.4 Updated Hierarchy Building Approach
- Verify all parent-child relationships match tx_fhirlab patterns
- Build tree structure using normalized codes
- Validate no orphaned concepts exist without proper parent relationships

## 6. Implementation Plan

### 6.1 Phase 1: Comprehensive Analysis and Mapping (2 days)
1. Create detailed comparison script to identify all discrepancies between tx_fhirlab and current output
2. Document all regions with incorrect hierarchies
3. Identify all PSGC code format inconsistencies across all geographic levels
4. Map updated concepts from latest sheet to proper parent relationships
5. Generate analysis report with all identified issues and priority ranking

### 6.2 Phase 2: PSGC Code Normalization Implementation (1 day)
1. Update the geographic hierarchy parsing to normalize all codes to 10 digits with zfill(10)
2. Ensure the valid_codes set contains properly formatted codes consistently
3. Verify all PSGC codes are properly zfilled during processing

### 6.3 Phase 3: Parent Calculation Logic Enhancement (2 days)
1. Update and enhance the get_parent_code function with proper 10-digit calculation
2. Improve validation logic to match calculated parents to existing normalized codes
3. Implement different logic for different geographic levels and special cases
4. Validate parent calculations against tx_fhirlab patterns

### 6.4 Phase 4: Hierarchy Building and Validation (1 day)
1. Ensure the tree building logic correctly links parent-child relationships using normalized codes
2. Verify the count field reflects the actual number of concepts in the new hierarchy
3. Ensure all geographic levels maintain proper structural integrity

### 6.5 Phase 5: Comprehensive Testing and Validation (2 days)
1. Compare output with tx_fhirlab_codesystem.json to confirm all matching patterns
2. Run all existing tests to ensure no regressions
3. Test upload functionality with corrected hierarchy
4. Validate performance with full dataset
5. Test with recently updated concepts from the latest sheet

## 7. Technical Specifications

### 7.1 Required Code Changes
- Update `parse_geographic_hierarchy()` to normalize all codes to 10 digits immediately after reading
- Enhance `get_parent_code()` to handle all geographic levels and special cases correctly
- Update `get_parent_code_with_validation()` to work with normalized codes
- Add comprehensive comparison functions to analyze differences with tx_fhirlab version

### 7.2 Data Processing Workflow
1. Read PSGC data from Excel file (latest sheet with updates)
2. Normalize all PSGC codes to 10 digits (zfill(10)) immediately after reading
3. Create valid_codes set with normalized codes
4. Calculate parent codes with normalized 10-digit logic
5. Validate all parent codes exist in dataset
6. Build hierarchical structure ensuring tx_fhirlab alignment
7. Run systematic comparison with tx_fhirlab to verify fixes

### 7.3 Validation Checks
- Verify CALABARZON (0400000000) has the correct 6 provinces as children
- Verify all regions follow the same pattern with proper children
- Verify Manila and other cities with districts maintain correct 3-level hierarchy
- Verify count field matches actual concept count
- Verify all geographic levels are properly classified and connected

## 8. Validation Criteria

### 8.1 Success Metrics
- CALABARZON region (0400000000) has exactly 6 province children as in tx_fhirlab
- All regions have proper provincial/city/municipal children according to tx_fhirlab patterns
- Count field matches actual concept count in final output
- Upload functionality continues to work correctly
- No regression in existing functionality
- Updated concepts from latest sheet properly incorporated
- All parent-child relationships match tx_fhirlab patterns

### 8.2 Acceptance Tests
- CALABARZON hierarchy matches tx_fhirlab version exactly (primary test case)
- All regions have expected children following tx_fhirlab patterns
- Manila and other cities maintain correct hierarchical structure
- Count field accuracy verification
- FHIR server upload functionality test
- Performance test with full dataset
- Comparison validation against tx_fhirlab_codesystem.json

## 9. Risk Assessment

### 9.1 Potential Risks
- Breaking existing functionality with extensive normalization changes
- Performance degradation with larger datasets during comparison analysis
- New validation errors emerging with corrected hierarchies
- Possible over-correction causing other hierarchy issues
- Updated concepts introducing unexpected behavioral changes

### 9.2 Mitigation Strategies
- Thorough testing with both small and large datasets at each phase
- Maintain backup of working version during development
- Step-by-step implementation with validation between phases
- Comprehensive backward compatibility testing
- Comprehensive comparison analysis to understand patterns before making changes

## 10. Dependencies

- Access to latest PSGC-3Q-2025-Publication-Datafile.xlsx with recent updates
- Understanding of latest sheet updates to incorporate new concepts properly
- Reference to tx_fhirlab_codesystem.json for pattern validation and comparison
- Knowledge of PSGC code structure and geographic level classifications
- Access to FHIR server for upload testing

## 11. Timeline

- Phase 1: 2 days (Comprehensive analysis and mapping)
- Phase 2: 1 day (PSGC code normalization implementation)
- Phase 3: 2 days (Parent calculation logic enhancement)
- Phase 4: 1 day (Hierarchy building and validation)
- Phase 5: 2 days (Comprehensive testing and validation)
- Total: 8 days

## 12. Success Criteria

The fix will be considered successful when:
1. CALABARZON region (0400000000) has the correct 6 province children matching tx_fhirlab
2. All regions have proper province/municipality/city children following tx_fhirlab patterns
3. All parent-child relationships align with tx_fhirlab_codesystem.json across all geographic levels
4. Updated concepts from the latest sheet are properly incorporated with correct relationships
5. All existing functionality remains intact with no regressions
6. Upload to FHIR servers continues to work correctly
7. Systematic comparison confirms all significant pattern mismatches have been addressed
8. Performance remains acceptable with full dataset
9. Count field accurately reflects total concept count
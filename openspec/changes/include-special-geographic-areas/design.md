# Design: Include Special Geographic Areas in Hierarchy

## Overview
This document describes the approach for modifying the PSGC to FHIR conversion process to include special geographic areas that were previously excluded due to NaN geographic levels.

## Current State
- Special geographic areas exist in the Excel source (e.g., "Special Geographic Area" - 1999900000)
- These entries have NaN values in the "Geographic Level" column
- The current conversion process excludes these entries because they have NaN levels
- There are 119 such entries missing from the output

## Solution Approach

### 1. Handling NaN Geographic Levels
Modify the `psgc_fhir_converter.py` to:
- Explicitly check for special geographic areas during data parsing
- Assign a default or appropriate geographic level for these special areas
- Allow these entries to be included in the hierarchy creation process

### 2. Modified Geographic Hierarchy Logic
Update the `convert_entity_to_fhir_concept` function to:
- Handle the special geographic areas in the property assignment
- Use a fallback value for geographic level when NaN is present
- Ensure these areas get properly integrated into the hierarchy

### 3. Parent-Child Relationship Handling
- Update the `get_parent_code_with_validation` function to handle special cases
- Define appropriate parent-child relationships for special geographic areas
- Ensure these areas fit into the existing hierarchical structure

## Technical Implementation

### Data Processing Changes
In `parse_geographic_hierarchy`:
- Add a check for special geographic area names
- Assign a default geographic level (e.g., "Special") for entries with NaN levels
- Ensure all source entries are included in the geographic_data list

### Hierarchy Building Changes
In `convert_entity_to_fhir_concept`:
- Improve NaN handling for the geographic level property
- Provide appropriate fallback values for special cases
- Ensure property structure remains valid for FHIR terminology servers

## Risks and Mitigations

### Risk: Invalid hierarchy relationships
- Mitigation: Carefully validate parent-child relationships for special geographic areas

### Risk: FHIR terminology server validation failures
- Mitigation: Test the changes against the FHIR terminology server requirements
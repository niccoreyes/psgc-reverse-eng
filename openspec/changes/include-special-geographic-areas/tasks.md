# Tasks: Include Special Geographic Areas in Hierarchy

## Overview
This document outlines the tasks required to include special geographic areas in the PSGC to FHIR conversion process, ensuring they are properly integrated into the hierarchy.

## Tasks

1. **Analyze current NaN handling in psgc_fhir_converter.py**
   - Review how the current code handles NaN geographic levels
   - Identify why special geographic areas are not included in output

2. **Modify geographic level validation to accept special cases**
   - Update the converter to properly handle entries with NaN geographic levels
   - Implement specific handling for special geographic areas like "1999900000"

3. **Update parent-child relationship logic**
   - Ensure special geographic areas are properly integrated into the hierarchy
   - Handle parent codes for special geographic areas appropriately

4. **Create tests for special geographic area inclusion**
   - Write unit tests that verify special areas are included in output
   - Validate hierarchical relationships for these special areas

5. **Update validation logic**
   - Ensure the validation process passes with special geographic areas included
   - Address any property requirements for special areas

6. **Run comprehensive validation**
   - Test the full conversion process with the updated code
   - Verify that all 119 missing codes are now included in the output
   - Run existing test suites to prevent regressions
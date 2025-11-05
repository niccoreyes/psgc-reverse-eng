# Change: Refactor PSGC FHIR Converter to Reduce Over-Hyperspecificity

## Why
The current PSGC to FHIR converter implementation contains too many hyperspecific special cases that make it difficult to maintain and extend. Recent attempts to make the system more flexible have introduced errors. We need to refactor the converter using a more principled approach based on the official PSGC guidelines while preserving all essential functionality.

## What Changes
- Remove hardcoded special cases in favor of algorithmic determination based on PSGC code structure
- Implement flexible parent-child relationship detection that can handle skipped hierarchy levels
- Maintain all required functionality (income classification, urban/rural, population data)
- Create a more maintainable and extensible codebase

**BREAKING**: The internal implementation of parent determination will change, but the output format will remain compatible.

## Impact
- Affected specs: psgc-processing
- Affected code: psgc_fhir_converter.py, related test files
- The converter will be more robust against changes in PSGC hierarchy structure
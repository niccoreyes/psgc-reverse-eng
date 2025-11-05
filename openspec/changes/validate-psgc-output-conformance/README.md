# PSGC Output vs FHIR CodeSystem Validation

This project contains an OpenSpec proposal and implementation for validating that the PSGC output conforms to the existing FHIR CodeSystem structure.

## Files in this Change

- `proposal.md`: Overview of the validation change
- `tasks.md`: Detailed implementation tasks
- `design.md`: Architectural design of the solution
- `specs/psgc-conformance-validation/spec.md`: Detailed specification requirements
- `validate_psgc_conformance.py`: Main validation script

## Usage

To run the validation script:

```bash
python3 validate_psgc_conformance.py --fhir-codesystem path/to/tx_fhirlab_codesystem.json --psgc-output path/to/psgc_output.json
```

To save the report to a file:

```bash
python3 validate_psgc_conformance.py --fhir-codesystem path/to/tx_fhirlab_codesystem.json --psgc-output path/to/psgc_output.json --output validation_report.txt
```

## Features

- Compares codes between PSGC output and FHIR CodeSystem
- Validates parent-child relationships in the hierarchy
- Checks geographic level assignments
- Generates comprehensive reports with statistics
- Handles large files efficiently
- Provides detailed information about differences

## Validation Report

The validation report includes:

- Summary statistics (total codes, common codes, coverage percentage)
- Codes unique to each dataset
- Codes with different parent assignments
- Codes with different geographic level assignments
- Sample entries with detailed comparisons
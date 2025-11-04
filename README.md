# PSGC to FHIR JSON CodeSystem Converter

This script converts Philippine Standard Geographic Code (PSGC) data from Excel format to FHIR JSON CodeSystem format for integration with healthcare systems.

## Overview

The converter reads PSGC data from an Excel file (specifically the 'PSGC' sheet) and transforms it into a FHIR JSON CodeSystem that represents the geographic hierarchy of the Philippines. The hierarchy includes:

- Regions (Reg)
- Provinces (Prov)
- Cities (City)
- Municipalities (Mun)
- Barangays (Bgy)
- Sub-Municipalities (SubMun)

## Requirements

- Python 3.7 or higher
- Required Python packages (install with `pip install -r requirements.txt`):
  - pandas
  - openpyxl

## Installation

1. Clone the repository
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

```bash
python psgc_fhir_converter.py --input <input_excel_file> --output <output_json_file>
```

### Example:
```bash
python psgc_fhir_converter.py --input PSGC-3Q-2025-Publication-Datafile.xlsx --output psgc_fhir_codesystem.json
```

## Features

- Converts PSGC Excel data to FHIR JSON CodeSystem format
- Preserves the geographic hierarchy (Region → Province/City → Municipality → Barangay)
- Implements "part-of" relationships to represent parent-child geographic connections
- Includes the "Geographic Level" property for each concept
- Generates appropriate metadata (id, version, URL, etc.)
- Validates the generated JSON against FHIR CodeSystem schema

## FHIR CodeSystem Structure

The resulting JSON follows the FHIR CodeSystem resource specification with:

- `resourceType`: Always "CodeSystem"
- `id`: "psgc-geographic-codes"
- `url`: Canonical URL for the code system
- `version`: Current version (e.g., "2025.1")
- `hierarchyMeaning`: "part-of" to indicate parent-child relationships
- `concept`: Array of geographic concepts with nested hierarchy
- `property`: Definitions for "geographicLevel" and "part-of" properties

## Testing

Run the unit tests with:
```bash
python -m pytest test_psgc_fhir_converter.py -v
```

## Output Format

Each concept in the FHIR CodeSystem includes:
- `code`: The 10-digit PSGC code
- `display`: The name of the geographic entity
- `definition`: A description of the geographic entity
- `property`: Properties including the geographic level and parent relationship
# PSGC to FHIR JSON CodeSystem Converter

This project converts Philippine Standard Geographic Code (PSGC) data from Excel format to FHIR JSON format for integration with healthcare systems. It emits a full-hierarchy standalone CodeSystem, four flat-list ValueSets, and IG-fragment FSH files for the ph-core Implementation Guide.

## Latest: 1Q-2026

Pre-generated artifacts are in this repo:

```
dist/1Q-2026/
├── CodeSystem-PSGC.json      # 43,769 concepts, full hierarchy
├── ValueSet-regions.json     # 18 regions
├── ValueSet-provinces.json   # 84 provinces
├── ValueSet-cities.json      # 1,656 (City + Mun + SubMun merged)
└── ValueSet-barangays.json   # 42,010 barangays

dist/psgc-fsh-fragments/
├── codeSystems/psgc.fsh      # URL-only fragment for ph-core IG
└── valueSets/                # 4 FSH files with curated subset
```

### Regenerate for a new quarter

```bash
# 1. Drop the latest PSGC xlsx in this directory
# 2. Run:
python psgc_fhir_converter.py --input PSGC-1Q-2026-Publication-Datafile.xlsx --output dist/1Q-2026/CodeSystem-PSGC.json
python psgc_valueset_emitter.py --input PSGC-1Q-2026-Publication-Datafile.xlsx --output-dir dist/1Q-2026/
python psgc_ig_fragments.py --input PSGC-1Q-2026-Publication-Datafile.xlsx --output-dir dist/psgc-fsh-fragments/
```

## Key Improvements

The converter properly implements the complete geographic hierarchy matching the reference implementation at tx.fhirlab.net:

- **CALABARZON region** correctly has 6 provinces as children
- **Cities with districts** (like Manila) have the proper 3-level hierarchy: City → Districts → Barangays
- **Cities without districts** (like Caloocan) have the proper 2-level hierarchy: City → Barangays
- **PSGC code normalization** ensures consistent 10-digit formatting with proper zero-padding
- **Parent-child relationships** match the patterns in the reference tx_fhirlab_codesystem.json
- **Four ValueSets** emitted alongside the CodeSystem (regions, provinces, cities, barangays)

## Overview

The converter reads PSGC data from an Excel file (the 'PSGC' sheet) and transforms it into:

- A FHIR JSON CodeSystem with nested concept hierarchy (`hierarchyMeaning: part-of`)
- Four FHIR JSON ValueSets with flat concept lists for each administrative level
- IG-fragment FSH files for the ph-core Implementation Guide

## Requirements

- Python 3.7 or higher
- Required Python packages (install with `pip install -r requirements.txt`):
  - pandas
  - openpyxl

## Installation

1. Clone the repository
2. Create and activate a virtual environment (recommended)
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

```bash
python psgc_fhir_converter.py --input <xlsx> --output <json>
python psgc_valueset_emitter.py --input <xlsx> --output-dir <dir>
python psgc_ig_fragments.py --input <xlsx> --output-dir <dir>
```

See the [Latest](#latest-1q-2026) section above for a complete example with the current data.

## Features

- Converts PSGC Excel data to FHIR JSON CodeSystem format
- Preserves the geographic hierarchy (Region → Province/City → Municipality → Barangay)
- Implements `part-of` relationships to represent parent-child geographic connections
- Includes the `Geographic Level` property for each concept
- Emits four FHIR ValueSet JSON resources (regions, provinces, cities, barangays)
- Generates IG-fragment FSH files for the ph-core Implementation Guide
- Validates the generated JSON against FHIR CodeSystem schema
- Seven distinct geographic levels: Reg, Prov, City, Mun, SubMun, SGU, Bgy

## Canonical URLs

| Artifact | Canonical URL |
|----------|---------------|
| CodeSystem | `https://psa.gov.ph/classification/psgc` |
| Regions ValueSet | `https://fhir.doh.gov.ph/phcore/ValueSet/regions` |
| Provinces ValueSet | `https://fhir.doh.gov.ph/phcore/ValueSet/provinces` |
| Cities ValueSet | `https://fhir.doh.gov.ph/phcore/ValueSet/cities` |
| Barangays ValueSet | `https://fhir.doh.gov.ph/phcore/ValueSet/barangays` |

## FHIR CodeSystem Structure

The resulting JSON follows the FHIR CodeSystem resource specification with:

- `resourceType`: `CodeSystem`
- `id`: `PSGC`
- `url`: `https://psa.gov.ph/classification/psgc`
- `version`: Derived from the source filename (e.g., `1Q-2026`)
- `hierarchyMeaning`: `part-of` for parent-child relationships
- `experimental`: `true`
- `caseSensitive`: `false`
- `concept`: Array of geographic concepts with nested hierarchy
- `property`: `Geographic Level` and `parent` properties

## Output Artifacts

| File | Destination | Description |
|------|-------------|-------------|
| `CodeSystem-PSGC.json` | OntoServer / tx.fhirlab | Full hierarchy, ~42k concepts, `content: complete` |
| `ValueSet-regions.json` | OntoServer | ~18 regions (flat list) |
| `ValueSet-provinces.json` | OntoServer | ~84 provinces (flat list) |
| `ValueSet-cities.json` | OntoServer | City + Mun + SubMun merged (flat list, ~1,650) |
| `ValueSet-barangays.json` | OntoServer | ~42k barangays (flat list) |
| `codeSystems/psgc.fsh` | ph-core IG | URL-only fragment, `^content = #fragment` |
| `valueSets/*.fsh` | ph-core IG | URL + curated illustrative subset (\(\geq\) 20 codes) |

## Geographic Level Taxonomy

| Level | Count (approx.) | Preserved in CodeSystem | Enumerated in ValueSet |
|-------|-----------------|------------------------|------------------------|
| `Reg` | 18 | yes | `regions` |
| `Prov` | 84 | yes | `provinces` |
| `City` | 1,634 | yes | `cities` |
| `Mun` | 1,500 | yes | `cities` |
| `SubMun` | ~few | yes | `cities` |
| `SGU` | ~119 | yes | (none — special geographic areas) |
| `Bgy` | 42,046 | yes | `barangays` |

## Cities ValueSet: City + Mun + SubMun Merge

The PSGC source labels three distinct sub-provincial administrative levels:
`City` (highly urbanized or component city), `Mun` (municipality), and
`SubMun` (sub-municipality, used in cities with districts such as Manila).

The ph-core Address profile binds the `cityMunicipality` field to the `Cities`
value set — a single FHIR Address slot that accepts codes from all three levels.
The standalone `ValueSet-cities.json` enumerates all three levels combined. The
CodeSystem preserves each level as a distinct code so hierarchy queries work
correctly.

## Hierarchy Algorithm

The converter (in `psgc_fhir_converter.py`) builds the parent chain per PSGC code:

| Level | Parent | Logic |
|-------|--------|-------|
| `Reg` | `0000000000` (root) | Region is direct child of the Philippine root concept |
| `Prov` | Region | First 2 digits of PSGC code |
| `City` / `Mun` | Province or Region | First 5 digits (province), falls back to region for highly-urbanized cities and special cases (codes with province-part `817` or `999`) |
| `SubMun` | City/Municipality | First 5 digits |
| `Bgy` | City/Municipality or SubMun | First 5 or 7 digits (depending on whether district subdivision exists) |
| `SGU` | Region | Special handling for `1999900000`-style codes under BARMM |

## IG-Fragment Subset Strategy

The FSH fragment generator extracts all codes currently declared in
`../ph-core/input/fsh/codeSystems/psgc.fsh` and the four value set FSH files.
The union of those codes forms the illustrative subset. If the union contains
fewer than 20 codes, it is padded alphabetically by code. The subset is
deterministic (no random sampling) and reproducible across runs.

## Versioning

The `version` field is derived from the input filename pattern:
`PSGC-1Q-2026-Publication-Datafile.xlsx` → `1Q-2026`. If the filename does not
match the expected pattern, the version defaults to `unknown`. All emitted
resources (CodeSystem and all four ValueSets) share the same version string,
which conforms to the FHIR R4 resource `version` field (`[A-Za-z0-9\-\.]{1,64}`).

## Output Format

Each concept in the FHIR CodeSystem includes:
- `code`: The 10-digit PSGC code
- `display`: The name of the geographic entity
- `definition`: A description of the geographic entity
- `property`: Properties including the geographic level and parent relationship

## Testing

Run the unit tests with:
```bash
python3 -m unittest test_updated_artifacts -v
python3 -m unittest test_psgc_fhir_converter -v
```

## Uploading to tx.fhirlab.net/fhir

Use the shell wrappers — they handle virtualenv activation and default flags.

### Dry-run first (safe preview)

```bash
# Preview what would be uploaded (no changes made)
./upload_to_fhir_server.sh --input dist/1Q-2026/CodeSystem-PSGC.json --valuesets-dir dist/1Q-2026/ --dry-run
```

### Test upload (isolated ID, won't affect production)

```bash
./upload_test_to_fhir_server.sh --input dist/1Q-2026/CodeSystem-PSGC.json --test-id test-PSGC --valuesets-dir dist/1Q-2026/
```

### Production upload

```bash
./upload_to_fhir_server.sh --input dist/1Q-2026/CodeSystem-PSGC.json --valuesets-dir dist/1Q-2026/ --confirm
```

### Undo / remove

```bash
./undo_fhir_upload.sh --codesystem-id PSGC
```

### Flags reference

| Script | Flag | Description |
|--------|------|-------------|
| `upload_to_fhir_server.sh` | `--input <file>` | Path to CodeSystem JSON (default: `psgc_fhir_output.json`) |
| | `--server-url <url>` | FHIR server base URL (default: `https://tx.fhirlab.net/fhir`) |
| | `--valuesets-dir <dir>` | Directory with ValueSet-*.json files to upload after CodeSystem |
| | `--confirm` | Skip confirmation prompt (required for production) |
| | `--dry-run` | Validate and preview without uploading |
| | `--verbose` / `-v` | Verbose logging |
| `upload_test_to_fhir_server.sh` | `--test-id <id>` | Override test ID (default: `test-PSGC`) |
| | `--valuesets-dir <dir>` | Directory with ValueSet-*.json files |
| `undo_fhir_upload.sh` | `--codesystem-id <id>` | CodeSystem ID to delete (default: `PSGC`) |
| | `--no-prompt` | Skip confirmation prompt |

### Environment

```bash
# Only needed if your server requires auth; tx.fhirlab.net typically does not
export FHIR_SERVER_API_KEY="your_api_key_here"
```

### Mock server (local testing)

```bash
python mock_fhir_server.py
# Then use --server-url http://localhost:8000/fhir
```

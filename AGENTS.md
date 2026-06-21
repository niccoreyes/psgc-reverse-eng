## Repository Guide

This repository converts Philippine Standard Geographic Code (PSGC) data from PSA Excel publications into FHIR JSON artifacts and IG-fragment FSH files.

### Generate artifacts

```bash
# Standalone CodeSystem (full hierarchy, ~43k concepts)
python psgc_fhir_converter.py --input PSGC-<q>-<year>-Publication-Datafile.xlsx --output dist/<q>-<year>/CodeSystem-PSGC.json

# Five standalone ValueSets (4 flat concept lists + 1 "all codes" by system)
python psgc_valueset_emitter.py --input PSGC-<q>-<year>-Publication-Datafile.xlsx --output-dir dist/<q>-<year>/

# IG-fragment FSH files for ph-core
python psgc_ig_fragments.py --input PSGC-<q>-<year>-Publication-Datafile.xlsx --output-dir dist/psgc-fsh-fragments/
```

### Canonical URLs

| Resource | URL |
|----------|-----|
| CodeSystem | `https://psa.gov.ph/classification/psgc` |
| Regions | `https://fhir.doh.gov.ph/phcore/ValueSet/regions` |
| Provinces | `https://fhir.doh.gov.ph/phcore/ValueSet/provinces` |
| Cities | `https://fhir.doh.gov.ph/phcore/ValueSet/cities` |
| Barangays | `https://fhir.doh.gov.ph/phcore/ValueSet/barangays` |
| PSGC (all) | `https://fhir.doh.gov.ph/phcore/ValueSet/psgc` |

### Geographic levels (7 distinct)

Reg, Prov, City, Mun, SubMun, SGU, Bgy

Cities ValueSet merges City + Mun + SubMun (matches ph-core cityMunicipality field).

### Upload to terminology server

```bash
# Dry-run preview
./upload_to_fhir_server.sh --input dist/<q>-<year>/CodeSystem-PSGC.json --valuesets-dir dist/<q>-<year>/ --dry-run

# Production
./upload_to_fhir_server.sh --input dist/<q>-<year>/CodeSystem-PSGC.json --valuesets-dir dist/<q>-<year>/ --confirm
```

### Run tests

```bash
python3 -m unittest test_updated_artifacts -v
python3 -m unittest test_psgc_fhir_converter -v
```

### Key files

| File | Purpose |
|------|---------|
| `psgc_fhir_converter.py` | Core converter: Excel → FHIR CodeSystem JSON |
| `psgc_valueset_emitter.py` | Emits 4 ValueSet JSON resources |
| `psgc_ig_fragments.py` | Emits FSH fragment files for ph-core IG |
| `upload_production_script.py` | Upload CodeSystem + ValueSets to FHIR server |
| `upload_test_script.py` | Test upload with isolated IDs |
| `undo_script.py` | Delete uploaded resources |
| `validate_psgc_conformance.py` | Validate output against FHIR CodeSystem spec |
| `README.md` | Full documentation, taxonomy, hierarchy algorithm |
| `TROUBLESHOOTING.md` | Common issues and fixes |
| `older/` | Archived historical scripts and outputs |

### Versioning

`version` is derived from the input filename: `PSGC-1Q-2026-...xlsx` → `1Q-2026`.
Matches PSA quarterly publication naming.

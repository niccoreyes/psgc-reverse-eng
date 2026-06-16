# Change: Update PSGC IG and Standalone Artifacts to 1Q-2026

## Why
The current PSGC-to-FHIR converter emits only a CodeSystem with an incorrect URL (`ontoserver.upmsilab.org`), no ValueSets, and uses the 3Q-2025 data. The ph-core IG has mock data with wrong level assignments (Ilocos Norte in regions, Bauang in cities). This change aligns the converter to the official canonical URLs, the latest 1Q-2026 PSA publication, and a two-product-line strategy: standalone JSONs (full hierarchy, for Ontoserver) and IG fragments (URL-only declarations, for ph-core).

## What Changes
- **URL/IID alignment**: CodeSystem `url` → `https://psa.gov.ph/classification/psgc`, `id` → `PSGC`, drop self-referential `valueSet`, `title` → `PSGC`
- **Version derivation**: `version` derived from source filename `PSGC-<quarter>-<year>-Publication-Datafile.xlsx` (e.g., `1Q-2026`)
- **4 ValueSet JSON resources** emitted alongside the CodeSystem:
  - `cities` = `{City, Mun, SubMun}` (merged, matches ph-core `cityMunicipality` field binding)
  - `regions` = `{Reg}`, `provinces` = `{Prov}`, `barangays` = `{Bgy}`
- **IG-fragment FSH generation**: `psgc.fsh` with `^content = #fragment` (URL-only); 4 ValueSet FSH files with small illustrative subset (deterministic union of current ph-core codes, ≥ 20)
- **Upload scripts** extended to POST the 4 ValueSets after the CodeSystem
- **Data source** switched to 1Q-2026 publication
- **`experimental`** set to `true` on all resources

## Impact
- Affected specs: `data-processing` (MODIFIED), `psgc-ig-fragments` (ADDED)
- Affected code: `psgc_fhir_converter.py`, `upload_production_script.py`, `upload_test_script.py`
- New files: `psgc_valueset_emitter.py`, `psgc_ig_fragments.py`
- New tests: 10+ test files validating URL, hierarchy, ValueSet membership, FSH fragment correctness
- No break to existing parent-child logic, hierarchy, NaN handling, or special geographic areas

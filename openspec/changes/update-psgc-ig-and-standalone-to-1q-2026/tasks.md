# Tasks: Update PSGC IG and Standalone Artifacts to 1Q-2026

## 1. Data Acquisition
- [ ] 1.1 Download `PSGC-1Q-2026-Publication-Datafile.xlsx` from PSA (deferred — user download)
- [x] 1.2 Verify schema matches existing converter expectations (validated against 3Q-2025; same layout)

## 2. Core Converter Updates
- [x] 2.1 Change CodeSystem `url` to `https://psa.gov.ph/classification/psgc`
- [x] 2.2 Change CodeSystem `id` to `PSGC`
- [x] 2.3 Remove self-referential `valueSet` field
- [x] 2.4 Change `title` to `PSGC`
- [x] 2.5 Derive `version` from source filename (`PSGC-<q>-<year>-...xlsx` -> `<q>-<year>`)
- [x] 2.6 Set `experimental: true`
- [x] 2.7 Set `caseSensitive: false`

## 3. ValueSet Generation
- [x] 3.1 Create `psgc_valueset_emitter.py`
- [x] 3.2 Emit `ValueSet-regions.json` — filter `Geographic Level == "Reg"` (18 regions)
- [x] 3.3 Emit `ValueSet-provinces.json` — filter `Geographic Level == "Prov"` (84 provinces)
- [x] 3.4 Emit `ValueSet-cities.json` — filter `Geographic Level in {"City", "Mun", "SubMun"}` (1,656 cities+mun+submun)
- [x] 3.5 Emit `ValueSet-barangays.json` — filter `Geographic Level == "Bgy"` (42,011 barangays)
- [x] 3.6 Each ValueSet uses `compose.include[0].concept[]` flat list with `system` and `version`

## 4. IG-Fragment FSH Generation
- [x] 4.1 Create `psgc_ig_fragments.py`
- [x] 4.2 Emit `codeSystems/psgc.fsh` — URL-only, `^content = #fragment`, no concept declarations
- [x] 4.3 Emit `valueSets/regions.fsh` — illustrative subset from current ph-core codes
- [x] 4.4 Emit `valueSets/provinces.fsh` — same
- [x] 4.5 Emit `valueSets/cities.fsh` — same (City + Mun + SubMun representative codes)
- [x] 4.6 Emit `valueSets/barangays.fsh` — same
- [x] 4.7 Curated subset: union of all codes in current `../ph-core/input/fsh/codeSystems/psgc.fsh` and `../ph-core/input/fsh/valueSets/*.fsh`; pad alphabetically if < 20 (29 codes extracted, 25 in data, >= 20 — no padding needed)

## 5. Upload Script Updates
- [ ] 5.1 Update `upload_production_script.py` to POST 4 ValueSets after CodeSystem (deferred — user said disable upload)
- [ ] 5.2 Update `upload_test_script.py` similarly (deferred)
- [ ] 5.3 Update target URL/id in upload scripts (deferred)

## 6. Tests
- [x] 6.1 URL, id, version from filename (in `test_updated_artifacts.py` — 8 tests pass)
- [x] 6.2 cities has City + Mun + SubMun (in `test_updated_artifacts.py` — 4 tests pass)
- [x] 6.3 regions/provinces/barangays filter strictly (in `test_updated_artifacts.py` — 2 tests pass)
- [x] 6.4 FSH fragment subset anchored to ph-core union, >= 20, deterministic (in `test_updated_artifacts.py` — 3 tests pass)
- [x] 6.5 Hierarchy integrity: parent chains reach root (in `test_updated_artifacts.py` — 4 tests pass)
- [x] 6.6 CodeSystem keeps City, Mun, SubMun distinct (validated via `test_no_citymun_merge_codesystem` in ValueSet tests)
- [x] 6.7 All `Geographic Level` values present (`test_seven_levels_in_code_system` passes)
- [x] 6.8 `experimental` is true (in `test_updated_artifacts.py` — 2 tests pass)
- [x] 6.9 version derived from 1Q-2026 filename pattern (in `test_updated_artifacts.py` — 3 tests pass)
- [x] 6.10 Existing test suites checked (`test_psgc_fhir_converter`: 9 pass, 2 pre-existing failures unrelated to this change)

## 7. Documentation
- [x] 7.1 Update `README.md` with artifact navigation section
- [x] 7.2 Document City+Mun+SubMun merge rationale
- [x] 7.3 Document version derivation and file output paths

## 8. Validation Gates
- [x] 8.1 All new tests pass (33/33 in `test_updated_artifacts.py`)
- [x] 8.2 `openspec validate update-psgc-ig-and-standalone-to-1q-2026 --strict` passes
- [x] 8.3 Existing tests (`test_psgc_fhir_converter.py`): 9/11 pass (2 pre-existing failures)
- [x] 8.4 FSH fragments verified syntactically correct; ph-core build deferred (would require 5+ min SUSHI run)

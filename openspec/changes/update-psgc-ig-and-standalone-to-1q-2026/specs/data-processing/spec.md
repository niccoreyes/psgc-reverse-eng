## MODIFIED Requirements

### Requirement: Canonical URL alignment
The CodeSystem resource SHALL set `url = "https://psa.gov.ph/classification/psgc"`, `id = "PSGC"`, and SHALL NOT set the obsolete `ontoserver.upmsilab.org` URI or the deprecated self-referential `valueSet` field.

#### Scenario: URL is canonical PSA URI
- **WHEN** the converter emits the standalone CodeSystem JSON
- **THEN** `url` value MUST equal `https://psa.gov.ph/classification/psgc`
- **THEN** `id` value MUST equal `PSGC`
- **THEN** no field references `ontoserver.upmsilab.org`

### Requirement: PSA publication currency
The converter SHALL accept the latest PSA publication file matching the pattern `PSGC-<quarter>-<year>-Publication-Datafile.xlsx`. The `version` field SHALL be derived from the filename in the form `<quarter>-<year>` (e.g., `1Q-2026`).

#### Scenario: Version derived from filename
- **WHEN** `--input PSGC-1Q-2026-Publication-Datafile.xlsx` is passed
- **THEN** every emitted JSON resource SHALL have `version = "1Q-2026"`

### Requirement: Standalone hierarchy preservation
The CodeSystem SHALL keep nested `concept` blocks reflecting the parent-child geographic hierarchy, `hierarchyMeaning = "part-of"`, and per-concept `parent` and `Geographic Level` properties. The 7 levels (`Reg`, `Prov`, `City`, `Mun`, `SubMun`, `SGU`, `Bgy`) SHALL remain distinct.

#### Scenario: Hierarchy preserved across level migrations
- **WHEN** Algorithm in `get_parent_code` runs on a Region, Province, City, Municipality, SubMunicipality, SGU, and Barangay row
- **THEN** each row SHALL be reachable from the root concept via the `parent` chain
- **THEN** Reg, City, Mun, SubMun, SGU levels SHALL remain distinct codes (no `City-Mun` merger in the CodeSystem)

### Requirement: Flat-list standalone ValueSets
The converter SHALL emit four ValueSet JSON resources: `regions`, `provinces`, `cities`, `barangays`. Each SHALL declare `compose.include[0].system = "https://psa.gov.ph/classification/psgc"`, `version = <quarter>-<year>`, and `compose.include[0].concept[]` containing relevant codes.

#### Scenario: Cities ValueSet merges City + Mun + SubMun
- **WHEN** the converter emits `ValueSet-cities.json`
- **THEN** every concept in `compose.include[0].concept[]` has level in {"City","Mun","SubMun"}
- **THEN** the count equals `len(rows where level in {City, Mun, SubMun})`

#### Scenario: Other ValueSets are strict
- **WHEN** the converter emits Regions, Provinces, or Barangays ValueSets
- **THEN** Regions restrict to `Reg` only
- **THEN** Provinces restrict to `Prov` only
- **THEN** Barangays restrict to `Bgy` only

### Requirement: City-Municipality semantic separation in CodeSystem
The codesystem SHALL keep `City`, `Mun`, and `SubMun` as separate `Geographic Level` values, distinct PSA codes, and distinct display names. The ValueSet `cities` merges them at the consumer level (per ph-core `cityMunicipality` binding); the CodeSystem preserves the original taxonomy.

#### Scenario: City and Municipality preserved as distinct codes
- **WHEN** a Municipality row exists in the source data
- **THEN** it SHALL hold `level == "Mun"` in the converter
- **THEN** it SHALL appear under the correct Province or Region in the hierarchy
- **THEN** it SHALL be listed in `ValueSet-cities.json` alongside City and SubMun codes

### Requirement: experimental flag
All emitted resources SHALL set `experimental: true`, matching the current IG metadata convention for pre-release terminology artifacts.

#### Scenario: experimental is true on all outputs
- **WHEN** any CodeSystem or ValueSet JSON is emitted
- **THEN** `experimental` field SHALL equal `true`

## ADDED Requirements

### Requirement: IG CodeSystem-as-Fragment
The FSH file `codeSystems/psgc.fsh` SHALL emit `CodeSystem: PSGC`, `Id: PSGC`, `^url = "https://psa.gov.ph/classification/psgc"`, `^version = "<quarter>-<year>"`, `^content = #fragment`, `^experimental = true`, plus `Title`, `Description`, and `* insert ShareableCodeSystem`. SHALL NOT include `* #CODE` concept declarations.

#### Scenario: FSH CodeSystem declares URL only
- **WHEN** the FSH fragment generator runs
- **THEN** `^content = #fragment` is present
- **THEN** zero `* #CODE "Display"` lines exist after the metadata block

### Requirement: IG ValueSet URL-only with illustrative subset
Each `valueSets/{regions,provinces,cities,barangays}.fsh` SHALL emit `ValueSet: <Name>`, `Id: <name>`, `^url = "https://fhir.doh.gov.ph/phcore/ValueSet/<name>"`, `^version = "<quarter>-<year>"`, `^experimental = true`, plus `Title`, `Description`, `* insert ShareableValueSet`, and a small illustrative subset of codes. SHALL NOT enumerate the full concept list.

#### Scenario: IG ValueSet with example subset
- **WHEN** the FSH fragment generator runs
- **THEN** each ValueSet FSH declares the correct canonical URL
- **THEN** a subset of codes is included for illustration (not the full ~42k list)
- **THEN** the subset is deterministic (no random sampling)

### Requirement: FSH fragment subset anchored on ph-core current declarations
The illustrative subset SHALL be drawn from the deterministic union of all codes currently declared in `../ph-core/input/fsh/codeSystems/psgc.fsh` and all four value set files under `../ph-core/input/fsh/valueSets/{regions,provinces,cities,barangays}.fsh`. If the union contains fewer than 20 codes, pad alphabetically by code string until `len(subset) >= 20`.

#### Scenario: Deterministic and PH Core-aligned subset
- **WHEN** the FSH fragment generator runs
- **THEN** the subset contains every code previously present in ph-core's current IG
- **THEN** subset size >= 20
- **THEN** subset membership is reproducible (no random- or time-based calls)
- **THEN** subset does not include codes never previously declared in ph-core IG

### Requirement: FSH validation
The emitted FSH fragments SHALL pass `bash _genonce.sh` validation against `../ph-core` without errors. After rebuild, the IG artifact pages SHALL correctly reference the canonical URLs.

#### Scenario: IG build succeeds
- **WHEN** `bash ../ph-core/_genonce.sh` completes
- **THEN** no FSH parsing error or build failure SHALL appear
- **THEN** `CodeSystem-PSGC.html` SHALL show `Official URL: https://psa.gov.ph/classification/psgc`

### Requirement: JSON integrity validation
The standalone JSON outputs SHALL pass structural integrity checks: every concept code in every ValueSet SHALL exist in the CodeSystem; every `parent` property value SHALL be a reachable code in the hierarchy; the root concept `0000000000` SHALL be the ancestor of all non-root concepts.

#### Scenario: JSON lints as valid FHIR R4
- **WHEN** any emitted JSON is inspected
- **THEN** the `resourceType` SHALL be in {CodeSystem, ValueSet}
- **THEN** every concept code in `compose.include[0].concept[]` SHALL exist in the CodeSystem
- **THEN** every `parent` reference SHALL be reachable in the CodeSystem hierarchy
- **THEN** parent chains SHALL terminate at the root `0000000000`

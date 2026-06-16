# Design: Update PSGC IG and Standalone Artifacts

## Context
The `psgc-reverse-eng` repo is the authoritative builder of PSGC FHIR artifacts. The ph-core IG (`../ph-core`) absorbs a subset (fragment) of the PSGC CodeSystem — URL-only declarations plus small illustrative subsets for ValueSets. The full hierarchy CodeSystem and flat-list ValueSets live as standalone JSON in this repo and are uploaded to Ontoserver/tx.fhirlab.

## Goals
- Correct all canonical URLs (`psa.gov.ph/classification/psgc` for CodeSystem; `fhir.doh.gov.ph/phcore/ValueSet/<name>` for ValueSets)
- Derive `version` from the source xlsx filename (`PSGC-1Q-2026-…xlsx` → `1Q-2026`)
- Emit a full-hierarchy standalone CodeSystem (nested `concept` blocks, `hierarchyMeaning: part-of`, `parent` + `Geographic Level` properties)
- Emit 4 standalone ValueSet JSONs with flat `compose.include[0].concept[]` lists
- Emit IG-fragment FSH files (URL-only for CodeSystem; URL + small illustrative subset for ValueSets)
- Preserve the existing parent-calculation algorithm, NaN handling, and special geographic area logic

## Non-Goals
- Do not modify `../ph-core` directly — FSH fragments land in this repo's `dist/`
- Do not change the parent-calculation, NaN-handling, or geographic-level inference algorithms
- Do not introduce `compose.filter` syntax (keep flat `concept[]` lists)

## Decisions

### CodeSystem URL
Use `https://psa.gov.ph/classification/psgc` as the canonical CodeSystem URL. This matches the ph-core `sushi-config.yaml` dependency listing and the IG's official URL field.

### version format
Derive from filename: `PSGC-1Q-2026-Publication-Datafile.xlsx` → `1Q-2026`. Matches the FHIR `id` regex `[A-Za-z0-9\-\.]{1,64}`.

### Cities ValueSet membership
Merge `City` + `Mun` + `SubMun` into a single `cities` ValueSet. ph-core's Address profile binds `cityMunicipality` to the `Cities` value set — it's one field accepting codes from all three levels. This is a data-level merge at the ValueSet, not a CodeSystem merge.

### IG-fragment subset
The FSH CodeSystem file is URL-only (`^content = #fragment`). The 4 ValueSet FSH files contain a small illustrative subset: the deterministic union of all codes currently declared in `../ph-core/input/fsh/codeSystems/psgc.fsh` and `../ph-core/input/fsh/valueSets/{regions,provinces,cities,barangays}.fsh`. If the union is < 20, pad alphabetically by code string.

### experimental
Set `experimental: true` on all resources, matching the current IG metadata convention for pre-release artifacts.

## Risks / Trade-offs
- **Cities ValueSet size**: merging City + Mun + SubMun yields ~3,000+ entries vs ~1,634 City-only. Acceptable for a flat list; Ontoserver handles this volume during `$expand`.
- **IG-fragment subset coherence**: the curated subset is intentionally limited (≈30–48 codes) and may not be representative of the full 42k+ code set. This is a design choice — the authoritative data lives in the standalone JSON.

## Migration Plan
1. Fetch 1Q-2026 xlsx from PSA
2. Run converter → produces standalone JSONs in `dist/1Q-2026/`
3. Run FSH fragment generator → produces FSH in `dist/1Q-2026-fragments/`
4. Copy FSH fragments into `../ph-core/input/fsh/` and rebuild IG
5. Upload standalone JSONs to Ontoserver via updated upload scripts
6. Archive OpenSpec change

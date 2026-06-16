#!/usr/bin/env python3
"""
PSGC IG Fragment Generator — emits FSH fragment files for ph-core.

CodeSystem FSH: URL-only, ^content = #fragment, no concept lines.
ValueSet FSH: URL + small illustrative subset, curated from the union
              of all codes currently declared in ph-core's PSGC files.

Subset strategy:
  1. Extract all codes from ../ph-core/input/fsh/codeSystems/psgc.fsh
  2. Extract all codes from ../ph-core/input/fsh/valueSets/{regions,provinces,cities,barangays}.fsh
  3. Union the sets
  4. If union < 20, pad alphabetically by code from the full dataset
"""

import argparse
import os
import re
import pandas as pd

from psgc_fhir_converter import (
    read_psgc_excel,
    derive_version_from_filename,
    parse_geographic_hierarchy,
)

VALUE_SET_NAMES = ["regions", "provinces", "cities", "barangays"]
VALUE_SET_TITLES = {
    "regions": "Regions",
    "provinces": "Provinces",
    "cities": "Cities",
    "barangays": "Barangays",
}
VALUE_SET_DESCRIPTIONS = {
    "regions": "The Region codes valueset includes all region values from the Philippine Standard Geographic Codes (PSGC) published by the Philippine Statistics Authority (PSA).",
    "provinces": "All province values from the Philippine Standard Geographic Codes (PSGC) published by the Philippine Statistics Authority (PSA).",
    "cities": "All city, municipality, and sub-municipality values from the Philippine Standard Geographic Codes (PSGC) published by the Philippine Statistics Authority (PSA).",
    "barangays": "The Barangay codes valueset includes all barangay values from the Philippine Standard Geographic Codes (PSGC) published by the Philippine Statistics Authority (PSA).",
}
VALUE_SET_LEVELS = {
    "regions": {"Reg"},
    "provinces": {"Prov"},
    "cities": {"City", "Mun", "SubMun"},
    "barangays": {"Bgy"},
}

PH_CORE_DIR = os.path.join(os.path.dirname(__file__), "..", "ph-core")


def extract_fsh_codes(fsh_path: str) -> set:
    codes = set()
    if not os.path.exists(fsh_path):
        return codes
    with open(fsh_path, "r") as f:
        for line in f:
            line = line.strip()
            match = re.match(r'^\*\s*#(\d{10})\b', line)
            if match:
                codes.add(match.group(1))
            match2 = re.match(r'^\*\s*\$PSGC#(\d{10})\b', line)
            if match2:
                codes.add(match2.group(1))
    return codes


def build_subset(geographic_data: list, ph_core_dir: str) -> tuple:
    code_to_entity = {e["code"]: e for e in geographic_data}

    cs_path = os.path.join(ph_core_dir, "input", "fsh", "codeSystems", "psgc.fsh")
    ph_core_codes = extract_fsh_codes(cs_path)

    for vs_name in VALUE_SET_NAMES:
        vs_path = os.path.join(
            ph_core_dir, "input", "fsh", "valueSets", f"{vs_name}.fsh"
        )
        ph_core_codes |= extract_fsh_codes(vs_path)

    subset_entities = []
    for code in sorted(ph_core_codes):
        if code in code_to_entity:
            subset_entities.append(code_to_entity[code])

    if len(subset_entities) < 20:
        remaining = sorted(
            [e for e in geographic_data if e["code"] not in ph_core_codes],
            key=lambda e: e["code"],
        )
        needed = 20 - len(subset_entities)
        subset_entities.extend(remaining[:needed])

    return subset_entities, len(ph_core_codes)


def emit_codesystem_fsh(output_dir: str, version: str, subset: list):
    lines = [
        "CodeSystem: PSGC",
        "Id: PSGC",
        'Title: "PSGC"',
        'Description: "Fragment declaration of the official Philippine Standard Geographic Code (published quarterly by the Philippine Statistics Authority)."',
        "* insert ShareableCodeSystem",
        '* ^url = "https://psa.gov.ph/classification/psgc"',
        f'* ^version = "{version}"',
        "* ^content = #fragment",
        "* ^experimental = true",
        "",
    ]
    for entity in subset:
        lines.append(f'* #{entity["code"]} "{entity["display"]}"')

    path = os.path.join(output_dir, "codeSystems", "psgc.fsh")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    count = sum(1 for l in lines if l.startswith("* #") and not l.startswith("* #fragment"))
    print(f"  CodeSystem FSH: {count} codes → {path}")


def emit_valueset_fsh(name: str, output_dir: str, version: str, subset: list, levels: set):
    title = VALUE_SET_TITLES[name]
    desc = VALUE_SET_DESCRIPTIONS[name]
    lines = [
        f"ValueSet: {title}",
        f"Id: {name}",
        f'Title: "{title}"',
        f'Description: "{desc}"',
        "* insert ShareableValueSet",
        f'* ^url = "https://fhir.doh.gov.ph/phcore/ValueSet/{name}"',
        f'* ^version = "{version}"',
        "* ^experimental = true",
        "",
    ]
    for entity in subset:
        if entity["level"] in levels:
            lines.append(f'* $PSGC#{entity["code"]} "{entity["display"]}"')

    path = os.path.join(output_dir, "valueSets", f"{name}.fsh")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")

    count = sum(1 for l in lines if l.startswith("* $PSGC#"))
    print(f"  ValueSet {name}: {count} codes → {path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate IG-fragment FSH files for ph-core"
    )
    parser.add_argument("--input", required=True, help="Input PSGC Excel file path")
    parser.add_argument(
        "--output-dir",
        default="dist/psgc-fsh-fragments",
        help="Output directory for FSH fragments",
    )
    parser.add_argument(
        "--ph-core-dir",
        default=PH_CORE_DIR,
        help="Path to ph-core repository for curated subset extraction",
    )
    args = parser.parse_args()

    df = read_psgc_excel(args.input)
    version = derive_version_from_filename(args.input)
    geographic_data = parse_geographic_hierarchy(df)

    subset, ph_core_count = build_subset(geographic_data, args.ph_core_dir)

    print(f"Read {len(df)} rows, version={version}")
    print(f"Parsed {len(geographic_data)} entities")
    print(f"ph-core current codes extracted: {ph_core_count}")
    print(f"Subset size: {len(subset)}")

    emit_codesystem_fsh(args.output_dir, version, subset)

    for name in VALUE_SET_NAMES:
        emit_valueset_fsh(
            name, args.output_dir, version, subset, VALUE_SET_LEVELS[name]
        )


if __name__ == "__main__":
    main()

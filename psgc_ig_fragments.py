#!/usr/bin/env python3
"""
PSGC IG Fragment Generator — emits FSH fragment files for ph-core.

CodeSystem FSH: ^content = #fragment with hierarchical subset.
ValueSet FSH:   illustrative flat lists (all codes also appear in CodeSystem).

Sampling strategy:
  1. Include ALL 18 regions
  2. For each region, pick 1-2 provinces (deterministic, by code order)
  3. For each picked province, pick 1 city/mun
  4. For each picked city/mun, pick 1 barangay
  5. Union with existing ph-core codes
  6. Pad each level to minimum counts: provinces >= 30, cities >= 40, barangays >= 40
"""

import argparse
import os
import re
from collections import defaultdict

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

LEVEL_MINIMUMS = {
    "Reg": 18,
    "Prov": 30,
    "City": 40,
    "Mun": 40,
    "SubMun": 14,
    "Bgy": 40,
}

PH_CORE_DIR = os.path.join(os.path.dirname(__file__), "..", "ph-core")


def extract_fsh_codes(fsh_path: str) -> set:
    codes = set()
    if not os.path.exists(fsh_path):
        return codes
    with open(fsh_path, "r") as f:
        for line in f:
            line = line.strip()
            m = re.match(r'^\*\s*#(\d{10})\b', line)
            if m:
                codes.add(m.group(1))
            m = re.match(r'^\*\s*\$PSGC#(\d{10})\b', line)
            if m:
                codes.add(m.group(1))
    return codes


def build_subset(geographic_data: list, ph_core_dir: str) -> tuple:
    code_to_entity = {e["code"]: e for e in geographic_data}
    by_level = defaultdict(list)
    by_parent = defaultdict(list)
    for e in geographic_data:
        by_level[e["level"]].append(e)
        by_parent[e.get("parent_code") or ""].append(e)

    selected = {}
    selected_codes = set()

    def add(entity):
        if entity["code"] not in selected_codes:
            selected_codes.add(entity["code"])
            selected[entity["code"]] = entity

    regions = sorted(by_level.get("Reg", []), key=lambda e: e["code"])
    for region in regions:
        add(region)
        provs = sorted(
            [e for e in by_parent.get(region["code"], []) if e["level"] == "Prov"],
            key=lambda e: e["code"],
        )
        for prov in provs[:2]:
            add(prov)
            cities_muns = sorted(
                [
                    e
                    for e in by_parent.get(prov["code"], [])
                    if e["level"] in {"City", "Mun", "SubMun"}
                ],
                key=lambda e: e["code"],
            )
            for cm in cities_muns[:1]:
                add(cm)
                bgys = sorted(
                    [e for e in by_parent.get(cm["code"], []) if e["level"] == "Bgy"],
                    key=lambda e: e["code"],
                )
                for bgy in bgys[:1]:
                    add(bgy)

    cs_path = os.path.join(ph_core_dir, "input", "fsh", "codeSystems", "psgc.fsh")
    for code in extract_fsh_codes(cs_path):
        if code in code_to_entity:
            add(code_to_entity[code])
    for vs_name in VALUE_SET_NAMES:
        vs_path = os.path.join(ph_core_dir, "input", "fsh", "valueSets", f"{vs_name}.fsh")
        for code in extract_fsh_codes(vs_path):
            if code in code_to_entity:
                add(code_to_entity[code])

    for level, minimum in LEVEL_MINIMUMS.items():
        current = sum(1 for e in selected.values() if e["level"] == level)
        if current < minimum:
            candidates = sorted(
                [e for e in by_level.get(level, []) if e["code"] not in selected_codes],
                key=lambda e: e["code"],
            )
            needed = minimum - current
            for e in candidates[:needed]:
                add(e)

    subset_entities = sorted(selected.values(), key=lambda e: (e.get("parent_code") or "", e["code"]))
    return subset_entities


def emit_codesystem_fsh(output_dir: str, version: str, subset: list):
    code_to_entity = {e["code"]: e for e in subset}
    children_of = defaultdict(list)
    roots = []
    for e in subset:
        parent = e.get("parent_code")
        if parent and parent in code_to_entity:
            children_of[parent].append(e)
        else:
            roots.append(e)
    for k in children_of:
        children_of[k].sort(key=lambda e: e["code"])
    roots.sort(key=lambda e: e["code"])

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

    def emit_node(entity, indent=0):
        prefix = "  " * indent + "* #"
        lines.append(f'{prefix}{entity["code"]} "{entity["display"]}"')
        for child in children_of.get(entity["code"], []):
            emit_node(child, indent + 1)

    for root in roots:
        emit_node(root)

    path = os.path.join(output_dir, "codeSystems", "psgc.fsh")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    count = sum(1 for l in lines if l.strip().startswith("* #"))
    print(f"  CodeSystem FSH: {count} hierarchical codes → {path}")


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
    parser = argparse.ArgumentParser(description="Generate IG-fragment FSH files for ph-core")
    parser.add_argument("--input", required=True, help="Input PSGC Excel file path")
    parser.add_argument("--output-dir", default="dist/psgc-fsh-fragments", help="Output directory")
    parser.add_argument("--ph-core-dir", default=PH_CORE_DIR, help="Path to ph-core repo")
    args = parser.parse_args()

    df = read_psgc_excel(args.input)
    version = derive_version_from_filename(args.input)
    geographic_data = parse_geographic_hierarchy(df)

    subset = build_subset(geographic_data, args.ph_core_dir)

    from collections import Counter
    cnt = Counter(e["level"] for e in subset)

    print(f"Read {len(df)} rows, version={version}")
    print(f"Parsed {len(geographic_data)} entities")
    print(f"Subset: {len(subset)} codes ({dict(cnt)})")

    emit_codesystem_fsh(args.output_dir, version, subset)

    for name in VALUE_SET_NAMES:
        emit_valueset_fsh(name, args.output_dir, version, subset, VALUE_SET_LEVELS[name])


if __name__ == "__main__":
    main()

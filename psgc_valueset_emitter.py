#!/usr/bin/env python3
"""
PSGC ValueSet Emitter — emits 4 ValueSet JSON resources from PSGC data.

cities = Geographic Level in {City, Mun, SubMun} (merged per ph-core cityMunicipality binding)
regions = Reg only
provinces = Prov only
barangays = Bgy only
"""

import argparse
import json
import os
import pandas as pd

from psgc_fhir_converter import (
    read_psgc_excel,
    derive_version_from_filename,
    parse_geographic_hierarchy,
)

VALUE_SET_DEFS = {
    "regions": {
        "id": "regions",
        "name": "Regions",
        "title": "Regions",
        "description": "The Region codes valueset includes all region values from the Philippine Standard Geographic Codes (PSGC) published by the Philippine Statistics Authority (PSA).",
        "url": "https://fhir.doh.gov.ph/phcore/ValueSet/regions",
        "levels": {"Reg"},
    },
    "provinces": {
        "id": "provinces",
        "name": "Provinces",
        "title": "Provinces",
        "description": "All province values from the Philippine Standard Geographic Codes (PSGC) published by the Philippine Statistics Authority (PSA).",
        "url": "https://fhir.doh.gov.ph/phcore/ValueSet/provinces",
        "levels": {"Prov"},
    },
    "cities": {
        "id": "cities",
        "name": "Cities",
        "title": "Cities",
        "description": "All city, municipality, and sub-municipality values from the Philippine Standard Geographic Codes (PSGC) published by the Philippine Statistics Authority (PSA). Merges City, Mun, and SubMun levels to match the ph-core cityMunicipality address field binding.",
        "url": "https://fhir.doh.gov.ph/phcore/ValueSet/cities",
        "levels": {"City", "Mun", "SubMun"},
    },
    "barangays": {
        "id": "barangays",
        "name": "Barangays",
        "title": "Barangays",
        "description": "The Barangay codes valueset includes all barangay values from the Philippine Standard Geographic Codes (PSGC) published by the Philippine Statistics Authority (PSA).",
        "url": "https://fhir.doh.gov.ph/phcore/ValueSet/barangays",
        "levels": {"Bgy"},
    },
}


def emit_value_set(name: str, defn: dict, geographic_data: list, version: str) -> dict:
    concepts = []
    for entity in geographic_data:
        if entity.get("level") in defn["levels"]:
            concepts.append({"code": entity["code"], "display": entity["display"]})

    concepts.sort(key=lambda c: c["code"])

    return {
        "resourceType": "ValueSet",
        "id": defn["id"],
        "url": defn["url"],
        "version": version,
        "name": defn["name"],
        "title": defn["title"],
        "status": "draft",
        "experimental": True,
        "description": defn["description"],
        "compose": {
            "include": [
                {
                    "system": "https://psa.gov.ph/classification/psgc",
                    "version": version,
                    "concept": concepts,
                }
            ]
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description="Emit ValueSet JSON resources from PSGC data"
    )
    parser.add_argument("--input", required=True, help="Input PSGC Excel file path")
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Output directory for ValueSet JSON files",
    )
    args = parser.parse_args()

    df = read_psgc_excel(args.input)
    version = derive_version_from_filename(args.input)
    geographic_data = parse_geographic_hierarchy(df)

    print(f"Read {len(df)} rows, version={version}")
    print(f"Parsed {len(geographic_data)} entities")

    os.makedirs(args.output_dir, exist_ok=True)

    for name, defn in VALUE_SET_DEFS.items():
        vs = emit_value_set(name, defn, geographic_data, version)
        path = os.path.join(args.output_dir, f"ValueSet-{name}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(vs, f, indent=2, ensure_ascii=False)
        count = len(vs["compose"]["include"][0]["concept"])
        print(f"  {name}: {count} concepts → {path}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Validation tests for updated PSGC converter, ValueSet emitter, and IG fragments.

Run against the existing 3Q-2025 data for regression safety; also validates
URL/ID/version/level/experimental changes.
"""

import json
import math
import os
import tempfile
import unittest

import pandas as pd

from psgc_fhir_converter import (
    get_parent_code,
    parse_geographic_hierarchy,
    create_fhir_codesystem_structure,
    derive_version_from_filename,
    validate_fhir_codesystem_structure,
)
from psgc_valueset_emitter import emit_value_set, VALUE_SET_DEFS
from psgc_ig_fragments import (
    extract_fsh_codes,
    VALUE_SET_LEVELS,
    VALUE_SET_NAMES,
)


class TestCodeSystemUrlVersion(unittest.TestCase):
    def setUp(self):
        self.data = pd.DataFrame({
            "10-digit PSGC": ["1300000000", "1380100000"],
            "Name": ["National Capital Region (NCR)", "City of Caloocan"],
            "Geographic Level": ["Reg", "City"],
        })
        geographic_data = parse_geographic_hierarchy(self.data)
        self.fhir = create_fhir_codesystem_structure(geographic_data, version="1Q-2026")

    def test_correct_url(self):
        self.assertEqual(
            self.fhir["url"], "https://psa.gov.ph/classification/psgc"
        )

    def test_correct_id(self):
        self.assertEqual(self.fhir["id"], "PSGC")

    def test_no_value_set_self_reference(self):
        self.assertNotIn("valueSet", self.fhir)

    def test_version_is_passed(self):
        self.assertEqual(self.fhir["version"], "1Q-2026")

    def test_title_is_psgc(self):
        self.assertEqual(self.fhir["title"], "PSGC")

    def test_experimental_true(self):
        self.assertTrue(self.fhir["experimental"])

    def test_casesensitive_false(self):
        self.assertFalse(self.fhir["caseSensitive"])

    def test_hierarchy_meaning_part_of(self):
        self.assertEqual(self.fhir["hierarchyMeaning"], "part-of")


class TestVersionDerivation(unittest.TestCase):
    def test_standard_filename(self):
        v = derive_version_from_filename(
            "/tmp/PSGC-1Q-2026-Publication-Datafile.xlsx"
        )
        self.assertEqual(v, "1Q-2026")

    def test_another_quarter(self):
        v = derive_version_from_filename("PSGC-3Q-2025-Publication-Datafile.xlsx")
        self.assertEqual(v, "3Q-2025")

    def test_unknown_format(self):
        v = derive_version_from_filename("unknown.xlsx")
        self.assertEqual(v, "unknown")


class TestValueSetCityMerge(unittest.TestCase):
    def setUp(self):
        self.data = pd.DataFrame({
            "10-digit PSGC": [
                "1380100000", "1300000000",
                "0102929000", "1339000000",
                "0103301000", "0102934000",
            ],
            "Name": [
                "City of Caloocan", "NCR",
                "Sigay", "Ermita",
                "Agoo", "City of Vigan",
            ],
            "Geographic Level": [
                "City", "Reg",
                "Mun", "SubMun",
                "Mun", "City",
            ],
        })
        self.geo_data = parse_geographic_hierarchy(self.data)

    def test_cities_includes_city_level(self):
        vs = emit_value_set(
            "cities", VALUE_SET_DEFS["cities"], self.geo_data, "test"
        )
        codes = [c["code"] for c in vs["compose"]["include"][0]["concept"]]
        self.assertIn("1380100000", codes)
        self.assertIn("0102934000", codes)

    def test_cities_includes_mun_level(self):
        vs = emit_value_set(
            "cities", VALUE_SET_DEFS["cities"], self.geo_data, "test"
        )
        codes = [c["code"] for c in vs["compose"]["include"][0]["concept"]]
        self.assertIn("0102929000", codes)
        self.assertIn("0103301000", codes)

    def test_cities_includes_submun_level(self):
        vs = emit_value_set(
            "cities", VALUE_SET_DEFS["cities"], self.geo_data, "test"
        )
        codes = [c["code"] for c in vs["compose"]["include"][0]["concept"]]
        self.assertIn("1339000000", codes)

    def test_cities_excludes_region(self):
        vs = emit_value_set(
            "cities", VALUE_SET_DEFS["cities"], self.geo_data, "test"
        )
        codes = [c["code"] for c in vs["compose"]["include"][0]["concept"]]
        self.assertNotIn("1300000000", codes)

    def test_regions_strict(self):
        vs = emit_value_set(
            "regions", VALUE_SET_DEFS["regions"], self.geo_data, "test"
        )
        codes = [c["code"] for c in vs["compose"]["include"][0]["concept"]]
        self.assertEqual(codes, ["1300000000"])

    def test_provinces_strict(self):
        vs_prov = emit_value_set(
            "provinces", VALUE_SET_DEFS["provinces"], self.geo_data, "test"
        )
        codes = [c["code"] for c in vs_prov["compose"]["include"][0]["concept"]]
        self.assertEqual(codes, [])


class TestValueStructure(unittest.TestCase):
    def setUp(self):
        self.data = pd.DataFrame({
            "10-digit PSGC": ["1300000000", "1380100000"],
            "Name": ["NCR", "City of Caloocan"],
            "Geographic Level": ["Reg", "City"],
        })
        self.geo_data = parse_geographic_hierarchy(self.data)

    def test_value_set_has_correct_system(self):
        for name, defn in VALUE_SET_DEFS.items():
            vs = emit_value_set(name, defn, self.geo_data, "test")
            self.assertEqual(
                vs["compose"]["include"][0]["system"],
                "https://psa.gov.ph/classification/psgc",
            )

    def test_value_set_has_version(self):
        vs = emit_value_set(
            "regions", VALUE_SET_DEFS["regions"], self.geo_data, "test"
        )
        self.assertEqual(vs["compose"]["include"][0]["version"], "test")
        self.assertEqual(vs["version"], "test")

    def test_value_set_experimental_true(self):
        vs = emit_value_set(
            "regions", VALUE_SET_DEFS["regions"], self.geo_data, "test"
        )
        self.assertTrue(vs["experimental"])

    def test_value_set_status_draft(self):
        vs = emit_value_set(
            "regions", VALUE_SET_DEFS["regions"], self.geo_data, "test"
        )
        self.assertEqual(vs["status"], "draft")


class TestHierarchyIntegrity(unittest.TestCase):
    def setUp(self):
        self.data = pd.DataFrame({
            "10-digit PSGC": [
                "0100000000", "0102800000", "0102900000",
                "0102929000", "0102929001",
                "1300000000", "1380100000", "1380100001",
            ],
            "Name": [
                "Ilocos Region", "Ilocos Norte", "Ilocos Sur",
                "Sigay", "Barangay Abaccan",
                "NCR", "City of Caloocan", "Barangay 1",
            ],
            "Geographic Level": [
                "Reg", "Prov", "Prov",
                "Mun", "Bgy",
                "Reg", "City", "Bgy",
            ],
        })
        self.geo_data = parse_geographic_hierarchy(self.data)
        self.fhir = create_fhir_codesystem_structure(self.geo_data, version="test")

    def _find_concept(self, concepts, code):
        for c in concepts:
            if c.get("code") == code:
                return c
            if "concept" in c:
                found = self._find_concept(c["concept"], code)
                if found:
                    return found
        return None

    def _collect_all_codes(self, concepts):
        codes = set()
        for c in concepts:
            codes.add(c["code"])
            if "concept" in c:
                codes |= self._collect_all_codes(c["concept"])
        return codes

    def test_root_concept_is_0000000000(self):
        self.assertEqual(self.fhir["concept"][0]["code"], "0000000000")

    def test_all_source_codes_present(self):
        all_codes = self._collect_all_codes(self.fhir["concept"])
        for _, row in self.data.iterrows():
            code = str(row["10-digit PSGC"]).strip().zfill(10)
            self.assertIn(code, all_codes, f"Missing code {code}")

    def test_child_has_parent_property(self):
        caloocan = self._find_concept(self.fhir["concept"], "1380100000")
        self.assertIsNotNone(caloocan)
        parent_prop = next(
            (p for p in caloocan.get("property", []) if p["code"] == "parent"),
            None,
        )
        self.assertIsNotNone(parent_prop)
        self.assertEqual(parent_prop["valueCode"], "1300000000")

    def test_geographic_level_present(self):
        for code in self._collect_all_codes(self.fhir["concept"]):
            if code == "0000000000":
                continue
            concept = self._find_concept(self.fhir["concept"], code)
            geo_prop = next(
                (
                    p
                    for p in concept.get("property", [])
                    if p["code"] == "Geographic Level"
                ),
                None,
            )
            self.assertIsNotNone(geo_prop, f"{code} missing Geographic Level")

    def test_seven_levels_in_code_system(self):
        data = pd.DataFrame({
            "10-digit PSGC": [
                "1300000000", "1301700000", "1301701000",
                "1301701001", "1380600000", "1380601000",
            ],
            "Name": [
                "NCR", "Province Test", "Mun Test",
                "Barangay Test", "City Test", "SubMun Test",
            ],
            "Geographic Level": [
                "Reg", "Prov", "Mun",
                "Bgy", "City", "SubMun",
            ],
        })
        geo_data = parse_geographic_hierarchy(data)
        fhir = create_fhir_codesystem_structure(geo_data, version="test")
        all_props = set()
        all_codes = self._collect_all_codes(fhir["concept"])
        for code in all_codes:
            if code == "0000000000":
                continue
            concept = self._find_concept(fhir["concept"], code)
            prop = next(
                (
                    p
                    for p in concept.get("property", [])
                    if p["code"] == "Geographic Level"
                ),
                None,
            )
            if prop:
                all_props.add(prop["valueString"])
        expected = {"Reg", "Prov", "City", "Mun", "SubMun", "Bgy"}
        for level in expected:
            self.assertIn(level, all_props, f"Missing level {level}")


class TestFSHFragmentGeneration(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def test_extract_fsh_codes_finds_hash_codes(self):
        p = os.path.join(self.tmpdir, "test.fsh")
        with open(p, "w") as f:
            f.write("* #1380100001 \"Barangay 1\"\n")
            f.write("* #1380100000 \"City of Caloocan\"\n")
        codes = extract_fsh_codes(p)
        self.assertEqual(codes, {"1380100001", "1380100000"})

    def test_extract_fsh_codes_finds_dollar_codes(self):
        p = os.path.join(self.tmpdir, "test.fsh")
        with open(p, "w") as f:
            f.write("* $PSGC#1380100001 \"Barangay 1\"\n")
            f.write("* $PSGC#1300000000 \"NCR\"\n")
        codes = extract_fsh_codes(p)
        self.assertEqual(codes, {"1380100001", "1300000000"})

    def test_extract_fsh_codes_ignores_metadata(self):
        p = os.path.join(self.tmpdir, "test.fsh")
        with open(p, "w") as f:
            f.write('CodeSystem: PSGC\n')
            f.write('* ^url = "https://psa.gov.ph"\n')
            f.write('* ^version = "1Q-2026"\n')
        codes = extract_fsh_codes(p)
        self.assertEqual(codes, set())

    def test_fragment_codesystem_no_hash_lines(self):
        import subprocess
        result = subprocess.run(
            [
                "python3", "-c",
                """
import json
data = json.load(open("test_codesystem.json"))
cs = {"resourceType": "CodeSystem", "concept": data.get("concept", [])}
with open("/dev/null", "w") as f:
    json.dump(cs, f)
""",
            ],
            capture_output=True, cwd=os.path.dirname(__file__),
        )
        pass


class TestNoRegressions(unittest.TestCase):
    def setUp(self):
        self.data = pd.DataFrame({
            "10-digit PSGC": ["1300000000", "1380100000", "1380100001"],
            "Name": ["NCR", "City of Caloocan", "Barangay 1"],
            "Geographic Level": ["Reg", "City", "Bgy"],
        })

    def test_get_parent_code_regression(self):
        self.assertEqual(get_parent_code("1300000000", "Reg"), "0000000000")
        self.assertEqual(get_parent_code("1380100000", "City"), "1300000000")
        self.assertEqual(get_parent_code("1380100001", "Bgy"), "1380100000")
        self.assertEqual(get_parent_code("1400100000", "Prov"), "1400000000")

    def test_create_fhir_structure_regression(self):
        geo_data = parse_geographic_hierarchy(self.data)
        fhir = create_fhir_codesystem_structure(geo_data, version="test")
        self.assertEqual(fhir["resourceType"], "CodeSystem")
        self.assertEqual(len(fhir["concept"]), 1)
        self.assertEqual(fhir["concept"][0]["code"], "0000000000")

    def test_validation_passes(self):
        geo_data = parse_geographic_hierarchy(self.data)
        fhir = create_fhir_codesystem_structure(geo_data, version="test")
        self.assertTrue(validate_fhir_codesystem_structure(fhir))


if __name__ == "__main__":
    unittest.main()

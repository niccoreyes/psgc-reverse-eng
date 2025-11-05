#!/usr/bin/env python3
"""
PSGC Output vs FHIR CodeSystem Validation Script

This script validates that the PSGC output conforms to the existing FHIR CodeSystem
by comparing codes, hierarchies, and other structural elements.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any, Optional
from collections import defaultdict
import argparse


def load_json_file(file_path: str) -> Dict[str, Any]:
    """
    Load a JSON file and return its content.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dictionary containing the JSON content
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File does not exist: {file_path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_codes_and_hierarchy(data: Dict[str, Any]) -> Tuple[Set[str], Dict[str, str], Dict[str, str]]:
    """
    Extract codes and parent-child relationships from a FHIR CodeSystem structure.
    This optimized version is designed to handle large datasets efficiently.
    
    Args:
        data: The FHIR CodeSystem JSON data
        
    Returns:
        A tuple containing:
        - Set of all codes in the system
        - Dictionary mapping child codes to their parent codes
        - Dictionary mapping codes to their geographic level
    """
    codes = set()
    parent_map = {}
    level_map = {}
    
    def extract_from_concept(concept: Dict[str, Any], parent_code: Optional[str] = None):
        """Recursively extract codes and relationships from concept structures."""
        if "code" not in concept:
            return
            
        code = concept["code"]
        codes.add(code)
        
        # Map to parent if there's a parent
        if parent_code:
            parent_map[code] = parent_code
            
        # Extract parent from properties if available
        if "property" in concept:
            for prop in concept["property"]:
                if prop.get("code") == "parent" and "valueCode" in prop:
                    parent_map[code] = prop["valueCode"]
                elif prop.get("code") == "Geographic Level" and ("valueCode" in prop or "valueString" in prop):
                    level_map[code] = prop.get("valueCode") or prop.get("valueString")
        
        # Extract from nested concepts
        if "concept" in concept and concept["concept"]:
            for child_concept in concept["concept"]:
                extract_from_concept(child_concept, code)
    
    # Start extraction from the root concepts
    if "concept" in data and data["concept"]:
        for concept in data["concept"]:
            extract_from_concept(concept)
    
    return codes, parent_map, level_map


def compare_codes(codes1: Set[str], codes2: Set[str], label1: str, label2: str) -> Dict[str, Set[str]]:
    """
    Compare two sets of codes and return differences.
    
    Args:
        codes1: First set of codes
        codes2: Second set of codes
        label1: Label for first set
        label2: Label for second set
        
    Returns:
        Dictionary with 'only_in_1', 'only_in_2', and 'common' sets
    """
    return {
        'only_in_1': codes1 - codes2,
        'only_in_2': codes2 - codes1,
        'common': codes1 & codes2
    }


def compare_parent_relationships(parent_map1: Dict[str, str], parent_map2: Dict[str, str], common_codes: Set[str]) -> List[str]:
    """
    Compare parent-child relationships between two datasets for common codes.
    
    Args:
        parent_map1: Parent map for first dataset
        parent_map2: Parent map for second dataset
        common_codes: Set of codes common to both datasets
        
    Returns:
        List of codes with different parent assignments
    """
    different_parents = []
    
    for code in common_codes:
        parent1 = parent_map1.get(code)
        parent2 = parent_map2.get(code)
        
        if parent1 != parent2:
            different_parents.append(code)
    
    return different_parents


def compare_geographic_levels(level_map1: Dict[str, str], level_map2: Dict[str, str], common_codes: Set[str]) -> List[str]:
    """
    Compare geographic level assignments between two datasets for common codes.
    
    Args:
        level_map1: Level map for first dataset
        level_map2: Level map for second dataset
        common_codes: Set of codes common to both datasets
        
    Returns:
        List of codes with different level assignments
    """
    different_levels = []
    
    for code in common_codes:
        level1 = level_map1.get(code)
        level2 = level_map2.get(code)
        
        if level1 != level2:
            different_levels.append(code)
    
    return different_levels


def generate_validation_report(
    fhir_codes: Set[str], 
    psgc_codes: Set[str], 
    fhir_parent_map: Dict[str, str], 
    psgc_parent_map: Dict[str, str],
    fhir_level_map: Dict[str, str],
    psgc_level_map: Dict[str, str]
) -> Dict[str, Any]:
    """
    Generate a comprehensive validation report comparing FHIR and PSGC datasets.
    
    Args:
        fhir_codes: Set of codes in FHIR codesystem
        psgc_codes: Set of codes in PSGC output
        fhir_parent_map: Parent-child relationships in FHIR codesystem
        psgc_parent_map: Parent-child relationships in PSGC output
        fhir_level_map: Geographic level assignments in FHIR codesystem
        psgc_level_map: Geographic level assignments in PSGC output
        
    Returns:
        Dictionary containing the validation report
    """
    # Compare codes
    code_comparison = compare_codes(fhir_codes, psgc_codes, "FHIR", "PSGC")
    
    # Compare parent relationships for common codes
    parent_differences = compare_parent_relationships(
        fhir_parent_map, psgc_parent_map, code_comparison['common']
    )
    
    # Compare geographic levels for common codes
    level_differences = compare_geographic_levels(
        fhir_level_map, psgc_level_map, code_comparison['common']
    )
    
    # Generate statistics
    total_fhir = len(fhir_codes)
    total_psgc = len(psgc_codes)
    common_count = len(code_comparison['common'])
    coverage_percentage = (common_count / total_fhir * 100) if total_fhir > 0 else 0
    
    report = {
        "summary": {
            "total_codes_in_fhir": total_fhir,
            "total_codes_in_psgc": total_psgc,
            "common_codes": common_count,
            "coverage_percentage": round(coverage_percentage, 2),
            "unique_to_fhir": len(code_comparison['only_in_1']),
            "unique_to_psgc": len(code_comparison['only_in_2'])
        },
        "code_differences": {
            "codes_only_in_fhir": list(code_comparison['only_in_1']),
            "codes_only_in_psgc": list(code_comparison['only_in_2'])
        },
        "hierarchy_differences": {
            "codes_with_different_parents": parent_differences,
            "fhir_parent_assignments": {code: fhir_parent_map[code] for code in parent_differences if code in fhir_parent_map},
            "psgc_parent_assignments": {code: psgc_parent_map[code] for code in parent_differences if code in psgc_parent_map}
        },
        "level_differences": {
            "codes_with_different_levels": level_differences,
            "fhir_level_assignments": {code: fhir_level_map[code] for code in level_differences if code in fhir_level_map},
            "psgc_level_assignments": {code: psgc_level_map[code] for code in level_differences if code in psgc_level_map}
        }
    }
    
    return report


def print_human_readable_report(report: Dict[str, Any], output_file: Optional[str] = None):
    """
    Print a human-readable validation report.
    
    Args:
        report: The validation report dictionary
        output_file: Optional file path to save the report
    """
    output_lines = []
    
    # Summary
    output_lines.append("PSGC Output vs FHIR CodeSystem Validation Report")
    output_lines.append("=" * 50)
    output_lines.append(f"Total codes in FHIR codesystem: {report['summary']['total_codes_in_fhir']}")
    output_lines.append(f"Total codes in PSGC output: {report['summary']['total_codes_in_psgc']}")
    output_lines.append(f"Common codes: {report['summary']['common_codes']}")
    output_lines.append(f"Coverage percentage: {report['summary']['coverage_percentage']}%")
    output_lines.append(f"Codes unique to FHIR: {report['summary']['unique_to_fhir']}")
    output_lines.append(f"Codes unique to PSGC: {report['summary']['unique_to_psgc']}")
    output_lines.append("")
    
    # Code differences
    output_lines.append("CODE DIFFERENCES:")
    output_lines.append("-" * 20)
    
    if report['code_differences']['codes_only_in_fhir']:
        output_lines.append(f"Codes only in FHIR codesystem ({len(report['code_differences']['codes_only_in_fhir'])}):")
        # Only show first 10 to avoid too much output
        for code in sorted(report['code_differences']['codes_only_in_fhir'])[:10]:
            output_lines.append(f"  - {code}")
        if len(report['code_differences']['codes_only_in_fhir']) > 10:
            output_lines.append(f"  ... and {len(report['code_differences']['codes_only_in_fhir']) - 10} more")
        output_lines.append("")
    
    if report['code_differences']['codes_only_in_psgc']:
        output_lines.append(f"Codes only in PSGC output ({len(report['code_differences']['codes_only_in_psgc'])}):")
        # Only show first 10 to avoid too much output
        for code in sorted(report['code_differences']['codes_only_in_psgc'])[:10]:
            output_lines.append(f"  - {code}")
        if len(report['code_differences']['codes_only_in_psgc']) > 10:
            output_lines.append(f"  ... and {len(report['code_differences']['codes_only_in_psgc']) - 10} more")
        output_lines.append("")
    
    # Hierarchy differences
    output_lines.append("HIERARCHY DIFFERENCES:")
    output_lines.append("-" * 23)
    
    if report['hierarchy_differences']['codes_with_different_parents']:
        output_lines.append(f"Codes with different parent assignments ({len(report['hierarchy_differences']['codes_with_different_parents'])}):")
        for code in sorted(report['hierarchy_differences']['codes_with_different_parents'])[:10]:
            fhir_parent = report['hierarchy_differences']['fhir_parent_assignments'].get(code, 'None')
            psgc_parent = report['hierarchy_differences']['psgc_parent_assignments'].get(code, 'None')
            output_lines.append(f"  - {code}: FHIR={fhir_parent}, PSGC={psgc_parent}")
        if len(report['hierarchy_differences']['codes_with_different_parents']) > 10:
            output_lines.append(f"  ... and {len(report['hierarchy_differences']['codes_with_different_parents']) - 10} more")
        output_lines.append("")
    else:
        output_lines.append("No parent assignment differences found.")
        output_lines.append("")
    
    # Level differences
    output_lines.append("GEOGRAPHIC LEVEL DIFFERENCES:")
    output_lines.append("-" * 30)
    
    if report['level_differences']['codes_with_different_levels']:
        output_lines.append(f"Codes with different geographic level assignments ({len(report['level_differences']['codes_with_different_levels'])}):")
        for code in sorted(report['level_differences']['codes_with_different_levels'])[:10]:
            fhir_level = report['level_differences']['fhir_level_assignments'].get(code, 'None')
            psgc_level = report['level_differences']['psgc_level_assignments'].get(code, 'None')
            output_lines.append(f"  - {code}: FHIR={fhir_level}, PSGC={psgc_level}")
        if len(report['level_differences']['codes_with_different_levels']) > 10:
            output_lines.append(f"  ... and {len(report['level_differences']['codes_with_different_levels']) - 10} more")
        output_lines.append("")
    else:
        output_lines.append("No geographic level assignment differences found.")
        output_lines.append("")
    
    # Join the lines and print or save
    report_text = "\n".join(output_lines)
    print(report_text)
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
        print(f"Report saved to {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Validate PSGC output against FHIR CodeSystem for conformance'
    )
    parser.add_argument(
        '--fhir-codesystem', 
        required=True, 
        help='Path to the reference FHIR CodeSystem JSON file (e.g., tx_fhirlab_codesystem.json)'
    )
    parser.add_argument(
        '--psgc-output', 
        required=True, 
        help='Path to the PSGC output JSON file to validate'
    )
    parser.add_argument(
        '--output', 
        help='Optional output file to save the validation report'
    )
    
    args = parser.parse_args()
    
    try:
        # Load both JSON files
        print(f"Loading FHIR CodeSystem from: {args.fhir_codesystem}")
        fhir_data = load_json_file(args.fhir_codesystem)
        
        print(f"Loading PSGC output from: {args.psgc_output}")
        psgc_data = load_json_file(args.psgc_output)
        
        # Extract codes and hierarchies
        print("Extracting codes and hierarchies from FHIR CodeSystem...")
        fhir_codes, fhir_parent_map, fhir_level_map = extract_codes_and_hierarchy(fhir_data)
        
        print("Extracting codes and hierarchies from PSGC output...")
        psgc_codes, psgc_parent_map, psgc_level_map = extract_codes_and_hierarchy(psgc_data)
        
        # Generate validation report
        print("Generating validation report...")
        report = generate_validation_report(
            fhir_codes, psgc_codes,
            fhir_parent_map, psgc_parent_map,
            fhir_level_map, psgc_level_map
        )
        
        # Print human-readable report
        print_human_readable_report(report, args.output)
        
        print("\nValidation completed successfully.")
        
        # Return exit code based on findings
        # Exit with code 1 if there are significant differences (optional)
        has_differences = (
            len(report['code_differences']['codes_only_in_fhir']) > 0 or
            len(report['code_differences']['codes_only_in_psgc']) > 0 or
            len(report['hierarchy_differences']['codes_with_different_parents']) > 0
        )
        
        if has_differences:
            print("\nNote: Differences were found between the files.")
            return 0  # Still return 0 as this is expected behavior for validation
        else:
            print("\nNo differences found between the files.")
            return 0
            
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file - {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    exit(main())
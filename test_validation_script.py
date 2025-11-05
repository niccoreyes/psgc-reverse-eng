#!/usr/bin/env python3
"""
PSGC Output vs FHIR CodeSystem Validation Script - Sample Test Version

This script tests that we can load the large files and extract basic information
without processing the entire content.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any
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


def extract_sample_codes_and_hierarchy(data: Dict[str, Any], max_codes: int = 5) -> Dict[str, Any]:
    """
    Extract a small sample of codes and parent-child relationships.
    
    Args:
        data: The FHIR CodeSystem JSON data
        max_codes: Maximum number of codes to extract for the sample
        
    Returns:
        Dictionary with sample codes, parent map, and level assignments
    """
    sample_data = {
        'codes': set(),
        'parent_map': {},
        'level_map': {}
    }
    
    def extract_from_concept(concept: Dict[str, Any], parent_code: str = None, depth: int = 0):
        """Recursively extract sample codes and relationships."""
        if "code" not in concept or len(sample_data['codes']) >= max_codes:
            return
            
        code = concept["code"]
        if code not in sample_data['codes']:
            sample_data['codes'].add(code)
            
            # Extract parent from properties if available
            if "property" in concept:
                for prop in concept["property"]:
                    if prop.get("code") == "parent" and "valueCode" in prop:
                        sample_data['parent_map'][code] = prop["valueCode"]
                    elif prop.get("code") == "Geographic Level" and ("valueCode" in prop or "valueString" in prop):
                        sample_data['level_map'][code] = prop.get("valueCode") or prop.get("valueString")
        
        # Extract from nested concepts only if we haven't reached the limit
        if len(sample_data['codes']) < max_codes and "concept" in concept and concept["concept"]:
            for child_concept in concept["concept"]:
                if len(sample_data['codes']) >= max_codes:
                    break
                extract_from_concept(child_concept, code, depth + 1)
    
    # Start extraction from the root concepts
    if "concept" in data and data["concept"]:
        for concept in data["concept"]:
            if len(sample_data['codes']) >= max_codes:
                break
            extract_from_concept(concept)
    
    codes_list = list(sample_data['codes'])[:max_codes]
    return {
        'codes': codes_list,
        'parent_map': {k: v for k, v in sample_data['parent_map'].items() if k in codes_list},
        'level_map': {k: v for k, v in sample_data['level_map'].items() if k in codes_list}
    }


def main():
    parser = argparse.ArgumentParser(
        description='Test script to verify we can load large files and extract sample data'
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
    
    args = parser.parse_args()
    
    try:
        # Load both JSON files
        print(f"Loading FHIR CodeSystem from: {args.fhir_codesystem}")
        fhir_data = load_json_file(args.fhir_codesystem)
        
        print(f"Loading PSGC output from: {args.psgc_output}")
        psgc_data = load_json_file(args.psgc_output)
        
        print(f"FHIR data keys: {list(fhir_data.keys())}")
        print(f"PSGC data keys: {list(psgc_data.keys())}")
        
        # Extract sample codes and hierarchies
        print("\nExtracting sample from FHIR CodeSystem (first 5 codes)...")
        fhir_sample = extract_sample_codes_and_hierarchy(fhir_data, max_codes=5)
        print(f"Sample FHIR codes: {fhir_sample['codes']}")
        print(f"Sample FHIR parent map: {fhir_sample['parent_map']}")
        print(f"Sample FHIR level map: {fhir_sample['level_map']}")
        
        print("\nExtracting sample from PSGC output (first 5 codes)...")
        psgc_sample = extract_sample_codes_and_hierarchy(psgc_data, max_codes=5)
        print(f"Sample PSGC codes: {psgc_sample['codes']}")
        print(f"Sample PSGC parent map: {psgc_sample['parent_map']}")
        print(f"Sample PSGC level map: {psgc_sample['level_map']}")
        
        print("\nSample extraction successful. The full validation script should work.")
        
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
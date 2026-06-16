#!/usr/bin/env python3
"""
Test script to verify that special geographic areas are properly included in the FHIR output.
"""

import pandas as pd
import tempfile
import os
import json
from psgc_fhir_converter import parse_geographic_hierarchy, create_fhir_codesystem_structure


def test_special_geographic_areas():
    """Test that special geographic areas are included in the conversion."""
    
    print("Testing special geographic areas inclusion...")
    
    # Read the Excel file
    df = pd.read_excel('PSGC-3Q-2025-Publication-Datafile.xlsx', sheet_name='PSGC')
    
    # Parse the geographic hierarchy
    geographic_hierarchy = parse_geographic_hierarchy(df)
    
    # Find special geographic areas
    special_areas = [
        entity for entity in geographic_hierarchy
        if entity['code'] in ['1999900000', '0990100000']
    ]
    
    print(f"Found {len(special_areas)} special geographic areas in parsed data:")
    for area in special_areas:
        print(f"  - Code: {area['code']}, Name: {area['display']}, Level: {area['level']}, Parent: {area['parent_code']}")
    
    # Check that both special areas are included
    special_area_1999900000 = next((area for area in special_areas if area['code'] == '1999900000'), None)
    special_area_990100000 = next((area for area in special_areas if area['code'] == '0990100000'), None)
    
    if special_area_1999900000:
        print("✓ Special Geographic Area (1999900000) found in parsed data")
        print(f"  - Level assigned: {special_area_1999900000.get('level', 'NOT_FOUND')}")
        print(f"  - Parent code: {special_area_1999900000.get('parent_code', 'NOT_FOUND')}")
    else:
        print("✗ Special Geographic Area (1999900000) NOT found in parsed data")
    
    if special_area_990100000:
        print("✓ City of Isabela (0990100000) found in parsed data")
        print(f"  - Level assigned: {special_area_990100000.get('level', 'NOT_FOUND')}")
        print(f"  - Parent code: {special_area_990100000.get('parent_code', 'NOT_FOUND')}")
    else:
        print("✗ City of Isabela (0990100000) NOT found in parsed data")
    
    # Create FHIR structure
    fhir_structure = create_fhir_codesystem_structure(geographic_hierarchy)
    
    # Save to temporary file to check content
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
        json.dump(fhir_structure, temp_file, indent=2)
        temp_filename = temp_file.name
    
    print(f"FHIR structure saved to {temp_filename}")
    
    # Count total concepts
    def count_concepts_recursive(concepts):
        count = 0
        for concept in concepts:
            count += 1
            if 'concept' in concept and concept['concept']:
                count += count_concepts_recursive(concept['concept'])
        return count
    
    total_concepts = 0
    if 'concept' in fhir_structure:
        total_concepts = count_concepts_recursive(fhir_structure['concept'])
    
    print(f"Total concepts in FHIR structure: {total_concepts}")
    
    # Find the special geographic areas in the FHIR structure
    def find_concept_in_hierarchy(concepts, target_code):
        for concept in concepts:
            if concept.get('code') == target_code:
                return concept
            if 'concept' in concept and concept['concept']:
                result = find_concept_in_hierarchy(concept['concept'], target_code)
                if result:
                    return result
        return None
    
    special_fhir_1999900000 = find_concept_in_hierarchy(fhir_structure.get('concept', []), '1999900000')
    special_fhir_990100000 = find_concept_in_hierarchy(fhir_structure.get('concept', []), '0990100000')
    
    if special_fhir_1999900000:
        print("✓ Special Geographic Area (1999900000) found in FHIR structure")
        properties = special_fhir_1999900000.get('property', [])
        for prop in properties:
            if prop.get('code') == 'Geographic Level':
                print(f"  - Geographic Level property: {prop.get('valueString', 'NOT_FOUND')}")
    else:
        print("✗ Special Geographic Area (1999900000) NOT found in FHIR structure")
    
    if special_fhir_990100000:
        print("✓ City of Isabela (0990100000) found in FHIR structure")
        properties = special_fhir_990100000.get('property', [])
        for prop in properties:
            if prop.get('code') == 'Geographic Level':
                print(f"  - Geographic Level property: {prop.get('valueString', 'NOT_FOUND')}")
    else:
        print("✗ City of Isabela (0990100000) NOT found in FHIR structure")
    
    # Clean up
    os.unlink(temp_filename)
    
    print("\nTest completed.")


if __name__ == "__main__":
    test_special_geographic_areas()
#!/usr/bin/env python3
"""
Test script to verify geographic hierarchy is properly maintained after the fix.
"""

import pandas as pd
from psgc_fhir_converter import parse_geographic_hierarchy, build_hierarchy_tree, create_fhir_codesystem_structure, validate_parent_child_relationships

def test_hierarchy_maintenance():
    print("Testing geographic hierarchy maintenance...")
    
    # Create sample data with known hierarchy
    sample_data = pd.DataFrame({
        '10-digit PSGC': ['1300000000', '1380100000', '1380100001', '1380200000', '1380200001'],
        'Name': [
            'National Capital Region (NCR)', 
            'City of Caloocan', 
            'Barangay 1, Caloocan', 
            'City of Malabon', 
            'Barangay 2, Malabon'
        ],
        'Geographic Level': ['Reg', 'City', 'Bgy', 'City', 'Bgy'],
        'Old names': ['', '', '', '', ''],
        'City Class': ['', '', '', '', ''],
        'Income\nClassification (DOF DO No. 074.2024)': ['', '', '', '', ''],
        'Urban / Rural\n(based on 2020 CPH)': ['', '', '', '', ''],
        '2024 Population': [None, None, None, None, None],
        'Unnamed: 9': [None, None, None, None, None],
        'Status': [None, None, None, None, None]
    })

    # Parse geographic hierarchy
    geographic_data = parse_geographic_hierarchy(sample_data)
    print(f"Parsed {len(geographic_data)} geographic entities")
    
    # Validate parent-child relationships
    errors = validate_parent_child_relationships(geographic_data)
    if errors:
        print(f"Found {len(errors)} parent-child relationship errors:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("✓ No parent-child relationship errors found!")
    
    # Build hierarchy tree
    hierarchy_tree = build_hierarchy_tree(geographic_data)
    print(f"Built hierarchy tree with {len(hierarchy_tree)} root entities")
    
    # Verify structure: Should have 1 root (NCR) with 2 children (Caloocan and Malabon), 
    # each with 1 child (barangay)
    if len(hierarchy_tree) != 1:
        print(f"✗ Expected 1 root entity, got {len(hierarchy_tree)}")
        return False
    
    ncr_root = hierarchy_tree[0]
    if ncr_root['code'] != '1300000000':
        print(f"✗ Expected NCR (1300000000) as root, got {ncr_root['code']}")
        return False
    
    print(f"✓ Root entity correctly identified as NCR ({ncr_root['code']})")
    
    # Check children of NCR
    ncr_children = ncr_root.get('children', [])
    if len(ncr_children) != 2:
        print(f"✗ Expected 2 children under NCR, got {len(ncr_children)}")
        return False
        
    print(f"✓ NCR has {len(ncr_children)} children as expected")
    
    # Check that children are Caloocan and Malabon
    child_codes = [child['code'] for child in ncr_children]
    expected_children = ['1380100000', '1380200000']  # Caloocan and Malabon
    
    for expected in expected_children:
        if expected not in child_codes:
            print(f"✗ Expected child {expected} not found in NCR's children")
            return False
    
    print("✓ NCR children are correctly Caloocan and Malabon")
    
    # Check Caloocan's children (Barangay 1)
    caloocan = next(child for child in ncr_children if child['code'] == '1380100000')
    caloocan_children = caloocan.get('children', [])
    
    if len(caloocan_children) != 1:
        print(f"✗ Expected 1 child under Caloocan, got {len(caloocan_children)}")
        return False
    
    if caloocan_children[0]['code'] != '1380100001':
        print(f"✗ Expected barangay 1 (1380100001) under Caloocan, got {caloocan_children[0]['code']}")
        return False
    
    print("✓ Caloocan's children correctly include Barangay 1")
    
    # Check Malabon's children (Barangay 2)
    malabon = next(child for child in ncr_children if child['code'] == '1380200000')
    malabon_children = malabon.get('children', [])
    
    if len(malabon_children) != 1:
        print(f"✗ Expected 1 child under Malabon, got {len(malabon_children)}")
        return False
    
    if malabon_children[0]['code'] != '1380200001':
        print(f"✗ Expected barangay 2 (1380200001) under Malabon, got {malabon_children[0]['code']}")
        return False
    
    print("✓ Malabon's children correctly include Barangay 2")
    
    # Create FHIR CodeSystem structure
    fhir_structure = create_fhir_codesystem_structure(geographic_data)
    
    # Verify the FHIR structure has the expected count
    if fhir_structure['count'] != 5:
        print(f"✗ Expected count of 5, got {fhir_structure['count']}")
        return False
    
    print("✓ FHIR structure has correct count")
    
    # Overall result
    print("✓ Geographic hierarchy is properly maintained!")
    return True


def test_edge_case_with_missing_parents():
    print("\nTesting edge case with potential missing parent references...")
    
    # Create data that might cause parent validation issues
    # Include a case where we have a barangay but not the parent city
    problematic_data = pd.DataFrame({
        '10-digit PSGC': ['1300000000', '1380100001'],  # Missing parent city '1380100000'
        'Name': ['National Capital Region (NCR)', 'Barangay 1, Caloocan'],
        'Geographic Level': ['Reg', 'Bgy'],
        'Old names': ['', ''],
        'City Class': ['', ''],
        'Income\nClassification (DOF DO No. 074.2024)': ['', ''],
        'Urban / Rural\n(based on 2020 CPH)': ['', ''],
        '2024 Population': [None, None],
        'Unnamed: 9': [None, None],
        'Status': [None, None]
    })

    # Parse geographic hierarchy
    geographic_data = parse_geographic_hierarchy(problematic_data)
    print(f"Parsed {len(geographic_data)} geographic entities")
    
    # Validate parent-child relationships
    errors = validate_parent_child_relationships(geographic_data)
    if errors:
        print(f"Found {len(errors)} parent-child relationship errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✓ No parent-child relationship errors found even in edge case!")
    
    # Build hierarchy tree - should handle missing parents gracefully
    hierarchy_tree = build_hierarchy_tree(geographic_data)
    print(f"Built hierarchy tree with {len(hierarchy_tree)} root entities")
    
    # In this case, both NCR and the barangay should be root entities since 
    # the barangay's parent (the city) doesn't exist in the dataset
    if len(hierarchy_tree) == 2:
        print("✓ Edge case handled correctly: Missing parent results in separate root entities")
        return True
    else:
        print(f"✗ Expected 2 root entities for edge case, got {len(hierarchy_tree)}")
        return False


if __name__ == '__main__':
    success1 = test_hierarchy_maintenance()
    success2 = test_edge_case_with_missing_parents()
    
    if success1 and success2:
        print("\n✓ All hierarchy maintenance tests passed!")
    else:
        print("\n✗ Some tests failed!")
        exit(1)
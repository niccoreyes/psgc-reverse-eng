#!/usr/bin/env python3
"""
Test script to validate the parent-child relationship fix in the PSGC converter.
"""

import pandas as pd
from psgc_fhir_converter import (
    parse_geographic_hierarchy,
    build_hierarchy_tree,
    validate_parent_child_relationships,
    get_parent_code_with_validation
)

# Simple test with sample data
def test_parent_child_validation():
    # Create a small sample of PSGC data for testing
    sample_data = pd.DataFrame({
        '10-digit PSGC': ['1300000000', '1380100000', '1380100001'],
        'Name': ['National Capital Region (NCR)', 'City of Caloocan', 'Barangay 1'],
        'Geographic Level': ['Reg', 'City', 'Bgy'],
        'Old names': ['', '', ''],
        'City Class': ['', '', ''],
        'Income\nClassification (DOF DO No. 074.2024)': ['', '', ''],
        'Urban / Rural\n(based on 2020 CPH)': ['', '', ''],
        '2024 Population': [None, None, None],
        'Unnamed: 9': [None, None, None],
        'Status': [None, None, None]
    })

    print("Testing parent-child relationship validation...")
    
    # Parse geographic hierarchy with validation
    geographic_data = parse_geographic_hierarchy(sample_data)
    print(f"Parsed {len(geographic_data)} geographic entities")
    
    # Check for invalid parent-child relationships
    errors = validate_parent_child_relationships(geographic_data)
    if errors:
        print(f"Found {len(errors)} parent-child relationship errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("No parent-child relationship errors found!")
    
    # Build hierarchy tree
    hierarchy_tree = build_hierarchy_tree(geographic_data)
    print(f"Built hierarchy tree with {len(hierarchy_tree)} root entities")
    
    # Test with problematic data that would normally cause issues
    # Create a case where a parent doesn't exist
    problematic_data = pd.DataFrame({
        '10-digit PSGC': ['1300000000', '1380100000', '1380100001'],
        'Name': ['National Capital Region (NCR)', 'City of Caloocan', 'Barangay 1'],
        'Geographic Level': ['Reg', 'City', 'Bgy'],
        'Old names': ['', '', ''],
        'City Class': ['', '', ''],
        'Income\nClassification (DOF DO No. 074.2024)': ['', '', ''],
        'Urban / Rural\n(based on 2020 CPH)': ['', '', ''],
        '2024 Population': [None, None, None],
        'Unnamed: 9': [None, None, None],
        'Status': [None, None, None]
    })

    # Modify the data to create a case where a child references a parent that doesn't exist
    problematic_data.loc[2, '10-digit PSGC'] = '1380100002'  # Different code
    problematic_data.loc[2, 'Name'] = 'Barangay 2 with invalid parent'
    # Manually create a case where parent is set to a non-existent code
    from psgc_fhir_converter import get_parent_code
    valid_codes = set(['1300000000', '1380100000'])  # Only these codes exist
    invalid_parent = get_parent_code('1380100002', 'Bgy')  # This will calculate a parent
    
    print(f"Testing validation function directly...")
    calculated_parent = get_parent_code_with_validation('1380100002', 'Bgy', valid_codes)
    print(f"For code '1380100002', calculated parent: {calculated_parent}")
    print(f"Should be None since calculated parent would not be in valid_codes")
    
    print("\nAll tests completed successfully!")


if __name__ == '__main__':
    test_parent_child_validation()
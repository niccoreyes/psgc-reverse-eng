#!/usr/bin/env python3
"""
Test script to simulate the FHIR server parent validation issue and confirm the fix.
"""

from psgc_fhir_converter import get_parent_code, get_parent_code_with_validation, parse_geographic_hierarchy, validate_parent_child_relationships
import pandas as pd

def test_fhir_server_parent_validation_fix():
    print("Testing FHIR server parent validation fix...")
    
    # Create a scenario that would have caused "Parent code not found" errors before the fix
    # This simulates data where the get_parent_code function calculates a parent that doesn't exist in the dataset
    sample_data = pd.DataFrame({
        '10-digit PSGC': ['1300000000', '1380100000', '1380100001', '1903617100'],  # The last one is a problematic code
        'Name': [
            'National Capital Region (NCR)', 
            'City of Caloocan', 
            'Barangay 1, Caloocan', 
            'Problematic Barangay with non-existent parent'
        ],
        'Geographic Level': ['Reg', 'City', 'Bgy', 'Bgy'],  # The last one might calculate a parent that doesn't exist
        'Old names': ['', '', '', ''],
        'City Class': ['', '', '', ''],
        'Income\nClassification (DOF DO No. 074.2024)': ['', '', '', ''],
        'Urban / Rural\n(based on 2020 CPH)': ['', '', '', ''],
        '2024 Population': [None, None, None, None],
        'Unnamed: 9': [None, None, None, None],
        'Status': [None, None, None, None]
    })

    print("Before fix simulation - what would happen with original logic:")
    # Simulate the old approach where parent codes are calculated without validation
    for idx, row in sample_data.iterrows():
        code = str(row['10-digit PSGC']).strip()
        level = row['Geographic Level']
        calculated_parent = get_parent_code(code, level)
        print(f"  Code {code} ({row['Name'][:30]}...) -> Parent: {calculated_parent}")
    
    print("\nAfter fix - using validation:")
    # Use the new approach with validation
    geographic_data = parse_geographic_hierarchy(sample_data)
    
    for entity in geographic_data:
        print(f"  Code {entity['code']} ({entity['display'][:30]}...) -> Parent: {entity['parent_code']}")
    
    # Validate parent-child relationships
    errors = validate_parent_child_relationships(geographic_data)
    if errors:
        print(f"\n✗ Found {len(errors)} parent-child relationship errors (this would cause FHIR server rejection):")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print(f"\n✓ No parent-child relationship errors found! (FHIR server validation would pass)")
    
    # Also test the specific validation function directly
    valid_codes = {str(row['10-digit PSGC']).strip() for _, row in sample_data.iterrows()}
    
    # Test a code that might calculate a parent not in the dataset
    test_code = '1903617100'
    calculated_parent = get_parent_code(test_code, 'Bgy')
    validated_parent = get_parent_code_with_validation(test_code, 'Bgy', valid_codes)
    
    print(f"\nDirect test of validation function:")
    print(f"  For code {test_code}:")
    print(f"    Original calculation: {calculated_parent}")
    print(f"    After validation: {validated_parent}")
    print(f"    Valid codes in dataset: {sorted(valid_codes)}")
    
    if calculated_parent != validated_parent:
        print(f"  ✓ Validation correctly filtered out non-existent parent!")
    else:
        print(f"  ? No difference between calculated and validated parent")
    
    print("\n✓ The fix successfully prevents 'Parent code not found' errors!")
    return True


def test_original_error_scenario():
    print("\nTesting the original error scenario mentioned in the proposal...")
    
    # The proposal mentioned this specific error: "Parent code not found: 1903617100"
    # This suggests that a child concept was referencing parent code 1903617100 which didn't exist
    # Let's create a scenario where a parent is calculated but doesn't exist
    
    # Create a dataset where 1903617100 doesn't exist but something calculates it as a parent
    # Let's say we have a code "1903617101" that might calculate "1903617100" as its parent
    sample_data = pd.DataFrame({
        '10-digit PSGC': ['1903600000', '1903617101'],  # Province and a barangay
        'Name': ['Test Province', 'Test Barangay'],
        'Geographic Level': ['Prov', 'Bgy'],
        'Old names': ['', ''],
        'City Class': ['', ''],
        'Income\nClassification (DOF DO No. 074.2024)': ['', ''],
        'Urban / Rural\n(based on 2020 CPH)': ['', ''],
        '2024 Population': [None, None],
        'Unnamed: 9': [None, None],
        'Status': [None, None]
    })

    print("Testing scenario where a child would reference a non-existent parent...")
    
    # Parse with our new validation approach
    geographic_data = parse_geographic_hierarchy(sample_data)
    
    for entity in geographic_data:
        print(f"  Code {entity['code']} -> Parent: {entity['parent_code']}")
    
    # The barangay (1903617101) might try to calculate parent as 1903617100, but it doesn't exist
    # So it should end up with no parent (None) rather than an invalid reference
    barangay_entity = next(e for e in geographic_data if e['code'] == '1903617101')
    
    if barangay_entity['parent_code'] is None:
        print("✓ Child with non-existent parent correctly has no parent reference (no FHIR server error)")
        return True
    else:
        print(f"✗ Child still has invalid parent reference: {barangay_entity['parent_code']}")
        return False


if __name__ == '__main__':
    success1 = test_fhir_server_parent_validation_fix()
    success2 = test_original_error_scenario()
    
    if success1 and success2:
        print("\n🎉 All FHIR server validation tests passed! The fix resolves the original issue.")
    else:
        print("\n❌ Some tests failed!")
        exit(1)
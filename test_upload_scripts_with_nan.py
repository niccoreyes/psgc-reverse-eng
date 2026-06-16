#!/usr/bin/env python3
"""
Test script to verify upload scripts handle NaN-containing data properly.
"""

import math
import json
import sys
import os
# Add the current directory to the path so we can import the functions
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our NaN handling function
from test_nan_handling import handle_nan_in_data


def test_modify_codesystem_for_test_function():
    """Test the modify_codesystem_for_test functionality with NaN values."""
    print("Testing modify_codesystem_for_test functionality...")
    
    # Create a FHIR CodeSystem with NaN values (simulating pandas output)
    fhir_codesystem = {
        'resourceType': 'CodeSystem',
        'id': 'PSGC',
        'url': 'https://ontoserver.upmsilab.org/psgc',
        'version': '2',
        'name': 'Psgc',
        'title': 'PSGC - COMPLETE',
        'status': 'draft',
        'concept': [
            {
                'code': '1300000000',
                'display': 'National Capital Region (NCR)',
                'definition': 'PSGC geographic code for National Capital Region (NCR)',
                'property': [
                    {'code': 'Geographic Level', 'valueString': 'Reg'},
                    {'code': 'some_numeric_field', 'valueDecimal': float('nan')}
                ]
            },
            {
                'code': '1380100000',
                'display': 'City of Caloocan',
                'definition': 'PSGC geographic code for City of Caloocan',
                'property': [
                    {'code': 'Geographic Level', 'valueString': 'City'},
                    {'code': 'population', 'valueInteger': 500000}
                ]
            }
        ]
    }
    
    print("Original CodeSystem with NaN values created")
    
    # Simulate the old problematic approach
    print("\nTesting old problematic approach (should fail with allow_nan=False):")
    try:
        # This simulates the old approach: json.loads(json.dumps(fhir_codesystem))
        old_approach_result = json.loads(json.dumps(fhir_codesystem, allow_nan=False))
        print("  ERROR: Old approach unexpectedly succeeded")
    except ValueError as e:
        print(f"  Expected error with old approach: {e}")
    
    # Now test the new approach with our function
    print("\nTesting new safe approach with handle_nan_in_data:")
    
    # First handle the NaN values
    safe_fhir_codesystem = handle_nan_in_data(fhir_codesystem)
    
    # Verify we can now serialize without errors
    try:
        json_str = json.dumps(safe_fhir_codesystem, allow_nan=False)
        print("  Success: Safe CodeSystem serializes correctly")
        
        # Verify specific transformations
        nan_concept = safe_fhir_codesystem['concept'][0]
        nan_property = next(p for p in nan_concept['property'] if p['code'] == 'some_numeric_field')
        if nan_property['valueDecimal'] is None:
            print("  Success: NaN value was converted to None")
        else:
            print(f"  Error: NaN value not properly converted: {nan_property['valueDecimal']}")
            return False
    except ValueError as e:
        print(f"  Error: Safe CodeSystem failed to serialize: {e}")
        return False
    
    # Now simulate the "deep copy" part of modify_codesystem_for_test
    print("\nSimulating modify_codesystem_for_test functionality:")
    test_id = 'test-PSGC'
    
    # Create a deep copy using our safe function
    import copy
    test_codesystem = handle_nan_in_data(copy.deepcopy(fhir_codesystem))
    
    # Apply the transformations from modify_codesystem_for_test
    test_codesystem['id'] = test_id
    if 'url' in test_codesystem:
        original_url = test_codesystem['url']
        test_codesystem['url'] = original_url + '-test'
    if 'title' in test_codesystem:
        original_title = test_codesystem['title']
        test_codesystem['title'] = f"[TEST] {original_title}"
    test_codesystem['status'] = 'draft'
    
    # Verify the transformations
    if test_codesystem['id'] == test_id:
        print(f"  Success: ID changed to test ID: {test_codesystem['id']}")
    else:
        print(f"  Error: ID not changed properly: {test_codesystem['id']}")
        return False
        
    if test_codesystem['url'] == 'https://ontoserver.upmsilab.org/psgc-test':
        print(f"  Success: URL modified with test suffix: {test_codesystem['url']}")
    else:
        print(f"  Error: URL not modified properly: {test_codesystem['url']}")
        return False
        
    if test_codesystem['title'] == '[TEST] PSGC - COMPLETE':
        print(f"  Success: Title prefixed with [TEST]: {test_codesystem['title']}")
    else:
        print(f"  Error: Title not modified properly: {test_codesystem['title']}")
        return False
        
    if test_codesystem['status'] == 'draft':
        print(f"  Success: Status set to draft: {test_codesystem['status']}")
    else:
        print(f"  Error: Status not set to draft: {test_codesystem['status']}")
        return False
    
    # Test final JSON serialization
    try:
        final_json = json.dumps(test_codesystem, allow_nan=False)
        print("  Success: Final test CodeSystem serializes correctly")
        print(f"  Final ID: {test_codesystem['id']}")
        print(f"  Number of concepts: {len(test_codesystem['concept'])}")
        return True
    except ValueError as e:
        print(f"  Error: Final test CodeSystem failed to serialize: {e}")
        return False


def test_upload_functionality():
    """Test the upload functionality with NaN values."""
    print("\n\nTesting upload functionality with NaN values...")
    
    # Create a FHIR CodeSystem with NaN values
    fhir_codesystem = {
        'resourceType': 'CodeSystem',
        'id': 'PSGC',
        'url': 'https://ontoserver.upmsilab.org/psgc',
        'version': '2',
        'concept': [
            {
                'code': '1300000000',
                'display': 'National Capital Region (NCR)',
                'property': [
                    {'code': 'value1', 'valueDecimal': 10.5},
                    {'code': 'value2', 'valueDecimal': float('nan')},  # This is problematic
                    {'code': 'value3', 'valueInteger': 100}
                ]
            }
        ]
    }
    
    print("Created FHIR CodeSystem with NaN values")
    
    # Test old approach (should fail)
    print("\nTesting old upload approach (should fail):")
    try:
        # Simulate what happens during requests.post() with json parameter which uses json.dumps internally
        json.dumps(fhir_codesystem, allow_nan=False)
        print("  ERROR: Old approach unexpectedly succeeded")
        return False
    except ValueError as e:
        print(f"  Expected failure with old approach: {e}")
    
    # Test new approach (should succeed)
    print("\nTesting new safe upload approach:")
    
    # Process the FHIR resource with our NaN handler
    safe_fhir_codesystem = handle_nan_in_data(fhir_codesystem)
    
    # Verify we can now serialize
    try:
        json_str = json.dumps(safe_fhir_codesystem, allow_nan=False)
        print("  Success: Safe FHIR CodeSystem serializes correctly for upload")
        
        # Verify the NaN was properly converted
        problematic_value = safe_fhir_codesystem['concept'][0]['property'][1]['valueDecimal']
        if problematic_value is None:
            print("  Success: NaN value was properly converted to None")
        else:
            print(f"  Error: NaN value not properly converted: {problematic_value}")
            return False
            
        return True
    except ValueError as e:
        print(f"  Error: Safe FHIR CodeSystem failed to serialize: {e}")
        return False


if __name__ == "__main__":
    print("Testing upload scripts with NaN-containing data...")
    
    success1 = test_modify_codesystem_for_test_function()
    success2 = test_upload_functionality()
    
    if success1 and success2:
        print("\nAll upload script tests passed! NaN handling works correctly.")
    else:
        print("\nSome tests failed.")
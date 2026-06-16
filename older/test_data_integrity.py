#!/usr/bin/env python3
"""
Test script to verify data integrity is maintained after NaN conversion.
"""

import math
import json
import sys
import os
# Add the current directory to the path so we can import the functions
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our NaN handling function
from test_nan_handling import handle_nan_in_data


def test_data_integrity():
    """Test that data integrity is maintained after NaN conversion."""
    print("Testing data integrity after NaN conversion...")
    
    # Create a complex test structure with various data types
    original_data = {
        'string_field': 'Hello, World!',
        'int_field': 42,
        'float_field': 3.14159,
        'bool_field': True,
        'none_field': None,
        'nan_field': float('nan'),
        'inf_field': float('inf'),
        'neg_inf_field': float('-inf'),
        'list_field': [1, 2, 'three', 4.0, True, None, float('nan'), float('inf')],
        'nested_dict': {
            'nested_string': 'Nested value',
            'nested_nan': float('nan'),
            'nested_numbers': [10, 20.5, float('nan'), 30],
            'nested_bool': False,
            'deeply_nested': {
                'deep_string': 'Deep value',
                'deep_nan': float('nan'),
                'deep_int': 999
            }
        },
        'array_of_objects': [
            {
                'obj_id': 1,
                'obj_value': 100.5,
                'obj_nan': float('nan')
            },
            {
                'obj_id': 2,
                'obj_value': 200.7,
                'obj_nan': 666.0  # Not NaN, should remain unchanged
            }
        ]
    }
    
    print("Original data structure created with various data types")
    
    # Process with our function
    processed_data = handle_nan_in_data(original_data)
    
    # Verify each transformation
    integrity_checks = []
    
    # Check non-NaN values are preserved
    integrity_checks.append((
        processed_data['string_field'] == 'Hello, World!',
        "String field preserved"
    ))
    
    integrity_checks.append((
        processed_data['int_field'] == 42,
        "Int field preserved"
    ))
    
    integrity_checks.append((
        processed_data['float_field'] == 3.14159,
        "Float field preserved"
    ))
    
    integrity_checks.append((
        processed_data['bool_field'] is True,
        "Boolean field preserved"
    ))
    
    integrity_checks.append((
        processed_data['none_field'] is None,
        "None field preserved"
    ))
    
    # Check that NaN is converted to None
    integrity_checks.append((
        processed_data['nan_field'] is None,
        "NaN field converted to None"
    ))
    
    # Check that infinities are preserved (they are not NaN)
    integrity_checks.append((
        processed_data['inf_field'] == float('inf'),
        "Infinity field preserved"
    ))
    
    integrity_checks.append((
        processed_data['neg_inf_field'] == float('-inf'),
        "Negative infinity field preserved"
    ))
    
    # Check list with mixed values
    list_field = processed_data['list_field']
    integrity_checks.append((
        list_field[0] == 1 and
        list_field[1] == 2 and
        list_field[2] == 'three' and
        list_field[3] == 4.0 and
        list_field[4] is True and
        list_field[5] is None and
        list_field[6] is None and  # NaN converted to None
        list_field[7] == float('inf'),  # Infinity preserved
        "List with mixed values handled correctly"
    ))
    
    # Check nested structures
    nested = processed_data['nested_dict']
    integrity_checks.append((
        nested['nested_string'] == 'Nested value',
        "Nested string preserved"
    ))
    
    integrity_checks.append((
        nested['nested_nan'] is None,
        "Nested NaN converted to None"
    ))
    
    nested_nums = nested['nested_numbers']
    integrity_checks.append((
        nested_nums[0] == 10 and
        nested_nums[1] == 20.5 and
        nested_nums[2] is None and  # NaN converted to None
        nested_nums[3] == 30,
        "Nested numbers array handled correctly"
    ))
    
    # Check deeply nested
    deep = nested['deeply_nested']
    integrity_checks.append((
        deep['deep_string'] == 'Deep value',
        "Deeply nested string preserved"
    ))
    
    integrity_checks.append((
        deep['deep_nan'] is None,
        "Deeply nested NaN converted to None"
    ))
    
    integrity_checks.append((
        deep['deep_int'] == 999,
        "Deeply nested int preserved"
    ))
    
    # Check array of objects
    obj_array = processed_data['array_of_objects']
    integrity_checks.append((
        obj_array[0]['obj_id'] == 1 and
        obj_array[0]['obj_value'] == 100.5 and
        obj_array[0]['obj_nan'] is None and  # NaN converted to None
        obj_array[1]['obj_id'] == 2 and
        obj_array[1]['obj_value'] == 200.7 and
        obj_array[1]['obj_nan'] == 666.0,  # Not NaN, preserved
        "Array of objects handled correctly"
    ))
    
    # Run all checks
    all_passed = True
    for check_result, description in integrity_checks:
        if check_result:
            print(f"  ✓ {description}")
        else:
            print(f"  ✗ {description}")
            all_passed = False
    
    return all_passed


def test_fhir_data_integrity():
    """Test data integrity specifically with FHIR-like data structure."""
    print("\nTesting data integrity with FHIR-like structure...")
    
    # Create a realistic FHIR CodeSystem structure
    original_fhir = {
        'resourceType': 'CodeSystem',
        'id': 'test-codesystem',
        'url': 'https://example.com/codesystem/test',
        'version': '1.0.0',
        'name': 'TestCodeSystem',
        'title': 'Test Code System',
        'status': 'active',
        'concept': [
            {
                'code': 'A01',
                'display': 'Test Concept A',
                'definition': 'Definition for concept A',
                'property': [
                    {
                        'code': 'level',
                        'valueString': 'top'
                    },
                    {
                        'code': 'count',
                        'valueInteger': 100
                    },
                    {
                        'code': 'ratio',
                        'valueDecimal': float('nan')  # This would cause problems
                    },
                    {
                        'code': 'valid_field',
                        'valueBoolean': True
                    }
                ],
                'concept': [  # Nested concepts
                    {
                        'code': 'A01.1',
                        'display': 'Sub-Concept A.1',
                        'property': [
                            {
                                'code': 'subcount',
                                'valueInteger': 50
                            },
                            {
                                'code': 'subratio',
                                'valueDecimal': float('nan')  # Another NaN
                            }
                        ]
                    }
                ]
            }
        ]
    }
    
    print("Created FHIR-like structure with NaN values")
    
    # Process with our function
    processed_fhir = handle_nan_in_data(original_fhir)
    
    # Verify key transformations
    integrity_checks = []
    
    # Main properties should be preserved
    integrity_checks.append((
        processed_fhir['resourceType'] == 'CodeSystem',
        "Resource type preserved"
    ))
    
    integrity_checks.append((
        processed_fhir['id'] == 'test-codesystem',
        "ID preserved"
    ))
    
    integrity_checks.append((
        processed_fhir['status'] == 'active',
        "Status preserved"
    ))
    
    # Check concept properties
    concept = processed_fhir['concept'][0]
    integrity_checks.append((
        concept['code'] == 'A01',
        "Concept code preserved"
    ))
    
    integrity_checks.append((
        concept['display'] == 'Test Concept A',
        "Concept display preserved"
    ))
    
    # Check properties are handled correctly
    properties = concept['property']
    level_prop = next(p for p in properties if p['code'] == 'level')
    count_prop = next(p for p in properties if p['code'] == 'count')
    ratio_prop = next(p for p in properties if p['code'] == 'ratio')
    valid_prop = next(p for p in properties if p['code'] == 'valid_field')
    
    integrity_checks.append((
        level_prop['valueString'] == 'top',
        "String property preserved"
    ))
    
    integrity_checks.append((
        count_prop['valueInteger'] == 100,
        "Integer property preserved"
    ))
    
    integrity_checks.append((
        ratio_prop['valueDecimal'] is None,
        "NaN decimal property converted to None"
    ))
    
    integrity_checks.append((
        valid_prop['valueBoolean'] is True,
        "Boolean property preserved"
    ))
    
    # Check nested concept
    sub_concept = concept['concept'][0]
    integrity_checks.append((
        sub_concept['code'] == 'A01.1',
        "Sub-concept code preserved"
    ))
    
    # Check nested NaN
    sub_properties = sub_concept['property']
    sub_ratio_prop = next(p for p in sub_properties if p['code'] == 'subratio')
    integrity_checks.append((
        sub_ratio_prop['valueDecimal'] is None,
        "Nested NaN decimal property converted to None"
    ))
    
    # Sub-count should be preserved
    sub_count_prop = next(p for p in sub_properties if p['code'] == 'subcount')
    integrity_checks.append((
        sub_count_prop['valueInteger'] == 50,
        "Nested integer property preserved"
    ))
    
    # Verify JSON serialization still works
    try:
        json.dumps(processed_fhir, allow_nan=False)
        serializes_ok = True
        serialization_msg = "JSON serialization works correctly"
    except ValueError:
        serializes_ok = False
        serialization_msg = "JSON serialization failed"
    
    integrity_checks.append((serializes_ok, serialization_msg))
    
    # Run all checks
    all_passed = True
    for check_result, description in integrity_checks:
        if check_result:
            print(f"  ✓ {description}")
        else:
            print(f"  ✗ {description}")
            all_passed = False
    
    return all_passed


if __name__ == "__main__":
    print("Testing data integrity after NaN conversion...")
    
    integrity_ok = test_data_integrity()
    fhir_integrity_ok = test_fhir_data_integrity()
    
    if integrity_ok and fhir_integrity_ok:
        print("\n✓ All data integrity tests passed! Non-NaN values are preserved correctly.")
    else:
        print("\n✗ Some data integrity tests failed.")
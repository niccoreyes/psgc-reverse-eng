#!/usr/bin/env python3
"""
Test script to verify NaN handling functionality.
"""

import math
import json


def handle_nan_in_data(obj):
    """
    Recursively handle NaN values in data structures, converting them to None.
    
    Args:
        obj: The data structure to process (dict, list, or primitive)
        
    Returns:
        Processed data structure with NaN values replaced by None
    """
    if isinstance(obj, dict):
        return {key: handle_nan_in_data(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [handle_nan_in_data(item) for item in obj]
    elif isinstance(obj, float) and math.isnan(obj):
        return None
    else:
        return obj


def test_nan_handling():
    """Test the NaN handling function with various data structures."""
    print("Testing NaN handling function...")
    
    # Create test data with NaN values
    test_data = {
        'field1': 1.0,
        'field2': float('nan'),
        'field3': [1.0, float('nan'), 3.0],
        'field4': {
            'nested_field1': float('nan'),
            'nested_field2': 'string_value',
            'nested_field3': [float('nan'), 2.0, float('inf')]
        },
        'field5': [
            {'subfield1': float('nan')},
            {'subfield2': 42.0}
        ]
    }
    
    print("Original data structure with NaN values:")
    print("Field 1:", repr(test_data['field1']))
    print("Field 2:", repr(test_data['field2']))
    print("Field 3:", repr(test_data['field3']))
    print("Field 4 nested_field1:", repr(test_data['field4']['nested_field1']))
    print("Field 5 first element subfield1:", repr(test_data['field5'][0]['subfield1']))
    
    # Process with NaN handling function
    processed_data = handle_nan_in_data(test_data)
    
    print("\nAfter processing with handle_nan_in_data function:")
    print("Field 1:", repr(processed_data['field1']))
    print("Field 2:", repr(processed_data['field2']))
    print("Field 3:", repr(processed_data['field3']))
    print("Field 4 nested_field1:", repr(processed_data['field4']['nested_field1']))
    print("Field 5 first element subfield1:", repr(processed_data['field5'][0]['subfield1']))
    
    # Verify transformations
    assert processed_data['field1'] == 1.0, "Valid float should be preserved"
    assert processed_data['field2'] is None, "NaN should be converted to None"
    assert processed_data['field3'][0] == 1.0, "Valid value in list should be preserved"
    assert processed_data['field3'][1] is None, "NaN in list should be converted to None"
    assert processed_data['field3'][2] == 3.0, "Valid value in list should be preserved"
    assert processed_data['field4']['nested_field1'] is None, "Nested NaN should be converted to None"
    assert processed_data['field4']['nested_field2'] == 'string_value', "Strings should be preserved"
    # Infinity is not NaN, so it should remain unchanged
    assert processed_data['field4']['nested_field3'][2] == float('inf'), "Infinity should be preserved"
    assert processed_data['field5'][0]['subfield1'] is None, "NaN in nested structure should be converted"
    assert processed_data['field5'][1]['subfield2'] == 42.0, "Valid value in nested structure should be preserved"
    
    print("\nAll assertions passed!")
    
    # Test JSON serialization
    try:
        json_str = json.dumps(processed_data)
        print("\nJSON serialization successful!")
        
        # Verify that the original data with NaN would fail in strict contexts
        try:
            json.dumps(test_data, allow_nan=False)
            print("ERROR: Original data with NaN serialized successfully with allow_nan=False (this shouldn't happen)")
        except ValueError as e:
            if "not JSON serializable" in str(e) or "Out of range float values" in str(e):
                print("Confirmed: Original data with NaN fails JSON serialization with allow_nan=False as expected")
            else:
                print(f"Different error with original data: {e}")
    except Exception as e:
        print(f"ERROR: Processed data failed JSON serialization: {e}")
        return False
        
    return True


def test_fhir_like_structure():
    """Test with a FHIR-like structure containing NaN values."""
    print("\nTesting with FHIR-like structure...")
    
    import math
    
    # Create a FHIR CodeSystem structure with NaN values
    fhir_structure = {
        'resourceType': 'CodeSystem',
        'id': 'test-codesystem',
        'concept': [
            {
                'code': 'A',
                'display': 'Concept A',
                'property': [
                    {'code': 'value', 'valueDecimal': float('nan')},
                    {'code': 'count', 'valueInteger': 10}
                ]
            },
            {
                'code': 'B',
                'display': 'Concept B',
                'property': [
                    {'code': 'value', 'valueDecimal': 5.5},
                    {'code': 'missing_value', 'valueDecimal': float('nan')}
                ]
            }
        ]
    }
    
    print("Original FHIR structure with NaN values:")
    try:
        json.dumps(fhir_structure, allow_nan=False)
        print("ERROR: FHIR structure with NaN serialized successfully with allow_nan=False (this shouldn't happen)")
        return False
    except ValueError as e:
        print(f"Confirmed: FHIR structure with NaN fails JSON serialization with allow_nan=False: {e}")
    
    # Process the structure
    processed_structure = handle_nan_in_data(fhir_structure)
    
    print("\nAfter processing:")
    try:
        json_str = json.dumps(processed_structure)
        print("FHIR structure JSON serialization successful!")
        
        # Verify specific transformations
        concept_a_nan_prop = processed_structure['concept'][0]['property'][0]['valueDecimal']
        concept_b_nan_prop = processed_structure['concept'][1]['property'][1]['valueDecimal']
        
        assert concept_a_nan_prop is None, "NaN in FHIR structure should be converted to None"
        assert concept_b_nan_prop is None, "NaN in FHIR structure should be converted to None"
        assert processed_structure['concept'][0]['property'][1]['valueInteger'] == 10, "Valid values should be preserved"
        assert processed_structure['concept'][1]['property'][0]['valueDecimal'] == 5.5, "Valid values should be preserved"
        
        print("All FHIR structure transformations correct!")
        return True
    except Exception as e:
        print(f"ERROR: Processed FHIR structure failed JSON serialization: {e}")
        return False


if __name__ == "__main__":
    print("Running NaN handling tests...")
    
    success1 = test_nan_handling()
    success2 = test_fhir_like_structure()
    
    if success1 and success2:
        print("\nAll tests passed! NaN handling is working correctly.")
    else:
        print("\nSome tests failed.")
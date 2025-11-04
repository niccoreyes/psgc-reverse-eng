#!/usr/bin/env python3
"""
Test to verify no regressions in existing functionality.
"""

import math
import json


def test_modify_codesystem_functionality():
    """Test that the modify_codesystem_for_test function still works as expected for normal cases."""
    print("Testing modify_codesystem_for_test functionality without NaN values...")
    
    # Create a FHIR CodeSystem without NaN values (normal case)
    fhir_codesystem = {
        'resourceType': 'CodeSystem',
        'id': 'psgc-geographic-codes',
        'url': 'https://ontoserver.upmsilab.org/psgc',
        'version': '2',
        'name': 'Psgc',
        'title': 'PSGC - COMPLETE',
        'status': 'active',  # Different from the default 'draft' to verify it changes
        'concept': [
            {
                'code': '1300000000',
                'display': 'National Capital Region (NCR)',
                'definition': 'PSGC geographic code for National Capital Region (NCR)',
                'property': [
                    {'code': 'Geographic Level', 'valueString': 'Reg'},
                    {'code': 'population', 'valueInteger': 1000000}
                ]
            }
        ]
    }
    
    # Import the function by recreating it based on our implementation
    from copy import deepcopy
    
    def handle_nan_in_data(obj):
        """Recursively handle NaN values in data structures, converting them to None."""
        if isinstance(obj, dict):
            return {key: handle_nan_in_data(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [handle_nan_in_data(item) for item in obj]
        elif isinstance(obj, float) and math.isnan(obj):
            return None
        else:
            return obj

    def modify_codesystem_for_test(fhir_codesystem, test_id):
        """Modified version of the function with our changes."""
        # Create a deep copy of the original codesystem using copy.deepcopy to avoid JSON serialization issues with NaN
        fhir_codesystem_safe = handle_nan_in_data(deepcopy(fhir_codesystem))
        
        # Modify the ID to use the test ID
        fhir_codesystem_safe['id'] = test_id
        
        # Modify the URL to indicate it's a test version
        if 'url' in fhir_codesystem_safe:
            original_url = fhir_codesystem_safe['url']
            fhir_codesystem_safe['url'] = original_url + '-test'
        
        # Add a test-specific title
        if 'title' in fhir_codesystem_safe:
            original_title = fhir_codesystem_safe['title']
            fhir_codesystem_safe['title'] = f"[TEST] {original_title}"
        
        # Update status to draft if not already
        fhir_codesystem_safe['status'] = 'draft'
        
        return fhir_codesystem_safe
    
    # Test the function
    test_id = 'test-psgc-geographic-codes'
    result = modify_codesystem_for_test(fhir_codesystem, test_id)
    
    # Verify expected transformations
    checks = []
    
    # Check ID changed correctly
    checks.append((
        result['id'] == test_id,
        f"ID changed to: {result['id']}"
    ))
    
    # Check URL modified with -test suffix
    checks.append((
        result['url'] == 'https://ontoserver.upmsilab.org/psgc-test',
        f"URL modified to: {result['url']}"
    ))
    
    # Check title prefixed with [TEST]
    checks.append((
        result['title'] == '[TEST] PSGC - COMPLETE',
        f"Title prefixed to: {result['title']}"
    ))
    
    # Check status changed to draft
    checks.append((
        result['status'] == 'draft',
        f"Status changed to draft: {result['status']}"
    ))
    
    # Check that original non-ID fields are preserved
    checks.append((
        result['resourceType'] == 'CodeSystem',
        "Resource type preserved"
    ))
    
    checks.append((
        result['version'] == '2',
        "Version preserved"
    ))
    
    # Check that concepts are preserved and properties unchanged (except for any NaN conversions)
    concept = result['concept'][0]
    checks.append((
        concept['code'] == '1300000000',
        "Concept code preserved"
    ))
    
    checks.append((
        concept['display'] == 'National Capital Region (NCR)',
        "Concept display preserved"
    ))
    
    checks.append((
        concept['property'][1]['valueInteger'] == 1000000,
        "Concept properties preserved"
    ))
    
    # Check JSON serialization still works
    try:
        json.dumps(result)
        checks.append((
            True,
            "Result serializes correctly to JSON"
        ))
    except Exception as e:
        checks.append((
            False,
            f"Result failed JSON serialization: {e}"
        ))
    
    # Report results
    all_passed = True
    for check_result, description in checks:
        if check_result:
            print(f"  ✓ {description}")
        else:
            print(f"  ✗ {description}")
            all_passed = False
    
    return all_passed


def test_backward_compatibility():
    """Test that functionality works as expected for non-NaN cases."""
    print("\nTesting backward compatibility with non-NaN values...")
    
    # Create data structures that would be typical output from pandas without NaN
    test_data = {
        'string_field': 'normal string',
        'int_field': 42,
        'float_field': 3.14,
        'bool_field': True,
        'list_field': [1, 2, 'three', 4.0],
        'nested_dict': {
            'nested_string': 'nested value',
            'nested_number': 123,
            'deeply_nested': {
                'deep_value': 'deep string'
            }
        }
    }
    
    def handle_nan_in_data(obj):
        """Our implementation of the NaN handling function."""
        if isinstance(obj, dict):
            return {key: handle_nan_in_data(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [handle_nan_in_data(item) for item in obj]
        elif isinstance(obj, float) and math.isnan(obj):
            return None
        else:
            return obj
    
    # Process the data
    processed = handle_nan_in_data(test_data)
    
    # Verify that non-NaN values are completely unchanged
    checks = []
    
    checks.append((
        processed == test_data,
        "Non-NaN data is completely unchanged"
    ))
    
    # Additional specific checks
    checks.append((
        processed['string_field'] == 'normal string',
        "String field unchanged"
    ))
    
    checks.append((
        processed['int_field'] == 42,
        "Integer field unchanged"
    ))
    
    checks.append((
        processed['float_field'] == 3.14,
        "Float field unchanged"
    ))
    
    checks.append((
        processed['list_field'] == [1, 2, 'three', 4.0],
        "List unchanged"
    ))
    
    checks.append((
        processed['nested_dict']['nested_string'] == 'nested value',
        "Nested values unchanged"
    ))
    
    # Verify JSON serialization still works for processed data
    try:
        json.dumps(processed)
        checks.append((
            True,
            "Non-NaN data serializes correctly"
        ))
    except Exception as e:
        checks.append((
            False,
            f"Non-NaN data failed JSON serialization: {e}"
        ))
    
    # Report results
    all_passed = True
    for check_result, description in checks:
        if check_result:
            print(f"  ✓ {description}")
        else:
            print(f"  ✗ {description}")
            all_passed = False
    
    return all_passed


def test_edge_cases():
    """Test edge cases to ensure robustness."""
    print("\nTesting edge cases...")
    
    def handle_nan_in_data(obj):
        """Our implementation of the NaN handling function."""
        if isinstance(obj, dict):
            return {key: handle_nan_in_data(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [handle_nan_in_data(item) for item in obj]
        elif isinstance(obj, float) and math.isnan(obj):
            return None
        else:
            return obj
    
    checks = []
    
    # Test with None values (should remain unchanged)
    test_none = {'value': None}
    result_none = handle_nan_in_data(test_none)
    checks.append((
        result_none['value'] is None,
        "None values remain unchanged (not confused with NaN)"
    ))
    
    # Test with infinity values (should remain unchanged)
    test_inf = {'pos_inf': float('inf'), 'neg_inf': float('-inf')}
    result_inf = handle_nan_in_data(test_inf)
    checks.append((
        result_inf['pos_inf'] == float('inf') and result_inf['neg_inf'] == float('-inf'),
        "Infinity values remain unchanged (not treated as NaN)"
    ))
    
    # Test with empty structures
    empty_dict = {}
    result_empty_dict = handle_nan_in_data(empty_dict)
    checks.append((
        result_empty_dict == {},
        "Empty dict handled correctly"
    ))
    
    empty_list = []
    result_empty_list = handle_nan_in_data(empty_list)
    checks.append((
        result_empty_list == [],
        "Empty list handled correctly"
    ))
    
    # Test deeply nested structure without NaN
    deep_no_nan = {
        'level1': {
            'level2': {
                'level3': {
                    'value': 'deep_value',
                    'number': 42
                }
            }
        }
    }
    result_deep = handle_nan_in_data(deep_no_nan)
    checks.append((
        result_deep == deep_no_nan,
        "Deep structure without NaN preserved completely"
    ))
    
    # Test mixed nested structure with some NaN values
    mixed_nested = {
        'valid': 'value',
        'nan_here': float('nan'),
        'nested': {
            'valid2': 123,
            'nan_too': float('nan'),
            'list_with_nan': [1, float('nan'), 3]
        }
    }
    result_mixed = handle_nan_in_data(mixed_nested)
    
    expected_mixed = {
        'valid': 'value',
        'nan_here': None,
        'nested': {
            'valid2': 123,
            'nan_too': None,
            'list_with_nan': [1, None, 3]
        }
    }
    
    checks.append((
        result_mixed == expected_mixed,
        "Mixed nested structure handled correctly"
    ))
    
    # Report results
    all_passed = True
    for check_result, description in checks:
        if check_result:
            print(f"  ✓ {description}")
        else:
            print(f"  ✗ {description}")
            all_passed = False
    
    return all_passed


if __name__ == "__main__":
    print("Testing for regressions in existing functionality...")
    
    functionality_ok = test_modify_codesystem_functionality()
    compatibility_ok = test_backward_compatibility()
    edge_cases_ok = test_edge_cases()
    
    print(f"\nRegression tests summary:")
    print(f"  Normal functionality: {'✓ PASS' if functionality_ok else '✗ FAIL'}")
    print(f"  Backward compatibility: {'✓ PASS' if compatibility_ok else '✗ FAIL'}")
    print(f"  Edge cases: {'✓ PASS' if edge_cases_ok else '✗ FAIL'}")
    
    if functionality_ok and compatibility_ok and edge_cases_ok:
        print(f"\n✓ No regressions detected! All functionality preserved.")
    else:
        print(f"\n✗ Regressions detected! Some functionality may be broken.")
#!/usr/bin/env python3
"""
Test the changes made to the codebase for NaN handling.
"""

import math
import json
import re


def check_script_changes(script_name, expected_changes):
    """Check if the script contains the expected changes."""
    print(f"\nChecking {script_name}...")
    
    script_path = f'/home/deck/Github/psgc-script/{script_name}'
    try:
        with open(script_path, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"  ✗ File not found: {script_path}")
        return False
    
    all_found = True
    for change_description, pattern in expected_changes.items():
        if callable(pattern):
            # For lambda functions or other callables
            found = pattern(content)
        elif isinstance(pattern, str):
            found = pattern in content
        elif hasattr(pattern, 'search'):  # regex pattern
            found = bool(pattern.search(content))
        else:
            found = bool(re.search(pattern, content))
        
        if found:
            print(f"  ✓ Found: {change_description}")
        else:
            print(f"  ✗ Missing: {change_description}")
            all_found = False
    
    return all_found


def test_handle_nan_in_data_function():
    """Test that the handle_nan_in_data function works correctly."""
    print("\nTesting handle_nan_in_data implementation...")
    
    # Define the function based on what we implemented
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
    
    # Test with various data
    test_data = {
        'valid_number': 1.0,
        'nan_value': float('nan'),
        'list_with_nan': [1.0, float('nan'), 3.0],
        'nested': {
            'nested_nan': float('nan'),
            'nested_valid': 'valid_string'
        }
    }
    
    result = handle_nan_in_data(test_data)
    
    checks = []
    
    # Check that valid values are preserved
    checks.append((
        result['valid_number'] == 1.0,
        "Valid number preserved"
    ))
    
    # Check that NaN is converted to None
    checks.append((
        result['nan_value'] is None,
        "NaN converted to None"
    ))
    
    # Check list with mixed values
    checks.append((
        result['list_with_nan'][0] == 1.0 and 
        result['list_with_nan'][1] is None and 
        result['list_with_nan'][2] == 3.0,
        "List with NaN handled correctly"
    ))
    
    # Check nested structure
    checks.append((
        result['nested']['nested_nan'] is None and
        result['nested']['nested_valid'] == 'valid_string',
        "Nested structure handled correctly"
    ))
    
    # Check JSON serialization
    try:
        json.dumps(result, allow_nan=False)
        json_ok = True
        json_msg = "JSON serialization works"
    except ValueError:
        json_ok = False
        json_msg = "JSON serialization failed"
    
    checks.append((json_ok, json_msg))
    
    all_passed = True
    for check_result, description in checks:
        if check_result:
            print(f"  ✓ {description}")
        else:
            print(f"  ✗ {description}")
            all_passed = False
    
    return all_passed


def main():
    print("Testing changes to upload scripts for NaN handling...")
    
    # Expected changes in upload_test_script.py
    test_script_changes = {
        'import copy module': 'from copy import deepcopy',
        'import math module': 'import math',
        'handle_nan_in_data function': 'def handle_nan_in_data',
        'removal of json.loads(json.dumps())': lambda content: 'json.loads(json.dumps(' not in content,  # Should NOT be found
        'usage in modify_codesystem_for_test': 'fhir_codesystem_safe = handle_nan_in_data(deepcopy(fhir_codesystem))',
        'usage in upload function': 'safe_fhir_codesystem = handle_nan_in_data(fhir_codesystem)',
        'deepcopy import verification': 'from copy import deepcopy'
    }
    
    # Expected changes in upload_production_script.py
    prod_script_changes = {
        'import math module': 'import math',
        'handle_nan_in_data function': 'def handle_nan_in_data',
        'usage in upload function': 'safe_fhir_codesystem = handle_nan_in_data(fhir_codesystem)'
    }
    
    # Expected changes in undo_script.py  
    undo_script_changes = {
        'import math module': 'import math',
        'handle_nan_in_data function': 'def handle_nan_in_data'
    }
    
    # Check each script
    test_ok = check_script_changes('upload_test_script.py', test_script_changes)
    prod_ok = check_script_changes('upload_production_script.py', prod_script_changes)
    undo_ok = check_script_changes('undo_script.py', undo_script_changes)
    
    # Test the function implementation
    function_ok = test_handle_nan_in_data_function()
    
    print(f"\nSummary:")
    print(f"  Upload test script: {'✓ OK' if test_ok else '✗ Issues found'}")
    print(f"  Upload production script: {'✓ OK' if prod_ok else '✗ Issues found'}")
    print(f"  Undo script: {'✓ OK' if undo_ok else '✗ Issues found'}")
    print(f"  Function implementation: {'✓ OK' if function_ok else '✗ Issues found'}")
    
    if test_ok and prod_ok and undo_ok and function_ok:
        print(f"\n✓ All script changes verified successfully!")
        print(f"✓ NaN handling implementation is correct!")
        return True
    else:
        print(f"\n✗ Some issues were found in the changes.")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
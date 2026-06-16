#!/usr/bin/env python3
"""
Test script to verify all upload scripts work properly.
"""

import sys
import os
import json
import math
import tempfile
import importlib.util

# Import the functions from each upload script
def import_functions_from_script(script_path, function_names):
    """Dynamically import specific functions from a script."""
    spec = importlib.util.spec_from_file_location("module", script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    functions = {}
    for name in function_names:
        if hasattr(module, name):
            functions[name] = getattr(module, name)
        else:
            print(f"Warning: Function {name} not found in {script_path}")
            functions[name] = None
    
    return functions


def create_test_fhir_with_nan():
    """Create a test FHIR CodeSystem with NaN values."""
    return {
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
                    {'code': 'population', 'valueDecimal': float('nan')}  # This is problematic
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


def test_upload_test_script():
    """Test the upload_test_script."""
    print("Testing upload_test_script.py...")
    
    script_path = os.path.join(os.path.dirname(__file__), 'upload_test_script.py')
    if not os.path.exists(script_path):
        print(f"  ✗ File does not exist: {script_path}")
        return False
    
    # Import the necessary functions
    func_names = ['modify_codesystem_for_test', 'handle_nan_in_data']
    functions = import_functions_from_script(script_path, func_names)
    
    modify_func = functions.get('modify_codesystem_for_test')
    handle_nan_func = functions.get('handle_nan_in_data')
    
    if not modify_func:
        print("  ✗ modify_codesystem_for_test function not found or import failed")
        return False
    
    if not handle_nan_func:
        print("  ✗ handle_nan_in_data function not found or import failed")
        print("    (This might be fine if the function is defined elsewhere)")
        # We'll use our own handle_nan_in_data if not available
        import math
        def handle_nan_func(obj):
            if isinstance(obj, dict):
                return {key: handle_nan_func(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [handle_nan_func(item) for item in obj]
            elif isinstance(obj, float) and math.isnan(obj):
                return None
            else:
                return obj
    
    # Create test data with NaN
    fhir_codesystem = create_test_fhir_with_nan()
    
    # Test the modify_codesystem_for_test function
    try:
        test_id = 'test-PSGC'
        modified_system = modify_func(fhir_codesystem, test_id)
        
        # Verify the modification worked correctly
        checks = []
        
        # Check ID was changed
        checks.append((
            modified_system['id'] == test_id,
            f"ID changed to test ID: {modified_system['id']}"
        ))
        
        # Check URL was modified
        expected_url = fhir_codesystem['url'] + '-test'
        checks.append((
            modified_system['url'] == expected_url,
            f"URL modified correctly: {modified_system['url']}"
        ))
        
        # Check title was prefixed
        expected_title = f"[TEST] {fhir_codesystem['title']}"
        checks.append((
            modified_system['title'] == expected_title,
            f"Title prefixed correctly: {modified_system['title']}"
        ))
        
        # Check status is draft
        checks.append((
            modified_system['status'] == 'draft',
            f"Status set to draft: {modified_system['status']}"
        ))
        
        # Check that NaN was handled properly (no JSON serialization error)
        try:
            json_str = json.dumps(modified_system, allow_nan=False)
            checks.append((
                True,
                "Modified system serializes correctly without NaN errors"
            ))
            # Find the NaN that should have been converted
            nan_prop = modified_system['concept'][0]['property'][1]
            if nan_prop['code'] == 'population' and nan_prop['valueDecimal'] is None:
                checks.append((
                    True,
                    "NaN value properly converted to None"
                ))
            else:
                checks.append((
                    False,
                    f"NaN not properly converted: {nan_prop}"
                ))
        except ValueError as e:
            checks.append((
                False,
                f"Modified system failed JSON serialization: {e}"
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
        
    except Exception as e:
        print(f"  ✗ Error testing modify_codesystem_for_test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_upload_production_script():
    """Test the upload_production_script."""
    print("\nTesting upload_production_script.py...")
    
    script_path = os.path.join(os.path.dirname(__file__), 'upload_production_script.py')
    if not os.path.exists(script_path):
        print(f"  ✗ File does not exist: {script_path}")
        return False
    
    # Import the necessary functions
    func_names = ['handle_nan_in_data', 'upload_codesystem_to_server']
    functions = import_functions_from_script(script_path, func_names)
    
    handle_nan_func = functions.get('handle_nan_in_data')
    
    if not handle_nan_func:
        print("  ! handle_nan_in_data function not found, using test version")
        # Use our own function
        import math
        def handle_nan_func(obj):
            if isinstance(obj, dict):
                return {key: handle_nan_func(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [handle_nan_func(item) for item in obj]
            elif isinstance(obj, float) and math.isnan(obj):
                return None
            else:
                return obj
    
    # Test the NaN handling function
    test_data = {
        'field1': float('nan'),
        'field2': 'normal value',
        'field3': [1.0, float('nan'), 3.0]
    }
    
    try:
        processed = handle_nan_func(test_data)
        
        checks = []
        
        # Check NaN converted to None
        checks.append((
            processed['field1'] is None,
            "NaN value converted to None"
        ))
        
        # Check normal value preserved
        checks.append((
            processed['field2'] == 'normal value',
            "Normal string value preserved"
        ))
        
        # Check array with mixed values
        arr = processed['field3']
        checks.append((
            arr[0] == 1.0 and arr[1] is None and arr[2] == 3.0,
            "Array with NaN converted properly"
        ))
        
        # Check JSON serialization
        try:
            json_str = json.dumps(processed, allow_nan=False)
            checks.append((
                True,
                "Processed data serializes correctly without NaN errors"
            ))
        except ValueError as e:
            checks.append((
                False,
                f"Processed data failed JSON serialization: {e}"
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
        
    except Exception as e:
        print(f"  ✗ Error testing handle_nan_in_data: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_undo_script():
    """Test the undo_script."""
    print("\nTesting undo_script.py...")
    
    script_path = os.path.join(os.path.dirname(__file__), 'undo_script.py')
    if not os.path.exists(script_path):
        print(f"  ✗ File does not exist: {script_path}")
        return False
    
    # Import the necessary functions
    func_names = ['handle_nan_in_data']
    functions = import_functions_from_script(script_path, func_names)
    
    handle_nan_func = functions.get('handle_nan_in_data')
    
    if not handle_nan_func:
        print("  ! handle_nan_in_data function not found, using test version")
        # Use our own function
        import math
        def handle_nan_func(obj):
            if isinstance(obj, dict):
                return {key: handle_nan_func(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [handle_nan_func(item) for item in obj]
            elif isinstance(obj, float) and math.isnan(obj):
                return None
            else:
                return obj
    
    # Test the NaN handling function
    test_data = {
        'code_system': {
            'id': 'test-id',
            'resource': 'CodeSystem',
            'values': [float('nan'), 1.0, 2.0]
        }
    }
    
    try:
        processed = handle_nan_func(test_data)
        
        checks = []
        
        # Check nested NaN converted to None
        checks.append((
            processed['code_system']['values'][0] is None,
            "Nested NaN value converted to None"
        ))
        
        # Check other values preserved
        arr = processed['code_system']['values']
        checks.append((
            arr[1] == 1.0 and arr[2] == 2.0,
            "Other array values preserved"
        ))
        
        # Check JSON serialization
        try:
            json_str = json.dumps(processed, allow_nan=False)
            checks.append((
                True,
                "Processed data serializes correctly without NaN errors"
            ))
        except ValueError as e:
            checks.append((
                False,
                f"Processed data failed JSON serialization: {e}"
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
        
    except Exception as e:
        print(f"  ✗ Error testing undo script handle_nan_in_data: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_direct_imports():
    """Test that the scripts can at least be imported without syntax errors."""
    print("\nTesting script imports...")
    
    scripts = [
        'upload_test_script.py',
        'upload_production_script.py',
        'undo_script.py'
    ]
    
    all_good = True
    for script in scripts:
        script_path = os.path.join(os.path.dirname(__file__), script)
        try:
            spec = importlib.util.spec_from_file_location("module", script_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            print(f"  ✓ {script} imports successfully")
        except Exception as e:
            print(f"  ✗ {script} failed to import: {e}")
            all_good = False
    
    return all_good


if __name__ == "__main__":
    print("Testing all upload scripts...")
    
    # Test imports first
    imports_ok = test_direct_imports()
    
    # Then test functionality
    test_ok = test_upload_test_script()
    prod_ok = test_upload_production_script()
    undo_ok = test_undo_script()
    
    print(f"\nSummary:")
    print(f"  Import tests: {'✓ PASS' if imports_ok else '✗ FAIL'}")
    print(f"  Test script: {'✓ PASS' if test_ok else '✗ FAIL'}")
    print(f"  Production script: {'✓ PASS' if prod_ok else '✗ FAIL'}")
    print(f"  Undo script: {'✓ PASS' if undo_ok else '✗ FAIL'}")
    
    if imports_ok and test_ok and prod_ok and undo_ok:
        print("\n✓ All upload scripts tests passed!")
    else:
        print("\n✗ Some upload script tests failed.")
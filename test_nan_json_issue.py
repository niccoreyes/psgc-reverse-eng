#!/usr/bin/env python3
"""
Test to reproduce the original issue with pandas and NaN values.
"""

import math
import json

def test_json_with_nan():
    """Test how Python handles NaN in JSON serialization"""
    print("Testing JSON with NaN values...")
    
    # Test with NaN in different contexts
    test_values = [
        float('nan'),
        {"value": float('nan')},
        {"values": [1.0, float('nan'), 3.0]},
    ]
    
    for i, val in enumerate(test_values):
        print(f"\nTest {i+1}: {val}")
        try:
            # Default behavior
            result = json.dumps(val)
            print(f"  json.dumps() success: {result}")
        except ValueError as e:
            print(f"  json.dumps() failed: {e}")
            
        try:
            # With allow_nan=False (this should fail for NaN)
            result = json.dumps(val, allow_nan=False)
            print(f"  json.dumps(allow_nan=False) success: {result}")
        except ValueError as e:
            print(f"  json.dumps(allow_nan=False) failed: {e}")

def simulate_pandas_nan():
    """Simulate what happens with pandas-generated data containing NaN"""
    print("\nSimulating pandas-like NaN behavior...")
    
    # This simulates what might come from pandas
    import sys
    if sys.version_info >= (3, 13):
        # In Python 3.13, json may allow_nan by default in some contexts
        # Let's try to force the error with a more complex nested structure
        complex_data = {
            'data': [
                {'id': 1, 'value': 10.5},
                {'id': 2, 'value': float('nan')},
                {'id': 3, 'value': 15.7}
            ],
            'metadata': {
                'avg': float('nan'),
                'count': 3
            }
        }
        
        print("Complex data structure with NaN:")
        print(f"  Data: {complex_data}")
        
        # Try regular JSON serialization
        try:
            result = json.dumps(complex_data, allow_nan=False)
            print(f"  json.dumps(allow_nan=False) success: {result}")
        except ValueError as e:
            print(f"  json.dumps(allow_nan=False) failed: {e}")
            
        # This should definitely fail when allow_nan=False
        try:
            result = json.dumps(complex_data, allow_nan=False)
            print("  ERROR: This should have failed but didn't!")
        except ValueError as e:
            print(f"  Confirmed: json.dumps(allow_nan=False) fails as expected: {e}")
            return True
    
    return False

def test_original_problem():
    """Test the original problem: json.loads(json.dumps(obj)) with NaN"""
    print("\nTesting original problem: json.loads(json.dumps(obj)) with NaN...")
    
    obj_with_nan = {
        'value': float('nan'),
        'values': [1.0, float('nan'), 3.0]
    }
    
    print(f"Original object: {obj_with_nan}")
    
    try:
        # This is the original problematic pattern from the code
        result = json.loads(json.dumps(obj_with_nan, allow_nan=False))
        print(f"  json.loads(json.dumps(obj, allow_nan=False)) success: {result}")
        return False  # This shouldn't succeed if NaN is problematic
    except ValueError as e:
        print(f"  json.loads(json.dumps(obj, allow_nan=False)) failed: {e}")
        return True  # This is the expected behavior

if __name__ == "__main__":
    test_json_with_nan()
    simulate_pandas_nan()
    
    problem_exists = test_original_problem()
    if problem_exists:
        print("\nThe original problem exists when allow_nan=False")
    else:
        print("\nThe original problem may not occur in this Python version by default")
        print("But it would occur if allow_nan=False is explicitly set or in certain contexts")
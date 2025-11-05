#!/usr/bin/env python3
"""
Integration test to verify that Pateros fix works in the context of the full hierarchy processing.
"""

import sys
import os
import json
import tempfile
from unittest.mock import Mock

# Add the script directory to Python path
sys.path.insert(0, os.path.abspath('.'))

from psgc_fhir_converter import get_parent_code, get_parent_code_with_validation, parse_geographic_hierarchy
import pandas as pd

def test_integration():
    """
    Test that the Pateros fix works in the full processing context.
    """
    print("Testing integration of Pateros fix in full processing pipeline...")
    
    # Create a minimal mock dataset with Pateros and some surrounding NCR context
    mock_data = {
        '10-digit PSGC': ['1300000000', '1381701000', '1381701001', '1380600000'],  # NCR, Pateros, Pateros barangay, Manila
        'Name': ['National Capital Region (NCR)', 'Pateros', 'Aguho', 'City of Manila'],
        'Geographic Level': ['Reg', 'Mun', 'Bgy', 'City']
    }
    
    df = pd.DataFrame(mock_data)
    
    print("Created mock PSGC data with NCR, Pateros, and Manila...")
    
    # Test the parse_geographic_hierarchy function to ensure it works with our changes
    try:
        geographic_hierarchy = parse_geographic_hierarchy(df)
        print("✅ parse_geographic_hierarchy executed successfully")
        
        # Find the Pateros entry in the results
        pateros_entry = None
        ncr_entry = None
        manila_entry = None
        for entry in geographic_hierarchy:
            if entry['code'] == '1381701000':
                pateros_entry = entry
            elif entry['code'] == '1300000000':
                ncr_entry = entry
            elif entry['code'] == '1380600000':
                manila_entry = entry
        
        if pateros_entry and ncr_entry:
            print(f"✅ Found Pateros in results: {pateros_entry}")
            print(f"✅ Pateros parent_code: {pateros_entry.get('parent_code')}")
            
            # Verify that Pateros has NCR as parent
            if pateros_entry.get('parent_code') == '1300000000':
                print("✅ Pateros correctly has NCR as parent in the parsed hierarchy")
            else:
                print(f"❌ Pateros has wrong parent in hierarchy. Expected: 1300000000, Got: {pateros_entry.get('parent_code')}")
                return False
        else:
            print("❌ Could not find Pateros or NCR in the results")
            return False
        
        if manila_entry:
            print(f"✅ Found Manila in results: {manila_entry}")
            print(f"✅ Manila parent_code: {manila_entry.get('parent_code')}")
            
            # Verify that Manila still has NCR as parent (no regression)
            if manila_entry.get('parent_code') == '1300000000':
                print("✅ Manila still correctly has NCR as parent (no regression)")
            else:
                print(f"❌ Manila has wrong parent. Expected: 1300000000, Got: {manila_entry.get('parent_code')}")
                return False
        else:
            print("❌ Could not find Manila in the results")
            return False
        
        print("\n✅ Integration test passed! Pateros fix works correctly in full processing pipeline.")
        return True
        
    except Exception as e:
        print(f"❌ Error in integration test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_parent_validation_function():
    """
    Test the get_parent_code_with_validation function with Pateros to make sure validation works correctly
    """
    print("\nTesting get_parent_code_with_validation with Pateros...")
    
    # Create a set with valid codes that includes NCR
    valid_codes = {'1300000000', '1381701000', '1380600000'}  # NCR, Pateros, Manila
    
    # Test Pateros parent with validation
    pateros_parent = get_parent_code_with_validation('1381701000', 'Mun', valid_codes)
    print(f"Pateros with validation has parent: {pateros_parent}")
    
    if pateros_parent == '1300000000':  # NCR
        print("✅ get_parent_code_with_validation correctly returns NCR for Pateros")
        return True
    else:
        print(f"❌ get_parent_code_with_validation failed. Expected: 1300000000, Got: {pateros_parent}")
        return False

if __name__ == "__main__":
    success1 = test_integration()
    success2 = test_parent_validation_function()
    
    if success1 and success2:
        print("\n🎉 All integration tests passed!")
    else:
        print("\n❌ Some integration tests failed!")
        sys.exit(1)
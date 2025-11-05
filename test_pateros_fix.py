#!/usr/bin/env python3
"""
Test script to verify that Pateros (1381701000) now has NCR (1300000000) as parent
instead of the intermediate code (1381700000).
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from psgc_fhir_converter import get_parent_code

def test_pateros_parent():
    """
    Test that Pateros (1381701000) has NCR (1300000000) as its parent.
    """
    print("Testing Pateros parent relationship...")
    
    # Test Pateros with different level classifications
    pateros_code = "1381701000"
    
    # Test with 'Mun' level (as it appears in the data)
    parent_mun = get_parent_code(pateros_code, 'Mun')
    print(f"Pateros ({pateros_code}) with level 'Mun' has parent: {parent_mun}")
    
    # Test with 'City' level (for comparison)
    parent_city = get_parent_code(pateros_code, 'City')
    print(f"Pateros ({pateros_code}) with level 'City' has parent: {parent_city}")
    
    # Verify that both return NCR (1300000000)
    expected_parent = "1300000000"  # NCR
    if parent_mun == expected_parent:
        print("✅ Pateros with 'Mun' level correctly has NCR as parent")
    else:
        print(f"❌ Pateros with 'Mun' level has wrong parent. Expected: {expected_parent}, Got: {parent_mun}")
        return False
    
    if parent_city == expected_parent:
        print("✅ Pateros with 'City' level correctly has NCR as parent")
    else:
        print(f"❌ Pateros with 'City' level has wrong parent. Expected: {expected_parent}, Got: {parent_city}")
        return False
    
    # Test that other NCR cities still work correctly
    manila_code = "1380600000"
    parent_manila = get_parent_code(manila_code, 'City')
    print(f"\nManila ({manila_code}) has parent: {parent_manila}")
    
    if parent_manila == expected_parent:
        print("✅ Manila still correctly has NCR as parent")
    else:
        print(f"❌ Manila has wrong parent. Expected: {expected_parent}, Got: {parent_manila}")
        return False
    
    # Test that non-NCR municipalities still work correctly
    non_ncr_mun_code = "0401001000"  # Example from Batangas
    parent_non_ncr_mun = get_parent_code(non_ncr_mun_code, 'Mun')
    expected_non_ncr_parent = "0401000000"  # Batangas province
    print(f"\nNon-NCR municipality ({non_ncr_mun_code}) has parent: {parent_non_ncr_mun}")
    
    if parent_non_ncr_mun == expected_non_ncr_parent:
        print("✅ Non-NCR municipality still correctly has province as parent")
    else:
        print(f"❌ Non-NCR municipality has wrong parent. Expected: {expected_non_ncr_parent}, Got: {parent_non_ncr_mun}")
        return False
    
    print("\n🎉 All tests passed! Pateros is now correctly positioned under NCR.")
    return True

if __name__ == "__main__":
    success = test_pateros_parent()
    if not success:
        sys.exit(1)
    else:
        print("\n✅ All tests passed successfully!")
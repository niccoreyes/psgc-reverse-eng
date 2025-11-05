#!/usr/bin/env python3
"""
Test the updated PSGC hierarchy logic
"""

def get_parent_code(psgc_code: str, level: str) -> str:
    """
    Determine the parent PSGC code based on the PSGC structure:
    - Positions 1-2: Region code
    - Positions 3-5: Province code  
    - Positions 6-7: Municipality code
    - Positions 8-10: Barangay code
    
    Geographic hierarchy:
    - Root: Philippine Standard Geographic Code (0000000000)
    - Reg (Region): Child of Root
    - Prov (Province): Child of Region
    - City/Mun (City/Municipality): Child of Province (or Region if highly urbanized city)
    - Bgy (Barangay): Child of City/Municipality
    - SubMun (Sub-Municipality): Child of City/Municipality (not implemented in this function)
    
    Args:
        psgc_code (str): The 10-digit PSGC code
        level (str): Geographic level (Reg, Prov, City, Mun, Bgy)
        
    Returns:
        str: The parent PSGC code or '0000000000' if no parent (for regions)
    """
    # Ensure code is 10 digits with leading zeros if needed
    code = str(psgc_code).strip().zfill(10)
    
    if level == 'Reg':
        # Regions are children of the root Philippine Standard Geographic Code
        return '0000000000'
    elif level == 'Prov':
        # Provinces belong to regions (first 2 digits + zeros)
        return code[:2].ljust(10, '0')
    elif level in ['City', 'Mun']:  # City or Municipality
        # Cities/Municipalities belong to provinces (first 5 digits + zeros)
        province_code = code[:5].ljust(10, '0')
        region_code = code[:2].ljust(10, '0')
        
        # If the province code is the same as the current code, this is a highly urbanized city
        # that belongs directly to the region, not to a province
        if province_code == code:
            return region_code
        else:
            return province_code
    elif level == 'Bgy':  # Barangay
        # Barangays belong to municipalities/cities (first 7 digits + zeros)
        return code[:7].ljust(10, '0')
    elif level == 'SubMun':  # SubMunicipality
        # SubMunicipalities belong to municipalities/cities (first 7 digits + zeros)
        return code[:7].ljust(10, '0')
    else:
        # For other levels or unknown types
        return '0000000000'  # Default to root


def test_hierarchy():
    """Test the hierarchy implementation"""
    test_cases = [
        ('1380100000', 'City'),  # City of Caloocan - in NCR, so directly under region
        ('1381701001', 'Bgy'),   # Barangay example
        ('0381700000', 'Prov'),  # Province example
        ('0381701000', 'Mun'),   # Municipality example (belongs to a province)
        ('1300000000', 'Reg'),   # Region example
        ('1750700000', 'Prov'),  # Another province example
        ('1750701000', 'Mun'),   # Municipality in that province
        ('1750701001', 'Bgy'),   # Barangay in that municipality
        ('0645800000', 'City'),  # Another highly urbanized city that reports directly to region
    ]

    print('Testing the updated get_parent_code function:')
    print('PSGC Code Structure:')
    print('- First 2 digits: Region code')
    print('- Next 3 digits: Province code')
    print('- Next 2 digits: Municipality code')
    print('- Last 3 digits: Barangay code')
    print()
    
    for psgc_code, level in test_cases:
        parent = get_parent_code(psgc_code, level)
        print(f'Code: {psgc_code}, Level: {level} -> Parent: {parent}')
    
    print()
    print('Expected hierarchy relationships:')
    print('- Region (e.g. 1300000000) should have parent: 0000000000 (root)')
    print('- Province (e.g. 0381700000) should have parent: 0300000000 (region)')
    print('- Municipality in province (e.g. 0381701000) should have parent: 0381700000 (province)') 
    print('- Barangay (e.g. 0381701001) should have parent: 0381701000 (city/municipality)')
    print('- Highly urbanized city (e.g. 1380100000) should have parent: 1300000000 (region)')
    print()
    
    # Verify correct hierarchy
    print('Verifying hierarchy correctness:')
    # Province parent (should be region)
    province_parent = get_parent_code('0381700000', 'Prov')
    print(f'Province 0381700000 parent: {province_parent} (expected: 0300000000) - {province_parent == "0300000000" and "✓" or "✗"}')
    
    # Municipality in province parent (should be province)
    mun_parent = get_parent_code('0381701000', 'Mun')
    print(f'Municipality 0381701000 parent: {mun_parent} (expected: 0381700000) - {mun_parent == "0381700000" and "✓" or "✗"}')
    
    # Barangay parent (should be its city/municipality)
    bgy_parent = get_parent_code('0381701001', 'Bgy')
    print(f'Barangay 0381701001 parent: {bgy_parent} (expected: 0381701000) - {bgy_parent == "0381701000" and "✓" or "✗"}')
    
    # Region parent (should be root)
    reg_parent = get_parent_code('1300000000', 'Reg')
    print(f'Region 1300000000 parent: {reg_parent} (expected: 0000000000) - {reg_parent == "0000000000" and "✓" or "✗"}')
    
    # Highly urbanized city parent (should be region)
    huc_parent = get_parent_code('1380100000', 'City')
    print(f'Highly urbanized city 1380100000 parent: {huc_parent} (expected: 1300000000) - {huc_parent == "1300000000" and "✓" or "✗"}')


if __name__ == "__main__":
    test_hierarchy()
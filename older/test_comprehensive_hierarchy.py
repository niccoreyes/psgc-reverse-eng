#!/usr/bin/env python3
"""
Comprehensive test for the hierarchy implementation with validation
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


def get_parent_code_with_validation(psgc_code: str, level: str, valid_codes: set) -> str:
    """
    Determine the parent PSGC code and validate that it exists in the dataset.
    If the calculated parent code doesn't exist in the dataset, returns None.
    This function addresses the "Parent code not found" validation errors that
    occur when FHIR servers validate parent-child relationships in CodeSystems.
    
    Args:
        psgc_code (str): The 10-digit PSGC code
        level (str): Geographic level (Reg, Prov, City, Mun, Bgy)
        valid_codes (set): Set of all valid PSGC codes in the dataset
        
    Returns:
        Optional[str]: The parent PSGC code that exists in the dataset, or None
    """
    potential_parent = get_parent_code(psgc_code, level)
    if potential_parent and potential_parent in valid_codes:
        return potential_parent
    else:
        # This handles the case where the calculated parent code doesn't exist in the dataset
        # Previously, this would cause "Parent code not found" errors during FHIR server validation
        return None


def parse_geographic_hierarchy_mock(data_rows):
    """
    Mock parsing of geographic hierarchy based on our updated logic.
    This would typically process a DataFrame but we'll use a simplified version.
    """
    # Create a set of valid codes to validate parent codes against
    valid_codes = {row['code'] for row in data_rows}
    
    geographic_data = []
    
    for row in data_rows:
        psgc_code = row['code']
        name = row['name']
        level = row['level']
        # Use validated parent calculation to ensure parent codes exist in the dataset
        parent_code = get_parent_code_with_validation(psgc_code, level, valid_codes)
        
        geographic_entity = {
            'code': psgc_code,
            'display': name,
            'definition': f"PSGC geographic code for {name}",
            'level': level,
            'parent_code': parent_code
        }
        
        geographic_data.append(geographic_entity)
    
    return geographic_data


def build_hierarchy_tree(geographic_data):
    """
    Build a hierarchical tree structure from geographic data.
    This function now handles missing parent codes gracefully by treating entities
    with non-existent parents as root-level entities.
    
    Args:
        geographic_data: List of geographic entities with hierarchy information
        
    Returns:
        List: Tree structure of concepts with nested hierarchy
    """
    # Create a mapping from code to entity for quick lookups
    geo_map = {entity['code']: {**entity, 'children': []} for entity in geographic_data}
    
    # Create root level entities (those with no parent or parent not in the dataset)
    roots = []
    
    for entity in geo_map.values():
        parent_code = entity['parent_code']
        if parent_code and parent_code in geo_map:
            # Add this entity as a child to its parent (valid parent-child relationship)
            geo_map[parent_code]['children'].append(entity)
        else:
            # This is a root level entity (no parent or parent doesn't exist in dataset)
            # This handles the case where the parent code was calculated but doesn't exist in the dataset
            # The entity is treated as a root-level entity in the hierarchy
            roots.append(entity)
    
    return roots


def validate_parent_child_relationships(geographic_data):
    """
    Validates parent-child relationships in geographic data to ensure all parent codes exist.
    
    Args:
        geographic_data: List of geographic entities with hierarchy information
        
    Returns:
        List: List of error messages for any invalid relationships found
    """
    errors = []
    # Create a set of all valid codes for quick lookup
    valid_codes = {entity['code'] for entity in geographic_data}
    
    for entity in geographic_data:
        entity_code = entity['code']
        parent_code = entity.get('parent_code')
        
        if parent_code:
            if parent_code not in valid_codes:
                errors.append(f"Entity {entity_code} has parent code {parent_code} that does not exist in dataset")
    
    return errors


def test_comprehensive():
    """Comprehensive test of the hierarchy implementation"""
    # Sample data that represents the Philippines geographic structure
    sample_data = [
        {'code': '0000000000', 'name': 'Philippine Standard Geographic Code', 'level': 'Root'},
        {'code': '1300000000', 'name': 'National Capital Region (NCR)', 'level': 'Reg'},
        {'code': '0300000000', 'name': 'Central Luzon', 'level': 'Reg'},
        {'code': '0381700000', 'name': 'Rizal', 'level': 'Prov'},
        {'code': '0381701000', 'name': 'Antipolo', 'level': 'Mun'},
        {'code': '0381701001', 'name': 'Barangay 1, Antipolo', 'level': 'Bgy'},
        {'code': '1380100000', 'name': 'City of Caloocan', 'level': 'City'},  # HUC, directly under NCR
        {'code': '1380101001', 'name': 'Barangay 1, Caloocan', 'level': 'Bgy'},
    ]
    
    print("Comprehensive Hierarchy Test")
    print("=" * 40)
    print("Sample data:")
    for item in sample_data:
        print(f"  {item['code']}: {item['name']} ({item['level']})")
    
    # Parse the geographic hierarchy
    geographic_hierarchy = parse_geographic_hierarchy_mock(sample_data)
    
    print(f"\nParsed hierarchy with {len(geographic_hierarchy)} entities")
    print("Parent relationships:")
    for entity in geographic_hierarchy:
        parent = entity.get('parent_code', 'None')
        print(f"  {entity['code']} -> {parent}")
    
    # Build the hierarchy tree
    hierarchy_tree = build_hierarchy_tree(geographic_hierarchy)
    
    print(f"\nHierarchy tree built with {len(hierarchy_tree)} root entities")
    
    # Validate parent-child relationships
    validation_errors = validate_parent_child_relationships(geographic_hierarchy)
    
    print(f"\nValidation results:")
    print(f"Total entities: {len(geographic_hierarchy)}")
    print(f"Validation errors found: {len(validation_errors)}")
    
    if validation_errors:
        print("\nDetailed errors:")
        for error in validation_errors:
            print(f"  - {error}")
    else:
        print("No parent-child relationship errors found!")
    
    # Test that regions are direct children of root concept
    root_concept = {'code': '0000000000'}
    
    regions = []
    for entity in geographic_hierarchy:
        if entity['parent_code'] == root_concept['code']:
            regions.append(entity)
    
    print(f"\nRegions that are direct children of root (0000000000):")
    for region in regions:
        print(f"  - {region['code']}: {region['display']}")
    
    print(f"\nTotal regions: {len(regions)}")
    
    # Test validation with missing parent
    print(f"\nTesting validation with missing parent:")
    # Create data with a missing parent
    invalid_data = [
        {'code': '1380100000', 'name': 'City of Caloocan', 'level': 'City'},
        # Missing parent '1300000000' region
    ]
    
    invalid_hierarchy = parse_geographic_hierarchy_mock(invalid_data)
    invalid_errors = validate_parent_child_relationships(invalid_hierarchy)
    
    print(f"Entities with missing parents in test: {len(invalid_errors)}")
    for error in invalid_errors:
        print(f"  - {error}")


if __name__ == "__main__":
    test_comprehensive()
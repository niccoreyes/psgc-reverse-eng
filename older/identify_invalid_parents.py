#!/usr/bin/env python3
"""
Script to identify concepts that have invalid parent references in the PSGC dataset.
"""

import pandas as pd
from psgc_fhir_converter import (
    parse_geographic_hierarchy,
    validate_parent_child_relationships,
    get_parent_code_with_validation
)


def identify_invalid_parent_references(file_path):
    """
    Identify and report concepts that have invalid parent references in the dataset.
    
    Args:
        file_path (str): Path to the PSGC Excel file
    """
    print("Reading PSGC Excel file...")
    df = pd.read_excel(file_path, sheet_name='PSGC')
    
    # Clean up the column names (remove special characters or spaces)
    df.columns = df.columns.str.strip()
    
    print(f"Successfully read PSGC data with {len(df)} entries")
    
    # Create a set of valid codes to validate parent codes against
    valid_codes = set()
    for _, row in df.iterrows():
        psgc_code = str(row['10-digit PSGC']).strip()
        valid_codes.add(psgc_code)
    
    print(f"Created set of {len(valid_codes)} valid codes")
    
    # Identify concepts with parents that don't exist in dataset
    invalid_parent_refs = []
    
    for _, row in df.iterrows():
        psgc_code = str(row['10-digit PSGC']).strip()
        name = row['Name']
        level = row['Geographic Level']
        
        # Calculate what the parent code should be
        potential_parent = get_parent_code_with_validation(psgc_code, level, valid_codes)
        
        # Calculate what the original parent would have been without validation
        from psgc_fhir_converter import get_parent_code
        original_parent = get_parent_code(psgc_code, level)
        
        if original_parent and original_parent not in valid_codes:
            invalid_parent_refs.append({
                'code': psgc_code,
                'name': name,
                'level': level,
                'original_calculated_parent': original_parent,
                'has_valid_parent': potential_parent is not None
            })
    
    print(f"\nFound {len(invalid_parent_refs)} concepts with invalid parent references:")
    
    if invalid_parent_refs:
        print("\nDetails of invalid parent references:")
        for idx, item in enumerate(invalid_parent_refs[:20]):  # Show first 20
            print(f"{idx+1}. Code: {item['code']}, Name: {item['name']}, "
                  f"Level: {item['level']}, Original parent: {item['original_calculated_parent']}, "
                  f"Has valid parent after fix: {item['has_valid_parent']}")
        
        if len(invalid_parent_refs) > 20:
            print(f"\n... and {len(invalid_parent_refs) - 20} more")
    
    # Test the parsed hierarchy with validation
    print("\nValidating parsed hierarchy...")
    geographic_data = parse_geographic_hierarchy(df)
    
    # Check for invalid parent-child relationships in the parsed hierarchy
    errors = validate_parent_child_relationships(geographic_data)
    
    print(f"\nValidation results:")
    print(f"Total entries in hierarchy: {len(geographic_data)}")
    print(f"Validation errors found: {len(errors)}")
    
    if errors:
        print("\nDetailed errors:")
        for idx, error in enumerate(errors[:20]):  # Show first 20
            print(f"{idx+1}. {error}")
        if len(errors) > 20:
            print(f"\n... and {len(errors) - 20} more")
    else:
        print("No parent-child relationship errors found!")
    
    return invalid_parent_refs, errors


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print("Usage: python identify_invalid_parents.py <psgc_excel_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    identify_invalid_parent_references(file_path)
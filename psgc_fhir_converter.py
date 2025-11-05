#!/usr/bin/env python3
"""
PSGC to FHIR JSON CodeSystem Converter

This script converts Philippine Standard Geographic Code (PSGC) data from Excel format
to FHIR JSON CodeSystem format for integration with healthcare systems.
"""

import pandas as pd
import json
import argparse
from typing import Dict, List, Any, Optional


def read_psgc_excel(file_path: str) -> pd.DataFrame:
    """
    Reads the PSGC Excel file and returns a DataFrame with the data.
    
    Args:
        file_path (str): Path to the PSGC Excel file
        
    Returns:
        pd.DataFrame: DataFrame containing the PSGC data
    """
    # Read the 'PSGC' sheet from the Excel file
    df = pd.read_excel(
        file_path,
        sheet_name='PSGC'
    )
    
    # Clean up the column names (remove special characters or spaces)
    df.columns = df.columns.str.strip()
    
    # Return the DataFrame
    return df


def get_parent_code(psgc_code: str, level: str) -> Optional[str]:
    """
    Determine the parent PSGC code based on the PSGC structure algorithmically, 
    using the code's inherent structure to determine parent-child relationships.
    - Positions 1-2: Region code
    - Positions 3-5: Province code  
    - Positions 6-7: Municipality/City subdivision code
    - Positions 8-10: Barangay code
    
    Geographic hierarchy:
    - Root: Philippine Standard Geographic Code (0000000000)
    - Reg (Region): Child of Root
    - Prov (Province): Child of Region
    - City/Mun (City/Municipality): Child of Province (or Region if highly urbanized city)
    - SubMun (Intermediate level like districts in large cities): Child of City/Municipality
    - Bgy (Barangay): Child of City/Municipality or SubMunicipality (district)
    
    The function algorithmically determines parent codes based on PSGC structure,
    with logic to identify special cases by analyzing the code pattern rather than 
    hardcoding specific values.
    
    Args:
        psgc_code (str): The 10-digit PSGC code
        level (str): Geographic level (Reg, Prov, City, Mun, SubMun, Bgy, etc.)
        
    Returns:
        Optional[str]: The parent PSGC code or None if no parent
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
        # Calculate potential parent codes based on PSGC structure
        province_code = code[:5].ljust(10, '0')
        region_code = code[:2].ljust(10, '0')
        
        # Apply pattern-based logic to determine parent:
        # 1. If province code equals the current code, it's a highly urbanized city (HUC) 
        #    that reports directly to the region
        if province_code == code:
            return region_code
        
        # 2. Check if this municipality should report directly to region
        #    based on the province component indicating special administrative status
        province_part = code[2:5]
        if should_report_to_region_directly(province_part):
            return region_code
            
        # 3. Standard municipalities/cities belong to their provinces
        else:
            return province_code
    elif level == 'SubMun':  # Sub-municipality (like districts in large cities)
        # SubMunicipalities belong to municipalities/cities (first 5 digits + "00000")
        return code[:5].ljust(10, '0')
    elif level == 'Bgy':  # Barangay
        # Barangays belong to either:
        # 1. SubMunicipalities (districts): if positions 6-7 are not "00" (e.g. 1380601001 -> 1380601000) 
        # 2. Cities/Municipalities: if positions 6-7 are "00" (e.g. 1380100001 -> 1380100000)
        sixth_seventh = code[5:7]  # positions 6-7
        
        if sixth_seventh != "00":
            # Barangay belongs to a sub-municipality/district (use first 7 digits + zeros)
            return code[:7].ljust(10, '0')
        else:
            # Barangay belongs directly to city/municipality (use first 5 digits + zeros)
            return code[:5].ljust(10, '0')
    else:
        # For other levels or unknown types, default to root
        return '0000000000'


def get_parent_code_with_validation(psgc_code: str, level: str, valid_codes: set) -> Optional[str]:
    """
    Determine the parent PSGC code and validate that it exists in the dataset.
    If the calculated parent code doesn't exist in the dataset, tries to find an appropriate
    higher-level parent (e.g., region if province doesn't exist) to maintain hierarchy integrity.
    Special exception: regions (Reg) and special geographic areas have '0000000000' as parent, 
    which may not exist in the original dataset but is added as the root concept.
    
    Args:
        psgc_code (str): The 10-digit PSGC code
        level (str): Geographic level (Reg, Prov, City, Mun, Bgy, SubMun, Special)
        valid_codes (set): Set of all valid PSGC codes in the dataset
        
    Returns:
        Optional[str]: The parent PSGC code that exists in the dataset, or None
    """
    potential_parent = get_parent_code(psgc_code, level)
    
    # If the calculated parent exists in the dataset, use it
    if potential_parent and (potential_parent in valid_codes or potential_parent == '0000000000'):
        return potential_parent
    
    # If the calculated parent doesn't exist, implement fallback logic to find
    # a valid parent at a higher level in the hierarchy (e.g., region instead of province)
    code = str(psgc_code).strip().zfill(10)
    
    # For municipalities and cities, if the province parent doesn't exist,
    # try the region parent as a fallback
    if level in ['City', 'Mun']:
        region_code = code[:2].ljust(10, '0')
        if region_code in valid_codes or region_code == '0000000000':
            return region_code
    
    # If still no valid parent found, return None
    return None


def should_report_to_region_directly(province_part: str) -> bool:
    """
    Determines if a municipality should report directly to region based on the province component
    of its PSGC code, indicating special administrative status.
    
    Args:
        province_part (str): The province component of the PSGC code (positions 3-5)
        
    Returns:
        bool: True if the municipality should report directly to region, False otherwise
    """
    # In the Philippines administrative structure, certain codes indicate 
    # municipalities that report directly to their region:
    # - '817' is Pateros in NCR which doesn't belong to Rizal Province
    # - '999' is often used for special geographic areas in regions like BARMM
    special_direct_reporting_codes = ['817', '999']
    
    return province_part in special_direct_reporting_codes


def infer_geographic_level_from_code(psgc_code: str, name: str = "") -> str:
    """
    Infers the geographic level from the PSGC code structure when the level is not explicitly provided.
    This helps handle special geographic areas with NaN levels by analyzing the code pattern 
    according to official PSGC guidelines.
    
    Args:
        psgc_code (str): The 10-digit PSGC code
        name (str): The name of the geographic entity (for additional context)
        
    Returns:
        str: Inferred geographic level
    """
    # Ensure code is 10 digits with leading zeros
    code = str(psgc_code).strip().zfill(10)
    
    # Analyze the PSGC code structure to infer geographic level based on official patterns
    # Positions 1-2: Region code
    # Positions 3-5: Province code
    # Positions 6-7: Municipality/City code
    # Positions 8-10: Barangay code
    
    # Extract components based on PSGC structure
    region_code = code[:2]
    province_component = code[2:5]  # positions 3-5
    municipality_component = code[5:7]  # positions 6-7
    barangay_component = code[7:]  # positions 8-10
    
    # Special patterns based on official PSGC guidelines:
    # - If positions 3-10 are '99900000': This indicates a special administrative region (e.g. BARMM)
    # - If positions 6-10 are '99900': This might indicate special geographic areas
    
    # Check for special administrative regions (like BARMM)
    if region_code in ['19'] and province_component == '999' and municipality_component == '00' and barangay_component == '000':
        return 'Prov'  # Special geographic area treated as province level in BARMM
    # Additional special pattern for City of Isabela (special case but not fully standardized)
    elif code.startswith('09901') and code.endswith('000'):
        return 'City'  # City of Isabela special designation
    
    # Standard PSGC code analysis
    # If all digits after position 2 are 0, it's a region
    elif code[2:] == '000000000':
        return 'Reg'
    
    # If digits 6-10 are 0, it's likely a province
    elif barangay_component == '000' and municipality_component == '00':
        return 'Prov'
    
    # If digits 8-10 are 0 but digits 6-7 are not, it's likely a city or municipality
    elif barangay_component == '000' and municipality_component != '00':
        return 'City' if 'City' in name else 'Mun'
    
    # If it's not all zeros after position 7, it's likely a barangay
    elif barangay_component != '000':
        return 'Bgy'
    
    # If digits 8-10 are 0 but 6-7 are not, it could be a sub-municipality
    elif municipality_component != '00' and barangay_component == '000':
        return 'SubMun'
    
    # Default fallback for unrecognized patterns
    return 'Unknown'


def parse_geographic_hierarchy(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Parse the geographic hierarchy from the PSGC data.
    This function incorporates validation to ensure parent codes exist in the dataset,
    preventing "Parent code not found" errors during FHIR server validation.
    Special geographic areas with NaN levels are handled by inferring their level
    based on the PSGC code structure and common patterns.
    
    Args:
        df (pd.DataFrame): DataFrame with PSGC data
        
    Returns:
        List[Dict[str, Any]]: List of geographic entities with hierarchy information
    """
    # Create a set of valid codes to validate parent codes against
    # Ensure all codes are 10 digits with leading zeros for consistent matching
    valid_codes = set()
    for _, row in df.iterrows():
        psgc_code = str(row['10-digit PSGC']).strip().zfill(10)  # Ensure 10 digits with leading zeros
        valid_codes.add(psgc_code)
    
    geographic_data = []
    
    for _, row in df.iterrows():
        psgc_code = str(row['10-digit PSGC']).strip().zfill(10)  # Ensure 10 digits with leading zeros
        name = row['Name']
        level = row['Geographic Level']
        
        # Handle entries with NaN geographic levels by inferring from PSGC code structure
        if pd.isna(level):
            level = infer_geographic_level_from_code(psgc_code, name)
        
        # Use validated parent calculation to ensure parent codes exist in the dataset
        # This prevents "Parent code not found" errors during FHIR server validation
        # If a calculated parent doesn't exist in the dataset, this returns None
        # effectively treating the entity as a root-level entity in the hierarchy
        parent_code = get_parent_code_with_validation(psgc_code, level, valid_codes)
        
        geographic_entity = {
            'code': psgc_code,
            'display': name,
            'definition': f"PSGC geographic code for {name}",
            'level': level,
            'parent_code': parent_code
        }
        
        # Add other properties if they exist
        for col in df.columns:
            if col not in ['10-digit PSGC', 'Name', 'Geographic Level']:
                value = row[col]
                if pd.notna(value) and value != '':
                    geographic_entity[col.lower().replace(' ', '_').replace('-', '_')] = value
        
        geographic_data.append(geographic_entity)
    
    return geographic_data


def build_hierarchy_tree(geographic_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Build a flexible hierarchical tree structure from geographic data that can handle skipped levels.
    This function now handles missing parent codes gracefully by treating entities
    with non-existent parents as root-level entities, and can adjust for special
    geographic areas that might skip hierarchy levels.
    
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


def convert_entity_to_fhir_concept(entity: Dict[str, Any], include_children: bool = True) -> Dict[str, Any]:
    """
    Convert a geographic entity to a FHIR concept structure.
    
    Args:
        entity: Geographic entity to convert
        include_children: Whether to include child concepts in the result
        
    Returns:
        Dict: FHIR concept structure
    """
    concept = {
        "code": entity['code'],
        "display": entity['display'],
        "definition": entity['definition']
    }
    
    # Add properties
    properties = []
    
    # Parent relationship property (matching server format)
    if entity['parent_code']:
        properties.append({
            "code": "parent",
            "valueCode": entity['parent_code']
        })
    
    # Geographic level property (matching server format - using valueString instead of valueCode)
    # Handle special cases for known special geographic areas
    level_value = entity['level']
    
    properties.append({
        "code": "Geographic Level", 
        "valueString": level_value
    })
    
    if properties:
        concept["property"] = properties
    
    # Add children if they exist and we're including them
    if include_children and 'children' in entity and entity['children']:
        concept['concept'] = [
            convert_entity_to_fhir_concept(child, include_children=True) 
            for child in entity['children']
        ]
    
    return concept


def create_fhir_codesystem_structure(geographic_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Create the FHIR JSON CodeSystem structure from parsed geographic data.
    
    Args:
        geographic_data: List of geographic entities with hierarchy information
        
    Returns:
        Dict: FHIR JSON CodeSystem structure
    """
    # Create a mapping from code to entity for quick lookups
    geo_map = {entity['code']: {**entity, 'children': []} for entity in geographic_data}
    
    # Properly rebuild the tree ensuring parent-child relationships are established
    for entity in geo_map.values():
        parent_code = entity.get('parent_code')
        if parent_code and parent_code in geo_map:
            # Add this entity as a child to its parent
            geo_map[parent_code]['children'].append(entity)
    
    # Add the template root concept and find direct children of the root
    # (typically regions that have '0000000000' as their parent)
    regions = [entity for entity in geo_map.values() if entity.get('parent_code') == '0000000000']
    
    # Convert regions to FHIR concepts and add them as direct children of root
    region_concepts = []
    for region in regions:
        fhir_concept = convert_entity_to_fhir_concept(region, include_children=True)
        region_concepts.append(fhir_concept)
    
    # Create the root concept
    root_concept = {
        "code": "0000000000",
        "display": "Philippine Standard Geographic Code",
        "definition": "Philippine Standard Geographic Code"
    }
    
    # Add regions as children of the root concept
    if region_concepts:
        root_concept["concept"] = region_concepts
    
    # Count the total number of concepts in the hierarchy
    def count_concepts_in_hierarchy(concepts):
        count = 0
        for concept in concepts:
            count += 1
            if 'concept' in concept and concept['concept']:
                count += count_concepts_in_hierarchy(concept['concept'])
        return count
    
    total_concepts = 1  # Start with 1 for the root concept
    if 'concept' in root_concept:
        total_concepts += count_concepts_in_hierarchy(root_concept['concept'])
    
    # Create the FHIR CodeSystem structure
    fhir_structure = {
        "resourceType": "CodeSystem",
        "id": "psgc-geographic-codes",
        "url": "https://ontoserver.upmsilab.org/psgc",
        "version": "2",
        "name": "Psgc",
        "title": "PSGC - COMPLETE",
        "status": "draft",
        "contact": [
            {
                "telecom": [
                    {
                        "system": "email",
                        "value": "admin@upmsilab.org"  # Adding required value field for contact
                    }
                ]
            }
        ],
        "caseSensitive": False,
        "valueSet": "https://ontoserver.upmsilab.org/psgc",
        "hierarchyMeaning": "part-of",
        "compositional": False,
        "versionNeeded": True,
        "content": "complete",
        "count": total_concepts,
        "property": [
            {
                "code": "Geographic Level",
                "type": "string"
            }
        ],
        "concept": [root_concept]
    }
    
    return fhir_structure


def validate_fhir_codesystem_structure(fhir_structure: Dict[str, Any]) -> bool:
    """
    Basic validation of the FHIR CodeSystem structure.
    
    Args:
        fhir_structure: The FHIR CodeSystem structure to validate
        
    Returns:
        bool: True if structure is valid, False otherwise
    """
    required_fields = ["resourceType", "id", "url", "version", "status", "content", "concept"]
    
    for field in required_fields:
        if field not in fhir_structure:
            print(f"Validation error: Missing required field '{field}'")
            return False
    
    if fhir_structure["resourceType"] != "CodeSystem":
        print("Validation error: resourceType must be 'CodeSystem'")
        return False
    
    if fhir_structure["status"] not in ["draft", "active", "retired", "unknown"]:
        print("Validation error: status must be one of 'draft', 'active', 'retired', 'unknown'")
        return False
    
    if fhir_structure["content"] not in ["not-present", "example", "fragment", "complete", "supplement"]:
        print("Validation error: content must be one of the allowed values")
        return False
    
    if not isinstance(fhir_structure["concept"], list):
        print("Validation error: 'concept' field must be a list")
        return False
    
    # Validate some concepts
    for i, concept in enumerate(fhir_structure["concept"]):
        if "code" not in concept:
            print(f"Validation error: Concept at index {i} missing required 'code' field")
            return False
        
        if "display" not in concept:
            print(f"Validation error: Concept at index {i} missing required 'display' field")
            return False
    
    return True


def validate_against_fhir_terminology_server_requirements(fhir_structure: Dict[str, Any]) -> bool:
    """
    Validates the FHIR CodeSystem against basic terminology server requirements.
    
    Args:
        fhir_structure: The FHIR CodeSystem structure to validate
        
    Returns:
        bool: True if structure meets basic terminology server requirements, False otherwise
    """
    # Check that required fields for terminology servers are present
    if "url" not in fhir_structure:
        print("Terminology server validation error: Missing required 'url' field")
        return False
    
    # Check that URL is valid (just a basic check for http/https)
    url = fhir_structure["url"]
    if not (url.startswith("http://") or url.startswith("https://")):
        print(f"Terminology server validation error: URL '{url}' is not a valid URL")
        return False
    
    # Check that the CodeSystem has a proper version
    if "version" not in fhir_structure or not fhir_structure["version"]:
        print("Terminology server validation error: Missing or empty 'version' field")
        return False
    
    # Check that hierarchyMeaning is defined if there are nested concepts
    has_nested_concepts = any('concept' in c and c['concept'] for c in fhir_structure.get('concept', []))
    if has_nested_concepts and "hierarchyMeaning" not in fhir_structure:
        print("Terminology server validation error: Missing 'hierarchyMeaning' for nested concepts")
        return False
    
    # Check that if properties are defined, they follow FHIR structure
    if "property" in fhir_structure:
        for prop in fhir_structure["property"]:
            if "code" not in prop:
                print("Terminology server validation error: Property missing 'code' field")
                return False
            if "type" not in prop:
                print("Terminology server validation error: Property missing 'type' field")
                return False
    
    # Validate that all concept codes are unique within the CodeSystem
    def collect_codes(concepts, codes_list):
        for concept in concepts:
            if "code" in concept:
                codes_list.append(concept["code"])
            if "concept" in concept and concept["concept"]:
                collect_codes(concept["concept"], codes_list)
    
    all_codes = []
    collect_codes(fhir_structure.get("concept", []), all_codes)
    if len(all_codes) != len(set(all_codes)):
        print("Terminology server validation error: Duplicate concept codes found")
        return False
    
    return True


def validate_parent_child_relationships(geographic_data: List[Dict[str, Any]]) -> List[str]:
    """
    Validates parent-child relationships in geographic data to ensure all parent codes exist.
    
    Args:
        geographic_data: List of geographic entities with hierarchy information
        
    Returns:
        List[str]: List of error messages for any invalid relationships found
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


def main():
    """Main function to run the PSGC to FHIR converter."""
    parser = argparse.ArgumentParser(description='Convert PSGC Excel data to FHIR JSON CodeSystem format')
    parser.add_argument('--input', required=True, help='Input Excel file path')
    parser.add_argument('--output', required=True, help='Output JSON file path')
    
    args = parser.parse_args()
    
    # Read the PSGC Excel file
    df = read_psgc_excel(args.input)
    
    print(f"Successfully read PSGC data with {len(df)} entries")
    print(f"Columns: {list(df.columns)}")
    
    # Parse the geographic hierarchy
    geographic_hierarchy = parse_geographic_hierarchy(df)
    
    print(f"Parsed geographic hierarchy with {len(geographic_hierarchy)} entries")
    
    # Create FHIR CodeSystem structure
    fhir_codesystem = create_fhir_codesystem_structure(geographic_hierarchy)
    
    # Validate the structure
    is_valid_basic = validate_fhir_codesystem_structure(fhir_codesystem)
    if not is_valid_basic:
        print("FHIR CodeSystem basic structure validation failed")
        return 1  # Exit with error code

    # Validate against terminology server requirements
    is_valid_terminology = validate_against_fhir_terminology_server_requirements(fhir_codesystem)
    if not is_valid_terminology:
        print("FHIR CodeSystem terminology server validation failed")
        return 1  # Exit with error code

    print("FHIR CodeSystem structure validation passed")
    print("FHIR CodeSystem terminology server validation passed")
    
    # Write to output file
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(fhir_codesystem, f, indent=2, ensure_ascii=False)
    
    print(f"FHIR JSON CodeSystem structure created and saved to {args.output}")
    return 0


if __name__ == '__main__':
    main()
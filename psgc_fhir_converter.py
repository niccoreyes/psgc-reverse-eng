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
    Determine the parent PSGC code based on the geographic level.
    Based on the understanding that PSGC code structure is:
    - Digits 1-2: Region code
    - Digits 3-5: Province/City code  
    - Digits 6-8: Municipality/City code within Province
    - Digits 9-10: Barangay number within Municipality/City
    
    Geographic hierarchy:
    - Reg (Region): No parent or part of the national level
    - Prov (Province): Part of a Region
    - City/Mun (City/Municipality): Part of a Province or Region (for highly urbanized cities)
    - Bgy (Barangay): Part of a City/Municipality
    - SubMun (Sub-Municipality): Part of a City/Municipality
    
    Args:
        psgc_code (str): The 10-digit PSGC code
        level (str): Geographic level (Reg, Prov, City, Mun, Bgy, SubMun)
        
    Returns:
        Optional[str]: The parent PSGC code or None if no parent
    """
    # Work with original string without zero-padding first, then pad to 10 digits if needed
    code_original = str(psgc_code).strip()
    code = code_original.zfill(10)  # Ensure 10-digit format with leading zeros if needed
    
    if level == 'Reg':
        # Regions are top-level (no parent)
        return None
    elif level == 'Prov':
        # Provinces are part of regions - first 2 digits identify the region
        region_code = code[:2] + '00000000'
        region_numeric = str(int(region_code))
        return region_numeric if region_numeric != code_original else None
    elif level in ['City', 'Mun']:  # City or Municipality
        # Cities and municipalities are part of provinces
        # The parent is identified by first 5 digits + '00000'
        province_code = code[:5] + '00000'
        province_numeric = str(int(province_code))
        
        # If the province code matches the current code, this entity might be directly under region
        # (e.g. in the case of NCR or other special administrative regions)
        if province_code == code:
            # Get parent from region part (first 2 digits + zeros)
            region_code = code[:2] + '00000000'
            region_numeric = str(int(region_code))
            return region_numeric if region_numeric != code_original else None
        else:
            return province_numeric
    elif level == 'Bgy':  # Barangay
        # Barangays belong to municipalities/cities
        # Multiple patterns may exist in the dataset:
        # 1. In municipalities under provinces: RRPPLLLLCC with parent RRPPLLLL00 (last 2 digits)
        # 2. In municipalities under provinces: RRPPLLLCCC with parent RRPPLLL000 (last 3 digits) 
        # 3. In cities under regions: RRP0LLLCC with parent RRP000000 (last 5 digits)
        
        # Try each pattern in order of likelihood
        patterns_to_try = [
            lambda c: c[:8] + '00',  # Zero last 2 digits
            lambda c: c[:7] + '000', # Zero last 3 digits
            lambda c: c[:5] + '00000' # Zero last 5 digits
        ]
        
        for pattern_func in patterns_to_try:
            parent_code = pattern_func(code)
            if parent_code != code:
                # Convert back to numeric form without leading zeros
                parent_numeric = str(int(parent_code))
                return parent_numeric
        
        # If none of the patterns gave a different result
        return None
    elif level == 'SubMun':  # SubMunicipality
        # SubMunicipalities belong to municipalities/cities
        # The parent is identified by first 5 digits + '00000' (same level as the city/mun it's part of)
        city_mun_code = code[:5] + '00000'
        if city_mun_code != code:
            # Convert back to numeric form without leading zeros
            parent_numeric = str(int(city_mun_code))
            return parent_numeric
        else:
            return None
    else:
        # For other levels or unknown types
        return None


def parse_geographic_hierarchy(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Parse the geographic hierarchy from the PSGC data.
    
    Args:
        df (pd.DataFrame): DataFrame with PSGC data
        
    Returns:
        List[Dict[str, Any]]: List of geographic entities with hierarchy information
    """
    geographic_data = []
    
    for _, row in df.iterrows():
        psgc_code = str(row['10-digit PSGC']).strip()
        name = row['Name']
        level = row['Geographic Level']
        parent_code = get_parent_code(psgc_code, level)
        
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
    Build a hierarchical tree structure from geographic data.
    
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
            # Add this entity as a child to its parent
            geo_map[parent_code]['children'].append(entity)
        else:
            # This is a root level entity
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
    properties.append({
        "code": "Geographic Level",
        "valueString": entity['level']
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
    # Build the hierarchy tree
    hierarchy_tree = build_hierarchy_tree(geographic_data)
    
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
                        "system": "email"
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
        "count": len(geographic_data),
        "property": [
            {
                "code": "Geographic Level",
                "type": "string"
            }
        ],
        "concept": []
    }
    
    # Convert the hierarchy tree to FHIR concepts
    for root_entity in hierarchy_tree:
        fhir_concept = convert_entity_to_fhir_concept(root_entity, include_children=True)
        fhir_structure["concept"].append(fhir_concept)
    
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
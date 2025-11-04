#!/usr/bin/env python3
"""
Script to fix NaN values in the psgc_fhir_output.json file.
This addresses the issue where Geographic Level properties have NaN values
instead of proper string values, causing FHIR server validation to fail.
"""

import json
import math
import re

def fix_nan_in_fhir_structure(obj):
    """
    Recursively fix NaN values in FHIR structure, especially for Geographic Level properties.
    """
    if isinstance(obj, dict):
        fixed = {}
        for key, value in obj.items():
            fixed[key] = fix_nan_in_fhir_structure(value)
        
        # Special handling for property objects with Geographic Level
        if key == "property" and isinstance(value, list):
            for prop in fixed[key]:
                if (prop.get("code") == "Geographic Level" and 
                    (prop.get("valueString") is None or 
                     (isinstance(prop.get("valueString"), float) and 
                      math.isnan(prop["valueString"])))):
                    # Set to a default value like 'Unknown' or 'City' for known codes
                    # For 990100000 and 1999900000, we can provide specific defaults
                    code_val = obj.get('code', '')
                    if code_val == "990100000":
                        prop["valueString"] = "City"  # City of Isabela (Not a Province)
                    elif code_val == "1999900000":
                        prop["valueString"] = "Prov"  # Probably a province-level code
                    else:
                        prop["valueString"] = "Unknown"
        return fixed
    elif isinstance(obj, list):
        return [fix_nan_in_fhir_structure(item) for item in obj]
    elif isinstance(obj, float) and math.isnan(obj):
        return "Unknown"  # Replace all NaN with "Unknown" as a safe default
    else:
        return obj

def main():
    # Read the existing JSON file
    with open('psgc_fhir_output.json', 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix the literal NaN values in JSON (not valid JSON)
    # This handles the case where the JSON file literally contains "NaN" which is invalid
    content_with_fixed_nans = re.sub(r'\bNaN\b', '"NaN_PLACEHOLDER"', content)
    
    # Now parse the JSON with the placeholder
    try:
        data = json.loads(content_with_fixed_nans)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return 1
    
    # Replace the placeholder with a proper value
    def replace_nan_placeholders(obj):
        if isinstance(obj, dict):
            return {k: replace_nan_placeholders(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [replace_nan_placeholders(item) for item in obj]
        elif obj == "NaN_PLACEHOLDER":
            return "Unknown"
        else:
            return obj
    
    fixed_data = replace_nan_placeholders(data)
    
    # Apply additional fixes for Geographic Level specifically
    fixed_data = fix_nan_in_fhir_structure(fixed_data)
    
    # Write the fixed JSON back to the file
    with open('psgc_fhir_output.json', 'w', encoding='utf-8') as f:
        json.dump(fixed_data, f, indent=2, ensure_ascii=False)
    
    print("Successfully fixed NaN values in the FHIR output file.")
    print("The file should now be suitable for upload to the FHIR server.")

if __name__ == "__main__":
    main()
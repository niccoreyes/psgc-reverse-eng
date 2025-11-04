#!/usr/bin/env python3
"""
More targeted script to fix the specific NaN values in Geographic Level properties.
"""

import json
import re

def main():
    # Read the existing JSON file as text
    with open('psgc_fhir_output.json', 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"Original file character count: {len(content)}")
    
    # Find all occurrences of Geographic Level with NaN values
    print("Looking for Geographic Level properties with NaN values...")
    
    # Use regex to find "Geographic Level" with NaN valueString
    pattern = r'("code":\s*"Geographic Level".*?"valueString":\s*)NaN'
    matches = re.findall(pattern, content)
    print(f"Found {len(matches)} instances to fix")
    
    # Replace all "valueString": NaN with "valueString": "Unknown"
    # This pattern looks for the specific property pattern
    fixed_content = re.sub(pattern, r'\1"Unknown"', content)
    
    # Also handle other potential similar patterns
    # Find NaN values for codes that we know are problematic
    fixed_content = re.sub(r'("code":\s*"990100000".*?"valueString":\s*)NaN', r'\1"City"', fixed_content, flags=re.DOTALL)
    fixed_content = re.sub(r'("code":\s*"1999900000".*?"valueString":\s*)NaN', r'\1"Prov"', fixed_content, flags=re.DOTALL)
    
    print(f"Fixed file character count: {len(fixed_content)}")
    
    # Write the fixed content back
    with open('psgc_fhir_output.json', 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print("File has been updated, now checking for remaining NaN values...")
    
    # Check if there are still any literal NaN values in the file
    remaining_nan_count = len(re.findall(r'\bNaN\b', fixed_content))
    if remaining_nan_count > 0:
        print(f"Warning: {remaining_nan_count} literal 'NaN' values still exist in the file.")
        # Let's see them
        lines_with_nan = []
        for i, line in enumerate(fixed_content.split('\n')):
            if 'NaN' in line:
                lines_with_nan.append((i+1, line.strip()))
                if len(lines_with_nan) > 5:  # Limit output
                    break
        for line_num, line in lines_with_nan:
            print(f"Line {line_num}: {line}")
    else:
        print("No literal 'NaN' values found in the file.")
    
    # Try to validate the JSON structure
    print("Validating JSON structure...")
    try:
        with open('psgc_fhir_output.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        print("JSON validation successful!")
        
        # Now let's specifically check the problematic codes
        def check_concept(code_to_check, expected_level=None):
            def find_concept(concepts, target_code):
                for concept in concepts:
                    if concept.get('code') == target_code:
                        return concept
                    if 'concept' in concept:
                        result = find_concept(concept['concept'], target_code)
                        if result:
                            return result
                return None
            
            target_concept = find_concept(data.get('concept', []), code_to_check)
            if target_concept:
                properties = target_concept.get('property', [])
                for prop in properties:
                    if prop.get('code') == 'Geographic Level':
                        value = prop.get('valueString', 'NOT_FOUND')
                        print(f"Concept {code_to_check} has Geographic Level: {value}")
                        if expected_level and value == expected_level:
                            print(f"  ✓ Correctly set to expected value: {expected_level}")
                        elif value == 'Unknown':
                            print(f"  ⚠ Set to 'Unknown', might need correction")
                        break
                else:
                    print(f"Concept {code_to_check} has no Geographic Level property")
            else:
                print(f"Concept {code_to_check} not found in data")
                
        check_concept("990100000", "City")
        check_concept("1999900000", "Prov")
        
    except json.JSONDecodeError as e:
        print(f"JSON is still invalid: {e}")

if __name__ == "__main__":
    main()
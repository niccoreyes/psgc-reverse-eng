#!/usr/bin/env python3
"""
Quick script to fix the literal NaN in the JSON file.
"""

import json
import re

def main():
    # Read the existing JSON file as text
    with open('psgc_fhir_output.json', 'r', encoding='utf-8') as f:
        content = f.read()

    print("Replacing literal 'NaN' values with '\"Unknown\"'...")

    # Replace literal NaN with "Unknown" string (properly quoted for JSON)
    # Be careful to not replace "NaN" inside other strings
    # This regex looks for "NaN" that are values, not part of other strings
    fixed_content = re.sub(r':\s*NaN([,\}\]])', r': "Unknown"\1', content)
    
    # Handle NaN that might be at the end of the file or before commas/brackets
    fixed_content = re.sub(r'NaN([,\}\]])', r'"Unknown"\1', fixed_content)
    
    print("Checking if fix was applied...")
    
    # Write the fixed content back
    with open('psgc_fhir_output.json', 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    # Verify the fix by checking if there are still NaN in the file
    if 'NaN' in fixed_content:
        print("Warning: Some NaN values may still exist.")
    else:
        print("Successfully fixed literal NaN values in the FHIR output file.")
    
    print("Verifying that the file is valid JSON...")
    try:
        with open('psgc_fhir_output.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        print("JSON is valid and ready for upload.")
    except json.JSONDecodeError as e:
        print(f"Error: The JSON is still invalid: {e}")

if __name__ == "__main__":
    main()
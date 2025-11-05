#!/usr/bin/env python3
"""
Script to analyze PSGC Excel file codes and cross-reference with validation report
"""

import pandas as pd
import json

def main():
    # Read the Excel file
    df = pd.read_excel("PSGC-3Q-2025-Publication-Datafile.xlsx", sheet_name='PSGC')
    
    print(f"Total entries in Excel file: {len(df)}")
    
    # Get the 10-digit PSGC codes
    psgc_codes = set(df['10-digit PSGC'].astype(str).str.zfill(10))
    
    print(f"Unique PSGC codes in Excel: {len(psgc_codes)}")
    
    # Load the JSON output
    with open('psgc_fhir_output.json', 'r') as f:
        fhir_data = json.load(f)
    
    # Extract all codes from the FHIR output
    def extract_codes(concepts, codes_set):
        for concept in concepts:
            if 'code' in concept:
                codes_set.add(concept['code'])
            if 'concept' in concept:
                extract_codes(concept['concept'], codes_set)
    
    fhir_codes = set()
    extract_codes(fhir_data['concept'], fhir_codes)
    
    print(f"Total codes in FHIR output: {len(fhir_codes)}")
    
    # From the validation report:
    # Total codes in FHIR codesystem: 43785
    # Total codes in PSGC output: 43651
    # Common codes: 41761
    # Codes unique to FHIR: 2024
    # Codes unique to PSGC: 1890
    
    print("\nValidation Report Summary:")
    print("Total codes in FHIR codesystem (old): 43,785")
    print("Total codes in PSGC output: 43,651")
    print("Common codes: 41,761")
    print("Codes unique to FHIR (old): 2,024")
    print("Codes unique to PSGC: 1,890")
    
    print(f"\nActual data:")
    print(f"Codes in Excel (source): {len(psgc_codes)}")
    print(f"Codes in FHIR output: {len(fhir_codes)}")
    
    # Compare Excel codes with FHIR output codes
    missing_in_output = psgc_codes - fhir_codes
    extra_in_output = fhir_codes - psgc_codes
    
    print(f"\nComparison between Excel (source) and FHIR output:")
    print(f"Codes in Excel but missing from FHIR output: {len(missing_in_output)}")
    print(f"Codes in FHIR output but not in Excel: {len(extra_in_output)}")
    
    if missing_in_output:
        print(f"\nSample of codes in Excel but missing from FHIR output:")
        for i, code in enumerate(list(missing_in_output)[:10]):
            row = df[df['10-digit PSGC'].astype(str).str.zfill(10) == code]
            if not row.empty:
                name = row.iloc[0]['Name']
                level = row.iloc[0]['Geographic Level']
                print(f"  {code} - {name} - {level}")
    
    # Also look at the specific code with level difference mentioned in validation report
    if '0402104000' in psgc_codes:
        row = df[df['10-digit PSGC'].astype(str).str.zfill(10) == '0402104000']
        if not row.empty:
            name = row.iloc[0]['Name']
            level = row.iloc[0]['Geographic Level']
            print(f"\nSpecific code from validation report:")
            print(f"  0402104000: {name} - Level in Excel: {level} (FHIR shows=Mun, PSGC shows=City)")

if __name__ == "__main__":
    main()
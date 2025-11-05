#!/usr/bin/env python3
"""
Script to check the PSGC Excel file for code count and comparison with validation report
"""

import pandas as pd

def main():
    # Read the Excel file
    df = pd.read_excel("PSGC-3Q-2025-Publication-Datafile.xlsx", sheet_name='PSGC')
    
    print(f"Total entries in Excel file: {len(df)}")
    
    # Get the 10-digit PSGC codes
    psgc_codes = df['10-digit PSGC'].astype(str).str.zfill(10)
    
    print(f"Total PSGC codes in Excel: {len(psgc_codes)}")
    print(f"Unique PSGC codes in Excel: {len(set(psgc_codes))}")
    
    # Show a few sample codes
    print("\nSample codes from Excel:")
    for i, code in enumerate(psgc_codes[:10]):
        name = df.iloc[i]['Name']
        level = df.iloc[i]['Geographic Level']
        print(f"  {code} - {name} - {level}")

if __name__ == "__main__":
    main()
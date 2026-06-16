#!/usr/bin/env python3
"""
Script to analyze the geographic hierarchy and identify why entities are being excluded
"""

import sys
import json

def analyze_hierarchy():
    print("Analyzing the psgc_fhir_output.json file to understand the structure...")
    
    with open('psgc_fhir_output.json', 'r') as f:
        data = json.load(f)

    def count_all_codes_with_details(concept, level=0):
        count = 1
        level_counts = {level: 1}
        level_codes = {level: [concept.get('code')]}
        
        if 'concept' in concept and concept['concept']:
            for child in concept['concept']:
                child_count, child_level_counts, child_level_codes = count_all_codes_with_details(child, level + 1)
                count += child_count
                
                # Merge level counts
                for l, c in child_level_counts.items():
                    level_counts[l] = level_counts.get(l, 0) + c
                
                # Merge level codes
                for l, codes in child_level_codes.items():
                    if l not in level_codes:
                        level_codes[l] = []
                    level_codes[l].extend(codes)
        
        return count, level_counts, level_codes

    total_count = 0
    all_level_counts = {}
    all_level_codes = {}
    
    for concept in data.get('concept', []):
        count, level_counts, level_codes = count_all_codes_with_details(concept)
        total_count += count
        
        # Merge level counts
        for level, c in level_counts.items():
            all_level_counts[level] = all_level_counts.get(level, 0) + c
        
        # Merge level codes
        for level, codes in level_codes.items():
            if level not in all_level_codes:
                all_level_codes[level] = []
            all_level_codes[level].extend(codes)

    print(f"Total concepts in hierarchy: {total_count}")
    print("Concepts by level:")
    for level in sorted(all_level_counts.keys()):
        print(f"  Level {level}: {all_level_counts[level]} concepts")
    
    print(f"\nRoot concept: {data['concept'][0]['code']} - {data['concept'][0]['display']}")
    print(f"Root children (level 1): {len(data['concept'][0].get('concept', []))}")
    
    if data['concept'][0].get('concept'):
        print("\nFirst few level 1 concepts:")
        for i, concept in enumerate(data['concept'][0]['concept'][:5]):
            print(f"  {i+1}. {concept['code']} - {concept['display']}")
            if concept.get('concept'):
                print(f"     First child: {concept['concept'][0]['code']} - {concept['concept'][0]['display']}")
                
    print(f"\nExpected total from original data: 43,769 + 1 (root) = 43,770")
    print(f"Actual total in hierarchy: {total_count}")
    print(f"Missing: {43770 - total_count} concepts")


if __name__ == "__main__":
    analyze_hierarchy()
# OpenSpec Proposal: Fix PSGC Hierarchy Structure

## 1. Problem Statement

The current PSGC to FHIR converter has geographic hierarchy structure issues that don't follow the actual PSGC code format. While most of the parent-child relationships have been fixed as part of the 'fix-parent-child-relationships' change, there are still some specific cases that need correction:

- The root concept is properly set as "Philippine Standard Geographic Code" (0000000000)
- Most parent-child relationships now follow the PSGC code structure
- However, some specific cases like Pateros are still incorrectly placed under an intermediate code instead of directly under NCR
- Pateros (1381701000) is currently treated as a municipality with parent 1381700000, but it should be directly under NCR (1300000000) like other cities in the National Capital Region

## 2. PSGC Code Structure

The correct PSGC code structure is:
- **Region Code**: First 2 digits (positions 1–2)
- **Province Code**: Next 3 digits (positions 3–5)  
- **Municipality Code**: Next 2 digits (positions 6–7)
- **Barangay Code**: Last 3 digits (positions 8–10)

## 3. Current Status and Implementation

Most of the parent-child relationship issues have been addressed through the 'fix-parent-child-relationships' change as documented in PARENT_CHILD_FIX_SUMMARY.md. This includes:
- PSGC code normalization to 10 digits with leading zeros
- Proper handling of 3-level hierarchies for cities with districts (like Manila)
- Correct parent-child relationships for regions and provinces

However, there are still issues with special cases in the National Capital Region (NCR) where certain municipalities/cities are incorrectly classified, affecting their parent relationships.

## 4. Remaining Issues

- Pateros (1381701000) is incorrectly classified as a municipality with parent "1381700000" instead of being directly under NCR (1300000000)
- In NCR, Pateros should be treated similarly to other cities directly subordinate to the region, not as a municipality within a province
- This suggests the data may have Pateros classified as "Mun" when it should be treated as "City" or equivalent for NCR context

## 5. Proposed Solution

### 5.1 Update get_parent_code function with NCR special handling

Modify the existing function to check for NCR-specific cases where certain municipalities should be treated as direct children of NCR:

```python
def get_parent_code(psgc_code: str, level: str) -> Optional[str]:
    """
    Determine the parent PSGC code based on the PSGC structure:
    - Positions 1-2: Region code
    - Positions 3-5: Province code
    - Positions 6-7: Municipality code
    - Positions 8-10: Barangay code
    
    Args:
        psgc_code (str): The 10-digit PSGC code
        level (str): Geographic level (Reg, Prov, City, Mun, Bgy)
        
    Returns:
        Optional[str]: The parent PSGC code or None if no parent
    """
    # Ensure code is 10 digits
    code = str(psgc_code).strip().zfill(10)
    
    if level == 'Reg':
        # Regions are at the top level under the root Philippine entity
        return '0000000000'  # Root Philippine Standard Geographic Code
    elif level == 'Prov':
        # Provinces belong to regions (first 2 digits + zeros)
        return code[:2].ljust(10, '0')
    elif level in ['City', 'Mun']:  # City or Municipality
        # Cities/Municipalities belong to provinces (first 5 digits + zeros)
        province_code = code[:5].ljust(10, '0')
        region_code = code[:2].ljust(10, '0')
        
        # SPECIAL CASE: In NCR, some municipalities should be treated as cities directly under NCR
        # Pateros (1381701000) should be directly under NCR (1300000000) 
        # rather than under a province-level code (1381700000)
        if code.startswith('13') and code[2:5] == '817':  # Pateros-specific case
            return region_code  # Return NCR as parent
        
        # If the province code is the same as the current code, this is a highly urbanized city
        # that belongs directly to the region, not to a province
        if province_code == code:
            return region_code
        else:
            return province_code
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
        # For other levels or unknown types
        return None
```

### 5.2 Update Hierarchy Structure

The hierarchy should maintain the pattern where special cases in NCR (like Pateros) are directly connected to NCR:
- Root: "0000000000" - Philippine Standard Geographic Code
- Level 1: Regions (e.g., "1300000000" - National Capital Region)
- Level 2: Provinces/Municipalities directly under NCR (e.g., "1381701000" - Pateros directly under "1300000000")
- Level 3: Barangays under their respective municipalities/cities

## 6. Implementation Plan

**Task 1**: Update `get_parent_code` function to handle NCR special cases like Pateros
**Task 2**: Add more comprehensive NCR-specific handling if other similar cases exist
**Task 3**: Test the updated hierarchy implementation with sample data
**Task 4**: Verify that Pateros and similar NCR cases now have correct parent-child relationships
**Task 5**: Validate with FHIR terminology server requirements

## 7. Validation

- Verify that Pateros (1381701000) now has NCR (1300000000) as its parent
- Ensure all other parent codes still exist in the dataset
- Ensure the hierarchy follows the correct structure for NCR special cases
- Test with the complete PSGC dataset
- Validate with FHIR terminology server requirements

## 8. Expected Outcomes

- Correct geographic hierarchy representation for NCR special cases
- Pateros and similar cases will have valid parent relationships according to proper geographic structure
- All parent-child relationships will be valid
- FHIR CodeSystem that meets server validation requirements
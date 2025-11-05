# OpenSpec Proposal: Fix PSGC Hierarchy Structure

## 1. Problem Statement

The current PSGC to FHIR converter has a flawed geographic hierarchy structure that doesn't follow the actual PSGC code format. Currently:

- The hierarchy doesn't follow the correct PSGC code structure
- The root concept should be "Philippine Standard Geographic Code" (0000000000)
- The hierarchy should follow: Root -> Regions -> Provinces -> Municipalities -> Barangays
- Current implementation doesn't correctly extract parent codes based on the official PSGC structure

## 2. PSGC Code Structure

The correct PSGC code structure is:
- **Region Code**: First 2 digits (positions 1–2)
- **Province Code**: Next 3 digits (positions 3–5)  
- **Municipality Code**: Next 2 digits (positions 6–7)
- **Barangay Code**: Last 3 digits (positions 8–10)

## 3. Current Issues

- The root concept is not properly set as "Philippine Standard Geographic Code"
- Parent-child relationships don't follow the actual code structure
- Current implementation has complex logic that doesn't properly map to PSGC structure

## 4. Proposed Solution

### 4.1 Update get_parent_code function

Replace the current complex implementation with a clean function that follows the PSGC structure:

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
    code = psgc_code.zfill(10)
    
    if level == 'Reg':
        # Regions are at the top level under the root Philippine entity
        return '0000000000'  # Root Philippine Standard Geographic Code
    elif level == 'Prov':
        # Provinces belong to regions (first 2 digits + zeros)
        return code[:2].ljust(10, '0')
    elif level in ['City', 'Mun']:  # City or Municipality
        # Cities/Municipalities belong to provinces (first 5 digits + zeros)
        return code[:5].ljust(10, '0')
    elif level == 'Bgy':  # Barangay
        # Barangays belong to municipalities/cities (first 7 digits + zeros)
        return code[:7].ljust(10, '0')
    else:
        # For other levels or unknown types
        return None
```

### 4.2 Update Hierarchy Structure

Modify the hierarchy to be:
- Root: "0000000000" - Philippine Standard Geographic Code
- Level 1: Regions (e.g., "1300000000" - National Capital Region)
- Level 2: Provinces (e.g., "1381700000" - Pateros)
- Level 3: Municipalities/Cities (e.g., "1381701000" - Pateros)
- Level 4: Barangays (e.g., "1381701001" - Aguho)

### 4.3 Update CodeSystem Creation

Ensure the FHIR CodeSystem starts with the root Philippine entity as the main concept with regions as its direct children.

## 5. Implementation Plan

**Task 1**: Update `get_parent_code` function to use the correct PSGC structure
**Task 2**: Ensure all regions have "0000000000" as their parent code
**Task 3**: Update the hierarchy construction to start with the root Philippine entity
**Task 4**: Test the new hierarchy implementation with sample data
**Task 5**: Verify that all parent-child relationships are valid

## 6. Validation

- Verify all parent codes exist in the dataset
- Ensure the hierarchy follows the correct structure
- Test with the complete PSGC dataset
- Validate with FHIR terminology server requirements

## 7. Expected Outcomes

- Correct geographic hierarchy representation
- All parent-child relationships will be valid according to PSGC structure
- Root concept properly set to "Philippine Standard Geographic Code"
- FHIR CodeSystem that meets server validation requirements
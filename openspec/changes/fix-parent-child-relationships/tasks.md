## 1. Analysis and Research
- [ ] 1.1 Identify all concepts that have invalid parent references in the dataset
- [ ] 1.2 Analyze the `get_parent_code` function to understand how parent codes are calculated
- [ ] 1.3 Determine the root cause of parent codes that don't exist in dataset

## 2. Implementation
- [ ] 2.1 Update `get_parent_code` function to validate parent codes exist in the dataset
- [ ] 2.2 Modify the parent code assignment logic to handle missing parents appropriately
- [ ] 2.3 Add a validation function to check parent-child relationships before creating hierarchy
- [ ] 2.4 Update the hierarchy building logic to handle missing parent codes gracefully

## 3. Validation and Testing
- [ ] 3.1 Test the fix with the existing dataset to ensure no more parent validation errors
- [ ] 3.2 Verify that the geographic hierarchy is still properly maintained
- [ ] 3.3 Run full conversion process to check for any regressions
- [ ] 3.4 Test upload to FHIR server to confirm the fix resolves the issue

## 4. Documentation and Cleanup
- [ ] 4.1 Document the changes made to the parent-child relationship logic
- [ ] 4.2 Add comments to explain the validation approach
- [ ] 4.3 Verify all changes are properly implemented
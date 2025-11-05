import unittest
import tempfile
import json
import pandas as pd
import math
from io import StringIO
from psgc_fhir_converter import (
    get_parent_code,
    parse_geographic_hierarchy,
    create_fhir_codesystem_structure,
    validate_fhir_codesystem_structure
)

# Import the handle_nan_in_data function from the upload scripts
def handle_nan_in_data(obj):
    """
    Recursively handle NaN values in data structures, converting them to None.
    
    Args:
        obj: The data structure to process (dict, list, or primitive)
        
    Returns:
        Processed data structure with NaN values replaced by None
    """
    if isinstance(obj, dict):
        return {key: handle_nan_in_data(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [handle_nan_in_data(item) for item in obj]
    elif isinstance(obj, float) and math.isnan(obj):
        return None
    else:
        return obj


class TestPSGCFHIRConverter(unittest.TestCase):
    
    def setUp(self):
        """Set up test data."""
        # Create a small sample of PSGC data for testing
        self.sample_data = pd.DataFrame({
            '10-digit PSGC': ['1300000000', '1380100000', '1380100001'],
            'Name': ['National Capital Region (NCR)', 'City of Caloocan', 'Barangay 1'],
            'Geographic Level': ['Reg', 'City', 'Bgy'],
            'Old names': ['', '', ''],
            'City Class': ['', '', ''],
            'Income\nClassification (DOF DO No. 074.2024)': ['', '', ''],
            'Urban / Rural\n(based on 2020 CPH)': ['', '', ''],
            '2024 Population': [None, None, None],
            'Unnamed: 9': [None, None, None],
            'Status': [None, None, None]
        })
    
    def test_get_parent_code(self):
        """Test the parent code determination function."""
        # Test region (no parent)
        self.assertIsNone(get_parent_code('1300000000', 'Reg'))
        
        # Test city (parent is region)
        self.assertEqual(get_parent_code('1380100000', 'City'), '1300000000')
        
        # Test barangay (parent is city/mun)
        self.assertEqual(get_parent_code('1380100001', 'Bgy'), '1380100000')
        
        # Test province (parent is region)
        self.assertEqual(get_parent_code('1400100000', 'Prov'), '1400000000')
    
    def test_parse_geographic_hierarchy(self):
        """Test the geographic hierarchy parsing function."""
        result = parse_geographic_hierarchy(self.sample_data)
        
        self.assertEqual(len(result), 3)
        
        # Check first entry (region)
        self.assertEqual(result[0]['code'], '1300000000')
        self.assertEqual(result[0]['display'], 'National Capital Region (NCR)')
        self.assertEqual(result[0]['level'], 'Reg')
        self.assertIsNone(result[0]['parent_code'])
        
        # Check second entry (city)
        self.assertEqual(result[1]['code'], '1380100000')
        self.assertEqual(result[1]['display'], 'City of Caloocan')
        self.assertEqual(result[1]['level'], 'City')
        self.assertEqual(result[1]['parent_code'], '1300000000')
        
        # Check third entry (barangay)
        self.assertEqual(result[2]['code'], '1380100001')
        self.assertEqual(result[2]['display'], 'Barangay 1')
        self.assertEqual(result[2]['level'], 'Bgy')
        self.assertEqual(result[2]['parent_code'], '1380100000')
    
    def test_create_fhir_codesystem_structure(self):
        """Test the FHIR CodeSystem structure creation."""
        geographic_data = parse_geographic_hierarchy(self.sample_data)
        fhir_structure = create_fhir_codesystem_structure(geographic_data)
        
        # Check basic structure
        self.assertEqual(fhir_structure['resourceType'], 'CodeSystem')
        self.assertEqual(fhir_structure['id'], 'psgc-geographic-codes')
        # Count should be len(geographic_data) + 1 for the root concept
        self.assertEqual(fhir_structure['count'], len(geographic_data) + 1)
        
        # Check that there are concepts
        self.assertEqual(len(fhir_structure['concept']), 1)  # Should have 1 root concept (Philippine Standard Geographic Code)
        
        # Check the root concept is the Philippine Standard Geographic Code
        root_concept = fhir_structure['concept'][0]
        self.assertEqual(root_concept['code'], '0000000000')
        self.assertEqual(root_concept['display'], 'Philippine Standard Geographic Code')
        
        # The actual geographic entities should be children of the root concept
        self.assertIn('concept', root_concept)
        child_concepts = root_concept['concept']
        self.assertEqual(len(child_concepts), 1)  # Should contain the NCR region as a child
        
        # Check the first child concept (NCR region)
        region_concept = child_concepts[0]
        self.assertEqual(region_concept['code'], '1300000000')
        self.assertEqual(region_concept['display'], 'National Capital Region (NCR)')
        
        # Check it has children (Caloocan city)
        self.assertIn('concept', region_concept)
        city_concept = region_concept['concept'][0]
        self.assertEqual(city_concept['code'], '1380100000')
        self.assertEqual(city_concept['display'], 'City of Caloocan')
        
        # Check it has grandchildren (Barangay 1)
        self.assertIn('concept', city_concept)
        bgy_concept = city_concept['concept'][0]
        self.assertEqual(bgy_concept['code'], '1380100001')
        self.assertEqual(bgy_concept['display'], 'Barangay 1')
        
        # Check that geographic level property is present on geographic concepts (not on the root)
        for concept in [region_concept, city_concept, bgy_concept]:
            self.assertIn('property', concept)
            geo_level_prop = next(p for p in concept['property'] if p['code'] == 'Geographic Level')
            self.assertIsNotNone(geo_level_prop)
    
    def test_validate_fhir_codesystem_structure(self):
        """Test the FHIR CodeSystem validation function."""
        geographic_data = parse_geographic_hierarchy(self.sample_data)
        fhir_structure = create_fhir_codesystem_structure(geographic_data)
        
        # Valid structure should pass validation
        is_valid = validate_fhir_codesystem_structure(fhir_structure)
        self.assertTrue(is_valid)
        
        # Invalid structure should fail validation
        invalid_structure = {'resourceType': 'InvalidType', 'id': 'test'}
        is_valid = validate_fhir_codesystem_structure(invalid_structure)
        self.assertFalse(is_valid)
    
    def test_fhir_structure_properties(self):
        """Test that the FHIR structure has the required properties."""
        geographic_data = parse_geographic_hierarchy(self.sample_data)
        fhir_structure = create_fhir_codesystem_structure(geographic_data)
        
        # Check that the required properties are defined at the CodeSystem level
        self.assertIn('property', fhir_structure)
        properties = fhir_structure['property']
        
        # Should have Geographic Level property
        geo_level_prop = next((p for p in properties if p['code'] == 'Geographic Level'), None)
        self.assertIsNotNone(geo_level_prop)
        self.assertEqual(geo_level_prop['type'], 'string')
        
        # Note: Parent property is now defined at the concept level, not at the CodeSystem level
        # This is the correct implementation for the parent-child relationship fix
        
        # Check that the first concept is the root "Philippine Standard Geographic Code" which has no properties
        root_concept = fhir_structure['concept'][0]
        self.assertEqual(root_concept['code'], '0000000000')
        self.assertEqual(root_concept['display'], 'Philippine Standard Geographic Code')
        # This root concept should not have properties
        
        # Check that the child concepts (actual geographic entities) have properties
        geographic_concepts = root_concept['concept']  # The actual regions, cities, etc.
        self.assertGreater(len(geographic_concepts), 0)
        
        # The first geographic concept (Region) should not have a parent property
        region_concept = geographic_concepts[0]
        geo_level_prop = next((p for p in region_concept['property'] if p['code'] == 'Geographic Level'), None)
        self.assertIsNotNone(geo_level_prop)
        
        # The child concept (City) should have both geographic level and parent properties
        city_concept = region_concept['concept'][0]
        concept_properties = {prop['code']: prop for prop in city_concept['property']}
        
        self.assertIn('Geographic Level', concept_properties)
        self.assertIn('parent', concept_properties)
        self.assertEqual(concept_properties['parent']['valueCode'], '1300000000')  # Parent region code


class TestNaNHandling(unittest.TestCase):
    """Test class for NaN handling in FHIR data structures."""
    
    def test_handle_nan_in_data_with_nan_values(self):
        """Test that NaN values are properly converted to None."""
        import math
        
        # Create a test structure with NaN values
        test_data = {
            'field1': 1.0,
            'field2': float('nan'),
            'field3': [1.0, float('nan'), 3.0],
            'field4': {
                'nested_field1': float('nan'),
                'nested_field2': 'string_value',
                'nested_field3': [float('nan'), 2.0, float('inf')]
            }
        }
        
        # Process with our NaN handling function
        processed_data = handle_nan_in_data(test_data)
        
        # Check that top-level NaN was converted to None
        self.assertEqual(processed_data['field1'], 1.0)
        self.assertIsNone(processed_data['field2'])
        
        # Check that NaN in list was converted to None
        self.assertEqual(processed_data['field3'][0], 1.0)
        self.assertIsNone(processed_data['field3'][1])
        self.assertEqual(processed_data['field3'][2], 3.0)
        
        # Check nested structure
        self.assertIsNone(processed_data['field4']['nested_field1'])
        self.assertEqual(processed_data['field4']['nested_field2'], 'string_value')
        
        # Check list in nested structure
        self.assertIsNone(processed_data['field4']['nested_field3'][0])
        self.assertEqual(processed_data['field4']['nested_field3'][1], 2.0)
        # Note: infinity is not NaN, so it should remain unchanged
        self.assertEqual(processed_data['field4']['nested_field3'][2], float('inf'))
    
    def test_handle_nan_in_data_without_nan_values(self):
        """Test that the function preserves data without NaN values."""
        test_data = {
            'field1': 1.0,
            'field2': 'string_value',
            'field3': [1.0, 2.0, 3.0],
            'field4': {
                'nested_field1': 42.0,
                'nested_field2': 'nested_string',
                'nested_field3': [10.0, 20.0, 30.0]
            }
        }
        
        processed_data = handle_nan_in_data(test_data)
        
        # Check that all original values are preserved
        self.assertEqual(processed_data, test_data)
    
    def test_handle_nan_in_fhir_structure(self):
        """Test handling of NaN values in a FHIR-like structure."""
        import math
        
        # Create a FHIR CodeSystem structure with NaN values
        fhir_structure = {
            'resourceType': 'CodeSystem',
            'id': 'test-codesystem',
            'concept': [
                {
                    'code': 'A',
                    'display': 'Concept A',
                    'property': [
                        {'code': 'value', 'valueDecimal': float('nan')},
                        {'code': 'count', 'valueInteger': 10}
                    ]
                },
                {
                    'code': 'B',
                    'display': 'Concept B',
                    'property': [
                        {'code': 'value', 'valueDecimal': 5.5},
                        {'code': 'missing_value', 'valueDecimal': float('nan')}
                    ]
                }
            ]
        }
        
        processed_structure = handle_nan_in_data(fhir_structure)
        
        # Check that the basic structure is preserved
        self.assertEqual(processed_structure['resourceType'], 'CodeSystem')
        self.assertEqual(processed_structure['id'], 'test-codesystem')
        self.assertEqual(len(processed_structure['concept']), 2)
        
        # Check first concept
        concept_a = processed_structure['concept'][0]
        self.assertEqual(concept_a['code'], 'A')
        self.assertEqual(concept_a['display'], 'Concept A')
        
        # Check that NaN value was converted to None
        self.assertIsNone(concept_a['property'][0]['valueDecimal'])
        self.assertEqual(concept_a['property'][1]['valueInteger'], 10)
        
        # Check second concept
        concept_b = processed_structure['concept'][1]
        self.assertEqual(concept_b['code'], 'B')
        self.assertEqual(concept_b['display'], 'Concept B')
        
        # Check that valid value is preserved and NaN is converted to None
        self.assertEqual(concept_b['property'][0]['valueDecimal'], 5.5)
        self.assertIsNone(concept_b['property'][1]['valueDecimal'])


if __name__ == '__main__':
    unittest.main()
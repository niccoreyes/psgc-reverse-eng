import unittest
import tempfile
import json
import pandas as pd
from io import StringIO
from psgc_fhir_converter import (
    get_parent_code,
    parse_geographic_hierarchy,
    create_fhir_codesystem_structure,
    validate_fhir_codesystem_structure
)


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
        self.assertEqual(fhir_structure['count'], 3)
        
        # Check that there are concepts
        self.assertEqual(len(fhir_structure['concept']), 1)  # Should have 1 root concept with children
        
        # Check the root concept is the region
        root_concept = fhir_structure['concept'][0]
        self.assertEqual(root_concept['code'], '1300000000')
        self.assertEqual(root_concept['display'], 'National Capital Region (NCR)')
        
        # Check it has children
        self.assertIn('concept', root_concept)
        self.assertEqual(len(root_concept['concept']), 1)  # Caloocan city
        
        # Check the child concept
        city_concept = root_concept['concept'][0]
        self.assertEqual(city_concept['code'], '1380100000')
        self.assertEqual(city_concept['display'], 'City of Caloocan')
        
        # Check it has grandchildren
        self.assertIn('concept', city_concept)
        self.assertEqual(len(city_concept['concept']), 1)  # Barangay 1
        
        # Check the grandchild concept
        bgy_concept = city_concept['concept'][0]
        self.assertEqual(bgy_concept['code'], '1380100001')
        self.assertEqual(bgy_concept['display'], 'Barangay 1')
        
        # Check that geographic level property is present
        for concept in [root_concept, city_concept, bgy_concept]:
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
        
        # Check that the required properties are defined in the structure
        self.assertIn('property', fhir_structure)
        properties = fhir_structure['property']
        
        # Should have Geographic Level property
        geo_level_prop = next((p for p in properties if p['code'] == 'Geographic Level'), None)
        self.assertIsNotNone(geo_level_prop)
        self.assertEqual(geo_level_prop['type'], 'string')
        
        # Should have parent property
        parent_prop = next((p for p in properties if p['code'] == 'parent'), None)
        self.assertIsNotNone(parent_prop)
        self.assertEqual(parent_prop['type'], 'code')


if __name__ == '__main__':
    unittest.main()
#!/usr/bin/env python3
"""
Test Upload Script for PSGC FHIR CodeSystem

This script uploads the PSGC FHIR CodeSystem to the tx.fhirlab.net server
with a test ID for safe testing purposes.
"""

import json
import requests
import argparse
import os
import sys
import logging
from typing import Dict, Any, Optional
from psgc_fhir_converter import validate_fhir_codesystem_structure, validate_against_fhir_terminology_server_requirements


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_fhir_codesystem(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Load FHIR CodeSystem from a JSON file.
    
    Args:
        file_path (str): Path to the JSON file containing the FHIR CodeSystem
        
    Returns:
        Optional[Dict[str, Any]]: The loaded FHIR CodeSystem or None if failed
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return None
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in file: {file_path}")
        return None
    except Exception as e:
        logger.error(f"Error loading FHIR CodeSystem from {file_path}: {str(e)}")
        return None


def modify_codesystem_for_test(fhir_codesystem: Dict[str, Any], test_id: str) -> Dict[str, Any]:
    """
    Modify a FHIR CodeSystem to use a test ID and other test-specific values.
    
    Args:
        fhir_codesystem (Dict[str, Any]): Original FHIR CodeSystem
        test_id (str): Test ID to use for the CodeSystem
        
    Returns:
        Dict[str, Any]: Modified FHIR CodeSystem with test values
    """
    # Create a deep copy of the original codesystem
    test_codesystem = json.loads(json.dumps(fhir_codesystem))
    
    # Modify the ID to use the test ID
    test_codesystem['id'] = test_id
    
    # Modify the URL to indicate it's a test version
    if 'url' in test_codesystem:
        original_url = test_codesystem['url']
        test_codesystem['url'] = original_url + '-test'
    
    # Add a test-specific title
    if 'title' in test_codesystem:
        original_title = test_codesystem['title']
        test_codesystem['title'] = f"[TEST] {original_title}"
    
    # Update status to draft if not already
    test_codesystem['status'] = 'draft'
    
    return test_codesystem


def validate_fhir_for_upload(fhir_codesystem: Dict[str, Any]) -> bool:
    """
    Validate the FHIR CodeSystem before uploading.
    
    Args:
        fhir_codesystem (Dict[str, Any]): The FHIR CodeSystem to validate
        
    Returns:
        bool: True if valid for upload, False otherwise
    """
    logger.info("Validating FHIR CodeSystem structure...")
    
    # Basic FHIR CodeSystem validation
    basic_valid = validate_fhir_codesystem_structure(fhir_codesystem)
    if not basic_valid:
        logger.error("FHIR CodeSystem basic structure validation failed")
        return False
    
    # Terminology server requirements validation
    term_valid = validate_against_fhir_terminology_server_requirements(fhir_codesystem)
    if not term_valid:
        logger.error("FHIR CodeSystem terminology server validation failed")
        return False
    
    logger.info("FHIR CodeSystem validation passed")
    return True


def get_auth_headers() -> Dict[str, str]:
    """
    Get authentication headers for the FHIR server.
    
    Returns:
        Dict[str, str]: Authentication headers
    """
    api_key = os.getenv('FHIR_SERVER_API_KEY')
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    # Add authorization header only if API key is provided
    if api_key:
        headers['Authorization'] = f'Bearer {api_key}'
    
    return headers


def upload_codesystem_to_server(fhir_codesystem: Dict[str, Any], server_url: str) -> bool:
    """
    Upload the FHIR CodeSystem to the specified server.
    
    Args:
        fhir_codesystem (Dict[str, Any]): The FHIR CodeSystem to upload
        server_url (str): Base URL of the FHIR server
        
    Returns:
        bool: True if upload was successful, False otherwise
    """
    try:
        headers = get_auth_headers()
        
        # Construct the full URL for the upload
        upload_url = f"{server_url.rstrip('/')}/CodeSystem"
        
        # Make the POST request to create the resource
        response = requests.post(upload_url, json=fhir_codesystem, headers=headers, timeout=30)
        
        if response.status_code in [200, 201]:  # Success or created
            logger.info(f"Successfully uploaded CodeSystem with ID: {fhir_codesystem.get('id', 'unknown')}")
            logger.info(f"Response: {response.status_code}")
            return True
        else:
            logger.error(f"Upload failed with status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error during upload: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during upload: {str(e)}")
        return False


def main():
    """Main function to run the test upload script."""
    parser = argparse.ArgumentParser(description='Upload PSGC FHIR CodeSystem to server with test ID')
    parser.add_argument('--input', required=True, help='Input FHIR JSON file path')
    parser.add_argument('--server-url', required=True, help='FHIR server URL (e.g., https://tx.fhirlab.net/fhir)')
    parser.add_argument('--test-id', default='test-psgc-geographic-codes', 
                       help='Test ID to use for the CodeSystem (default: test-psgc-geographic-codes)')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Perform a dry run without actually uploading')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Load the FHIR CodeSystem from file
    fhir_codesystem = load_fhir_codesystem(args.input)
    if not fhir_codesystem:
        logger.error("Failed to load FHIR CodeSystem from file")
        sys.exit(1)
    
    # Modify the CodeSystem for test purposes
    logger.info(f"Modifying CodeSystem for test with ID: {args.test_id}")
    test_codesystem = modify_codesystem_for_test(fhir_codesystem, args.test_id)
    
    # Validate the modified CodeSystem
    if not validate_fhir_for_upload(test_codesystem):
        logger.error("Modified CodeSystem failed validation")
        sys.exit(1)
    
    if args.dry_run:
        logger.info("Dry run mode: Skipping actual upload")
        logger.info(f"Would upload CodeSystem with ID: {test_codesystem['id']}")
        logger.info(f"Server URL: {args.server_url}")
        return 0
    else:
        # Upload the test CodeSystem to the server
        logger.info(f"Uploading test CodeSystem to: {args.server_url}")
        success = upload_codesystem_to_server(test_codesystem, args.server_url)
        
        if success:
            logger.info("Test upload completed successfully")
            return 0
        else:
            logger.error("Test upload failed")
            sys.exit(1)


if __name__ == '__main__':
    main()
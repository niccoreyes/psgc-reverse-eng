#!/usr/bin/env python3
"""
Test script to validate the upload functionality with the mock FHIR server
"""

import subprocess
import time
import requests
import threading
import os
import sys
import json


def start_mock_server():
    """Start the mock FHIR server in a separate thread."""
    # Set environment variable for the API key
    os.environ['FHIR_SERVER_API_KEY'] = 'mock_key'
    
    # Start the mock server using subprocess
    server_process = subprocess.Popen([
        sys.executable, './mock_fhir_server.py'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Give the server a moment to start
    time.sleep(2)
    
    return server_process


def test_upload_scripts():
    """Test the upload scripts with the mock server."""
    
    print("Testing upload functionality with mock FHIR server...")
    
    # Test 1: Test upload script
    print("\n1. Testing test upload script...")
    try:
        result = subprocess.run([
            sys.executable, './upload_test_script.py',
            '--input', './test_codesystem.json',
            '--server-url', 'http://localhost:8000/fhir',
            '--test-id', 'test-psgc-codesystem-123',
            '--dry-run'  # First run with dry-run to make sure syntax is correct
        ], capture_output=True, text=True, timeout=30)
        
        print(f"Test upload dry-run return code: {result.returncode}")
        if result.stdout:
            print(f"STDOUT: {result.stdout}")
        if result.stderr:
            print(f"STDERR: {result.stderr}")
        
        # Now run without dry-run
        result = subprocess.run([
            sys.executable, './upload_test_script.py',
            '--input', './test_codesystem.json',
            '--server-url', 'http://localhost:8000/fhir',
            '--test-id', 'test-psgc-codesystem-123'
        ], capture_output=True, text=True, timeout=30, input='yes\n')  # Provide 'yes' for any prompts
        
        print(f"Test upload actual run return code: {result.returncode}")
        if result.stdout:
            print(f"STDOUT: {result.stdout}")
        if result.stderr:
            print(f"STDERR: {result.stderr}")
        
    except subprocess.TimeoutExpired:
        print("Test upload script timed out")
    except Exception as e:
        print(f"Error running test upload script: {e}")
    
    # Test 2: Production upload script
    print("\n2. Testing production upload script...")
    try:
        # First run with dry-run
        result = subprocess.run([
            sys.executable, './upload_production_script.py',
            '--input', './test_codesystem.json',
            '--server-url', 'http://localhost:8000/fhir',
            '--dry-run'
        ], capture_output=True, text=True, timeout=30)
        
        print(f"Production upload dry-run return code: {result.returncode}")
        if result.stdout:
            print(f"STDOUT: {result.stdout}")
        if result.stderr:
            print(f"STDERR: {result.stderr}")
        
        # Now run without dry-run but with --confirm to skip prompt
        result = subprocess.run([
            sys.executable, './upload_production_script.py',
            '--input', './test_codesystem.json',
            '--server-url', 'http://localhost:8000/fhir',
            '--confirm'
        ], capture_output=True, text=True, timeout=30)
        
        print(f"Production upload actual run return code: {result.returncode}")
        if result.stdout:
            print(f"STDOUT: {result.stdout}")
        if result.stderr:
            print(f"STDERR: {result.stderr}")
        
    except subprocess.TimeoutExpired:
        print("Production upload script timed out")
    except Exception as e:
        print(f"Error running production upload script: {e}")
    
    # Test 3: Undo script
    print("\n3. Testing undo script...")
    try:
        # First run with dry-run equivalent (we'll just check if resource exists)
        result = subprocess.run([
            sys.executable, './undo_script.py',
            '--server-url', 'http://localhost:8000/fhir',
            '--codesystem-id', 'psgc-geographic-codes',
            '--no-prompt'  # Skip confirmation for testing
        ], capture_output=True, text=True, timeout=30)
        
        print(f"Undo script return code: {result.returncode}")
        if result.stdout:
            print(f"STDOUT: {result.stdout}")
        if result.stderr:
            print(f"STDERR: {result.stderr}")
        
    except subprocess.TimeoutExpired:
        print("Undo script timed out")
    except Exception as e:
        print(f"Error running undo script: {e}")
    
    print("\nTesting completed!")


def main():
    """Main function to run the tests."""
    print("Starting FHIR upload functionality tests...")
    
    # Start the mock server
    server_process = start_mock_server()
    
    try:
        # Wait a bit for the server to be ready
        time.sleep(3)
        
        # Test the upload functionality
        test_upload_scripts()
        
    finally:
        # Shut down the server gracefully
        try:
            requests.post('http://localhost:8000/_shutdown')
        except:
            # If the shutdown request fails, terminate the process
            server_process.terminate()
            server_process.wait()


if __name__ == '__main__':
    main()
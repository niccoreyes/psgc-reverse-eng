#!/usr/bin/env python3
"""
Mock FHIR Server for Testing PSGC Upload Scripts

This script creates a simple mock FHIR server that can be used to test 
the upload scripts without needing access to the real tx.fhirlab.net server.
"""

from flask import Flask, request, jsonify, Response
import json
import uuid
from typing import Dict, Any, Optional
import threading
import time


app = Flask(__name__)

# In-memory storage for FHIR resources (for testing purposes only)
fhir_resources: Dict[str, Any] = {}
shutdown_event = threading.Event()


def generate_resource_id():
    """Generate a unique ID for FHIR resources."""
    return str(uuid.uuid4())


@app.route('/CodeSystem', methods=['POST'])
def create_codesystem():
    """Create a new CodeSystem resource."""
    try:
        resource = request.get_json()
        
        if not resource or 'resourceType' not in resource:
            return jsonify({'error': 'Invalid resource: missing resourceType'}), 400
        
        if resource['resourceType'] != 'CodeSystem':
            return jsonify({'error': 'Invalid resource: not a CodeSystem'}), 400
        
        # If an ID is provided in the resource, use it; otherwise, generate one
        resource_id = resource.get('id') or generate_resource_id()
        resource['id'] = resource_id
        
        # Store the resource
        fhir_resources[resource_id] = resource
        
        return jsonify(resource), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/CodeSystem/<resource_id>', methods=['GET'])
def get_codesystem(resource_id):
    """Get a specific CodeSystem by ID."""
    try:
        if resource_id not in fhir_resources:
            return jsonify({'error': 'Resource not found'}), 404
        
        return jsonify(fhir_resources[resource_id]), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/CodeSystem/<resource_id>', methods=['PUT'])
def update_codesystem(resource_id):
    """Update an existing CodeSystem."""
    try:
        if resource_id not in fhir_resources:
            return jsonify({'error': 'Resource not found'}), 404
        
        resource = request.get_json()
        
        if not resource or 'resourceType' not in resource:
            return jsonify({'error': 'Invalid resource: missing resourceType'}), 400
        
        if resource['resourceType'] != 'CodeSystem':
            return jsonify({'error': 'Invalid resource: not a CodeSystem'}), 400
        
        # Make sure the ID matches the URL
        resource['id'] = resource_id
        
        # Update the resource
        fhir_resources[resource_id] = resource
        
        return jsonify(resource), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/CodeSystem/<resource_id>', methods=['DELETE'])
def delete_codesystem(resource_id):
    """Delete a CodeSystem by ID."""
    try:
        if resource_id not in fhir_resources:
            return jsonify({'error': 'Resource not found'}), 404
        
        del fhir_resources[resource_id]
        
        # Return empty response with 204 status for successful deletion
        return '', 204
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/_shutdown', methods=['POST'])
def shutdown():
    """Graceful shutdown endpoint."""
    shutdown_event.set()
    return jsonify({'message': 'Shutting down'})


def run_mock_server(host='127.0.0.1', port=8000):
    """Run the mock FHIR server."""
    print(f"Starting mock FHIR server on {host}:{port}")
    print(f"Use FHIR_SERVER_API_KEY=mock_key when running upload scripts")
    print("Press Ctrl+C to stop the server\n")
    
    try:
        app.run(host=host, port=port, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        print("Server stopped.")


if __name__ == '__main__':
    import os
    os.environ['FLASK_ENV'] = 'production'  # Disable Flask's debug mode for production
    run_mock_server()
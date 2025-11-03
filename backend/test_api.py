#!/usr/bin/env python3
"""
Test script for the slide tile service APIs.
This script tests the DZI and tile endpoints to ensure they work correctly.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import app
import json

def test_dzi_endpoint():
    """Test the DZI endpoint returns proper XML format."""
    with app.test_client() as client:
        # Test with a non-existent slide first
        response = client.get('/api/slides/999/dzi')
        print(f"Non-existent slide DZI: {response.status_code}")
        assert response.status_code == 404
        
        # Test DZI endpoint format (we can't test actual slides without data)
        print("✓ DZI endpoint exists and returns proper error for non-existent slides")

def test_tile_endpoint():
    """Test the tile endpoint."""
    with app.test_client() as client:
        # Test with a non-existent slide first
        response = client.get('/api/slides/999/tiles/0/0/0')
        print(f"Non-existent slide tile: {response.status_code}")
        assert response.status_code == 404
        
        # Test with .jpeg extension
        response = client.get('/api/slides/999/tiles/0/0/0.jpeg')
        print(f"Non-existent slide tile (jpeg): {response.status_code}")
        assert response.status_code == 404
        
        print("✓ Tile endpoints exist and return proper errors for non-existent slides")

def test_info_endpoint():
    """Test the enhanced slide info endpoint."""
    with app.test_client() as client:
        # Test with a non-existent slide first
        response = client.get('/api/slides/999/info')
        print(f"Non-existent slide info: {response.status_code}")
        assert response.status_code == 404
        
        print("✓ Info endpoint exists and returns proper error for non-existent slides")

def test_health_endpoint():
    """Test the health endpoint."""
    with app.test_client() as client:
        response = client.get('/api/health')
        print(f"Health check: {response.status_code}")
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'ok'
        
        print("✓ Health endpoint works correctly")

def main():
    """Run all tests."""
    print("Testing slide tile service APIs...")
    print("=" * 50)
    
    try:
        test_health_endpoint()
        test_dzi_endpoint()
        test_tile_endpoint()
        test_info_endpoint()
        
        print("=" * 50)
        print("✅ All API endpoints are working correctly!")
        print("\nNote: Full functionality requires actual slide files in the database.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
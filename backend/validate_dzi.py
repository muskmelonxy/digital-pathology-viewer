#!/usr/bin/env python3
"""
Validate DZI XML format
This script generates and validates the DZI XML format to ensure it's correct for OpenSeadragon.
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom

def generate_dzi_xml(width=46000, height=32914, tile_size=256, overlap=0, format="jpeg"):
    """Generate DZI XML in the expected format."""
    xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<Image xmlns="http://schemas.microsoft.com/deepzoom/2008"
       Format="{format}"
       Overlap="{overlap}"
       TileSize="{tile_size}">
  <Size Width="{width}" Height="{height}"/>
</Image>'''
    return xml_content

def validate_dzi_xml(xml_content):
    """Validate that the DZI XML is well-formed and has the expected structure."""
    try:
        # Parse the XML
        root = ET.fromstring(xml_content)
        
        # Check namespace
        expected_namespace = "http://schemas.microsoft.com/deepzoom/2008"
        if root.tag != f"{{{expected_namespace}}}Image":
            print(f"❌ Wrong namespace: {root.tag}")
            return False
        
        # Check required attributes
        required_attrs = ['Format', 'Overlap', 'TileSize']
        for attr in required_attrs:
            if attr not in root.attrib:
                print(f"❌ Missing attribute: {attr}")
                return False
        
        # Check Size element
        size_elem = root.find(f"{{{expected_namespace}}}Size")
        if size_elem is None:
            print("❌ Missing Size element")
            return False
        
        # Check Size attributes
        if 'Width' not in size_elem.attrib or 'Height' not in size_elem.attrib:
            print("❌ Size element missing Width or Height")
            return False
        
        print("✅ DZI XML format is valid")
        return True
        
    except ET.ParseError as e:
        print(f"❌ XML parsing error: {e}")
        return False

def format_xml_pretty(xml_content):
    """Format XML for pretty printing."""
    try:
        dom = minidom.parseString(xml_content)
        return dom.toprettyxml(indent="  ")
    except Exception as e:
        print(f"Error formatting XML: {e}")
        return xml_content

def main():
    """Generate and validate DZI XML."""
    print("DZI XML Format Validation")
    print("=" * 40)
    
    # Generate sample DZI XML
    dzi_xml = generate_dzi_xml()
    
    print("Generated DZI XML:")
    print("-" * 20)
    print(format_xml_pretty(dzi_xml))
    print("-" * 20)
    
    # Validate the XML
    if validate_dzi_xml(dzi_xml):
        print("\n✅ DZI XML is ready for OpenSeadragon!")
    else:
        print("\n❌ DZI XML validation failed")
        return 1
    
    # Test with different parameters
    print("\nTesting with different parameters...")
    test_cases = [
        (1000, 800, 256, 1, "jpeg"),
        (50000, 40000, 512, 2, "png"),
    ]
    
    for width, height, tile_size, overlap, format in test_cases:
        xml = generate_dzi_xml(width, height, tile_size, overlap, format)
        if validate_dzi_xml(xml):
            print(f"✅ Test case {width}x{height} passed")
        else:
            print(f"❌ Test case {width}x{height} failed")
            return 1
    
    print("\n🎉 All tests passed!")
    return 0

if __name__ == '__main__':
    exit(main())
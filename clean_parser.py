#!/usr/bin/env python3
"""
Script to clean null bytes from parser.py file
"""

def clean_null_bytes(input_file, output_file):
    """Remove null bytes from a file"""
    try:
        # Read the file in binary mode
        with open(input_file, 'rb') as f:
            content = f.read()
        
        # Remove null bytes
        cleaned_content = content.replace(b'\x00', b'')
        
        # Write the cleaned content back
        with open(output_file, 'wb') as f:
            f.write(cleaned_content)
        
        print(f"Successfully cleaned {input_file} -> {output_file}")
        print(f"Removed {len(content) - len(cleaned_content)} null bytes")
        
    except Exception as e:
        print(f"Error cleaning file: {e}")

if __name__ == "__main__":
    clean_null_bytes("parser.py", "parser_clean.py")

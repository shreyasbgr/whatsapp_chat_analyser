#!/usr/bin/env python3
"""
Debug script to analyze media patterns in WhatsApp chat files
"""

import re
import sys
from typing import List

def analyze_file_for_media_patterns(file_path: str):
    """Analyze a chat file to identify media patterns."""
    
    print(f"🔍 Analyzing file: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return
    
    print(f"📄 Total lines in file: {len(lines)}")
    
    # Common media indicators to look for
    media_indicators = [
        'omitted', 'attached', 'media', 'image', 'video', 'audio', 'document',
        'sticker', 'gif', 'voice', 'contact', 'location', 'poll',
        'IMG-', 'VID-', 'AUD-', 'DOC-', '.jpg', '.jpeg', '.png', '.mp4',
        '.pdf', '.doc', '.docx', '<', '>'
    ]
    
    # Find lines containing potential media patterns
    media_lines = []
    for i, line in enumerate(lines, 1):
        line_lower = line.lower()
        for indicator in media_indicators:
            if indicator in line_lower:
                media_lines.append((i, line.strip()))
                break
    
    print(f"📊 Lines containing potential media patterns: {len(media_lines)}")
    
    if media_lines:
        print("\n📋 Sample media lines (first 20):")
        for line_num, line in media_lines[:20]:
            print(f"Line {line_num}: {repr(line)}")
    
    # Look for specific patterns
    patterns_to_check = [
        r'<.*omitted.*>',
        r'<.*attached.*>',
        r'image omitted',
        r'video omitted',
        r'audio omitted',
        r'document omitted',
        r'sticker omitted',
        r'voice.*omitted',
        r'contact.*omitted',
        r'location.*omitted',
        r'poll.*omitted',
        r'IMG-\d+',
        r'VID-\d+',
        r'AUD-\d+',
        r'DOC-\d+',
        r'attached:.*\.(jpg|jpeg|png|gif|mp4|mov|pdf|doc|docx|txt|zip|rar)',
    ]
    
    print("\n🔍 Pattern matching results:")
    for pattern in patterns_to_check:
        matches = 0
        sample_matches = []
        
        for line_num, line in enumerate(lines, 1):
            if re.search(pattern, line, re.IGNORECASE):
                matches += 1
                if len(sample_matches) < 3:
                    sample_matches.append((line_num, line.strip()))
        
        print(f"Pattern '{pattern}': {matches} matches")
        if sample_matches:
            for line_num, line in sample_matches:
                print(f"  Line {line_num}: {repr(line)}")
    
    # Check file format
    first_line = next((line for line in lines if line.strip()), "")
    if first_line.startswith('['):
        print(f"\n📱 Format detected: PC")
        print(f"First line: {repr(first_line)}")
    elif "-" in first_line and "," in first_line:
        print(f"\n📱 Format detected: Mobile")
        print(f"First line: {repr(first_line)}")
    else:
        print(f"\n📱 Format detected: Unknown")
        print(f"First line: {repr(first_line)}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python debug_media_patterns.py <chat_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    analyze_file_for_media_patterns(file_path)

if __name__ == "__main__":
    main()

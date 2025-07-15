#!/usr/bin/env python3
"""
Test script to validate enhanced media detection in WhatsApp chat parser
"""

import os
import sys
from parser import parse_chat_file
from collections import Counter

def test_media_detection():
    """Test the enhanced media detection with both mobile and PC reference files."""
    
    mobile_file = "mobile-pickleball-thane.txt"
    pc_reference_file = "pc_pickleball_thane_chat.txt"
    
    # Check if files exist
    if not os.path.exists(mobile_file):
        print(f"Error: Mobile file '{mobile_file}' not found")
        return
    
    if not os.path.exists(pc_reference_file):
        print(f"Warning: PC reference file '{pc_reference_file}' not found")
        print("Running without PC reference...")
        pc_reference_file = None
    
    print("🔍 Testing enhanced media detection...")
    print(f"📱 Mobile file: {mobile_file}")
    if pc_reference_file:
        print(f"💻 PC reference file: {pc_reference_file}")
    print("-" * 50)
    
    # Parse the chat file
    try:
        messages = parse_chat_file(mobile_file, utc_offset_hours=0, pc_reference_file=pc_reference_file)
        print(f"✅ Successfully parsed {len(messages)} messages")
        
        # Analyze media types (messages is a DataFrame)
        media_counter = Counter()
        media_messages = []
        
        # Convert DataFrame to list of dictionaries for easier processing
        messages_list = messages.to_dict('records')
        
        for msg in messages_list:
            if msg.get('media'):
                media_counter[msg['media']] += 1
                media_messages.append(msg)
        
        print(f"\n📊 Media Detection Results:")
        print(f"Total messages: {len(messages)}")
        print(f"Media messages: {len(media_messages)}")
        print(f"Media percentage: {len(media_messages)/len(messages)*100:.1f}%")
        
        if media_counter:
            print(f"\n📋 Media Types Found:")
            for media_type, count in media_counter.most_common():
                print(f"  {media_type}: {count}")
        else:
            print("\n❌ No media messages detected")
        
        # Show sample media messages
        if media_messages:
            print(f"\n🔍 Sample Media Messages (first 5):")
            for i, msg in enumerate(media_messages[:5]):
                print(f"\n{i+1}. [{msg['datetime_ist_human']}] {msg['sender']}")
                print(f"   Type: {msg['media']}")
                print(f"   Raw: {msg['raw_message'][:100]}...")
                if msg.get('media_file_name'):
                    print(f"   File: {msg['media_file_name']}")
                if msg.get('message'):
                    print(f"   Caption: {msg['message']}")
        
        # Check for enhancement statistics if PC reference was used
        if pc_reference_file:
            enhanced_count = sum(1 for msg in media_messages if msg.get('enhanced_from_pc', False))
            print(f"\n🔧 Enhancement Statistics:")
            print(f"Enhanced media messages: {enhanced_count}")
            print(f"Enhancement rate: {enhanced_count/len(media_messages)*100:.1f}%" if media_messages else "0%")
        
    except Exception as e:
        print(f"❌ Error parsing chat file: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_media_detection()

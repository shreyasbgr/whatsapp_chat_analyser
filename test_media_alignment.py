#!/usr/bin/env python3

import sys
import os
from datetime import timedelta

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parser import parse_pc, parse_mobile

def test_media_detection():
    """Test media detection patterns between PC and mobile formats"""
    
    # File paths
    pc_file = "/Users/shreyas/Code/whatsapp_chat_analysis/pc_pickleball_thane_chat.txt"
    mobile_file = "/Users/shreyas/Code/whatsapp_chat_analysis/mobile-pickleball-thane.txt"
    
    # Parse both files with IST offset (5.5 hours)
    ist_offset = timedelta(hours=5, minutes=30)
    
    # Read PC file
    print("Reading PC file...")
    with open(pc_file, 'r', encoding='utf-8') as f:
        pc_lines = f.readlines()
    print(f"PC file lines: {len(pc_lines)}")
    
    # Read Mobile file
    print("Reading Mobile file...")
    with open(mobile_file, 'r', encoding='utf-8') as f:
        mobile_lines = f.readlines()
    print(f"Mobile file lines: {len(mobile_lines)}")
    
    print("\nParsing PC format...")
    pc_messages = parse_pc(pc_lines, ist_offset)
    print(f"PC messages parsed: {len(pc_messages)}")
    
    print("\nParsing Mobile format...")
    mobile_messages = parse_mobile(mobile_lines, ist_offset)
    print(f"Mobile messages parsed: {len(mobile_messages)}")
    
    # Count messages by media type
    def count_media_types(messages):
        media_counts = {}
        for msg in messages:
            if msg.get('media'):
                media_type = msg['media']
                media_counts[media_type] = media_counts.get(media_type, 0) + 1
        return media_counts
    
    pc_media_counts = count_media_types(pc_messages)
    mobile_media_counts = count_media_types(mobile_messages)
    
    print("\n=== MEDIA TYPE COUNTS ===")
    print("\nPC Format:")
    for media_type, count in sorted(pc_media_counts.items()):
        print(f"  {media_type}: {count}")
    
    print("\nMobile Format:")
    for media_type, count in sorted(mobile_media_counts.items()):
        print(f"  {media_type}: {count}")
    
    # Calculate total media messages
    pc_total_media = sum(pc_media_counts.values())
    mobile_total_media = sum(mobile_media_counts.values())
    
    print(f"\nTotal media messages:")
    print(f"  PC: {pc_total_media}")
    print(f"  Mobile: {mobile_total_media}")
    print(f"  Difference: {pc_total_media - mobile_total_media}")
    
    # Show contact detection specifically
    pc_contacts = pc_media_counts.get('contact', 0)
    mobile_contacts = mobile_media_counts.get('contact', 0)
    
    print(f"\nContact messages:")
    print(f"  PC: {pc_contacts}")
    print(f"  Mobile: {mobile_contacts}")
    print(f"  Difference: {pc_contacts - mobile_contacts}")
    
    # Show some examples of media messages from both formats
    print("\n=== SAMPLE MEDIA MESSAGES ===")
    
    print("\nPC Format - Sample media messages:")
    pc_media_messages = [msg for msg in pc_messages if msg.get('media')][:5]
    for i, msg in enumerate(pc_media_messages):
        print(f"  {i+1}. Type: {msg['media']}, Content: {msg['message'][:100]}...")
    
    print("\nMobile Format - Sample media messages:")
    mobile_media_messages = [msg for msg in mobile_messages if msg.get('media')][:5]
    for i, msg in enumerate(mobile_media_messages):
        print(f"  {i+1}. Type: {msg['media']}, Content: {msg['message'][:100]}...")
    
    # Show contact messages specifically
    print("\n=== CONTACT MESSAGES ===")
    
    print("\nPC Format - Contact messages:")
    pc_contact_messages = [msg for msg in pc_messages if msg.get('media') == 'contact'][:3]
    for i, msg in enumerate(pc_contact_messages):
        print(f"  {i+1}. {msg['message'][:150]}...")
    
    print("\nMobile Format - Contact messages:")
    mobile_contact_messages = [msg for msg in mobile_messages if msg.get('media') == 'contact'][:3]
    for i, msg in enumerate(mobile_contact_messages):
        print(f"  {i+1}. {msg['message'][:150]}...")

if __name__ == "__main__":
    test_media_detection()

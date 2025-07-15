#!/usr/bin/env python3

from parser import parse_chat_file
from datetime import datetime
import pandas as pd

def enhance_mobile_media_detection():
    """Use timestamp-based matching to improve mobile media type detection."""
    print("Enhancing mobile media detection using timestamp matching...")
    
    # Parse both files
    pc_df = parse_chat_file('pc_pickleball_thane_chat.txt')
    mobile_df = parse_chat_file('mobile-pickleball-thane.txt')
    
    # Get media messages from both
    pc_media = pc_df[pc_df['media'] != '']
    mobile_media = mobile_df[mobile_df['media'] != '']
    
    print(f"PC media: {len(pc_media)} vs Mobile media: {len(mobile_media)}")
    
    # Create a timestamp-based mapping from PC to mobile
    pc_timestamp_media_map = {}
    for _, row in pc_media.iterrows():
        timestamp = row['datetime_ist']
        media_type = row['media']
        # Create a key based on timestamp (rounded to minute for fuzzy matching)
        dt = datetime.fromisoformat(timestamp)
        key = dt.strftime('%Y-%m-%d %H:%M')
        pc_timestamp_media_map[key] = media_type
    
    # Apply the mapping to mobile generic media messages
    mobile_generic_media = mobile_media[mobile_media['media'] == 'media']
    print(f"Mobile generic media to enhance: {len(mobile_generic_media)}")
    
    enhanced_count = 0
    enhancement_mapping = {}
    
    for idx, row in mobile_generic_media.iterrows():
        timestamp = row['datetime_ist']
        dt = datetime.fromisoformat(timestamp)
        key = dt.strftime('%Y-%m-%d %H:%M')
        
        if key in pc_timestamp_media_map:
            inferred_type = pc_timestamp_media_map[key]
            enhancement_mapping[idx] = inferred_type
            enhanced_count += 1
    
    print(f"Enhanced {enhanced_count} mobile media messages using timestamp matching")
    
    # Show the distribution of enhanced types
    if enhancement_mapping:
        print("\nEnhanced media types distribution:")
        from collections import Counter
        enhanced_types = Counter(enhancement_mapping.values())
        for media_type, count in enhanced_types.items():
            print(f"  {media_type}: {count}")
    
    return enhancement_mapping

def apply_enhancement_to_mobile_parser():
    """Apply the enhancement logic directly to the mobile parser."""
    # This would be integrated into the actual parser
    print("\nThis enhancement logic should be integrated into the mobile parser...")
    
    # The approach would be:
    # 1. Parse both PC and mobile initially
    # 2. Create timestamp-based mapping from PC media types
    # 3. Apply the mapping to mobile generic media messages
    # 4. Update the mobile parser to use this enhanced detection
    
    pass

if __name__ == "__main__":
    enhancement_mapping = enhance_mobile_media_detection()
    apply_enhancement_to_mobile_parser()

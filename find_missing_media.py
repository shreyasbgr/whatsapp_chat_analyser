#!/usr/bin/env python3

from parser import parse_chat_file
from datetime import datetime
import pandas as pd

def find_missing_media():
    """Find the 42 missing media messages in mobile format."""
    print("Finding missing media messages in mobile format...")
    
    # Parse both files
    pc_df = parse_chat_file('pc_pickleball_thane_chat.txt')
    mobile_df = parse_chat_file('mobile-pickleball-thane.txt')
    
    # Get media messages from both
    pc_media = pc_df[pc_df['media'] != '']
    mobile_media = mobile_df[mobile_df['media'] != '']
    
    print(f"PC media: {len(pc_media)}")
    print(f"Mobile media: {len(mobile_media)}")
    print(f"Missing: {len(pc_media) - len(mobile_media)}")
    
    # Create timestamp-based comparison
    pc_media_times = {}
    for _, row in pc_media.iterrows():
        timestamp = row['datetime_ist']
        dt = datetime.fromisoformat(timestamp)
        key = dt.strftime('%Y-%m-%d %H:%M')
        pc_media_times[key] = {
            'media_type': row['media'],
            'raw_message': row['raw_message'],
            'sender': row['sender'],
            'timestamp': timestamp
        }
    
    mobile_media_times = {}
    for _, row in mobile_media.iterrows():
        timestamp = row['datetime_ist']
        dt = datetime.fromisoformat(timestamp)
        key = dt.strftime('%Y-%m-%d %H:%M')
        mobile_media_times[key] = {
            'media_type': row['media'],
            'raw_message': row['raw_message'],
            'sender': row['sender'],
            'timestamp': timestamp
        }
    
    # Find PC media messages that don't exist in mobile
    missing_in_mobile = []
    for key, pc_msg in pc_media_times.items():
        if key not in mobile_media_times:
            missing_in_mobile.append(pc_msg)
    
    print(f"\nFound {len(missing_in_mobile)} media messages in PC that are missing in mobile:")
    
    # Show examples of missing messages
    for i, msg in enumerate(missing_in_mobile[:20]):  # Show first 20
        print(f"{i+1}. {msg['timestamp']} - {msg['media_type']} - {msg['sender']}")
        print(f"   Raw: {msg['raw_message'][:100]}...")
        print()
    
    # Now let's check what these messages look like in the mobile format
    print("Checking what these missing messages look like in mobile format...")
    
    # Get all mobile messages (including non-media)
    mobile_all = mobile_df
    
    matches_found = []
    for missing_msg in missing_in_mobile[:10]:  # Check first 10
        timestamp = missing_msg['timestamp']
        dt = datetime.fromisoformat(timestamp)
        
        # Look for messages around the same time in mobile
        for _, mobile_row in mobile_all.iterrows():
            mobile_dt = datetime.fromisoformat(mobile_row['datetime_ist'])
            time_diff = abs((dt - mobile_dt).total_seconds())
            
            if time_diff <= 60:  # Within 1 minute
                matches_found.append({
                    'pc_msg': missing_msg,
                    'mobile_msg': mobile_row,
                    'time_diff': time_diff
                })
                break
    
    if matches_found:
        print(f"\nFound {len(matches_found)} corresponding messages in mobile format:")
        for i, match in enumerate(matches_found):
            print(f"{i+1}. Time diff: {match['time_diff']} seconds")
            print(f"   PC ({match['pc_msg']['media_type']}): {match['pc_msg']['raw_message'][:100]}...")
            print(f"   Mobile (media='{match['mobile_msg']['media']}'): {match['mobile_msg']['raw_message'][:100]}...")
            print()
    
    return missing_in_mobile, matches_found

if __name__ == "__main__":
    missing_in_mobile, matches_found = find_missing_media()

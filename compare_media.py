#!/usr/bin/env python3

from parser import parse_chat_file

def compare_media():
    """Compare total media shared between PC and mobile formats."""
    print("Comparing total media shared...")
    
    # Parse both files
    pc_df = parse_chat_file('pc_pickleball_thane_chat.txt')
    mobile_df = parse_chat_file('mobile-pickleball-thane.txt')
    
    # Calculate total media
    pc_media_count = len(pc_df[pc_df['media'] != ''])
    mobile_media_count = len(mobile_df[mobile_df['media'] != ''])
    
    print(f"PC total media messages: {pc_media_count}")
    print(f"Mobile total media messages: {mobile_media_count}")
    
    # Find media types
    pc_media_types = pc_df['media'].value_counts()
    mobile_media_types = mobile_df['media'].value_counts()
    
    print("\nPC media type distribution:")
    for media_type, count in pc_media_types.items():
        if media_type:
            print(f"  {media_type}: {count}")
    
    print("\nMobile media type distribution:")
    for media_type, count in mobile_media_types.items():
        if media_type:
            print(f"  {media_type}: {count}")

    # Identify discrepancies in media types
    discrepancies = []
    for media_type in set(pc_media_types.index).union(set(mobile_media_types.index)):
        pc_count = pc_media_types.get(media_type, 0)
        mobile_count = mobile_media_types.get(media_type, 0)
        if pc_count != mobile_count:
            discrepancies.append((media_type, pc_count, mobile_count))
            
    if discrepancies:
        print("\nDiscrepancies in media types:")
        for media_type, pc_count, mobile_count in discrepancies:
            print(f"  {media_type}: PC = {pc_count}, Mobile = {mobile_count}")
    else:
        print("\nNo discrepancies in media types found.")

if __name__ == "__main__":
    compare_media()

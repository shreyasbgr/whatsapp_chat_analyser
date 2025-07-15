#!/usr/bin/env python3

from parser import parse_chat_file

def analyze_media_patterns():
    """Analyze media patterns to identify what's being missed in mobile parsing."""
    print("Analyzing media patterns...")
    
    # Parse both files
    pc_df = parse_chat_file('pc_pickleball_thane_chat.txt')
    mobile_df = parse_chat_file('mobile-pickleball-thane.txt')
    
    # Get media messages from both
    pc_media = pc_df[pc_df['media'] != '']
    mobile_media = mobile_df[mobile_df['media'] != '']
    
    print(f"PC total media messages: {len(pc_media)}")
    print(f"Mobile total media messages: {len(mobile_media)}")
    print(f"Difference: {len(pc_media) - len(mobile_media)}")
    
    # Show sample PC media messages by type
    print("\nPC media samples by type:")
    for media_type in pc_media['media'].unique():
        if media_type:
            sample = pc_media[pc_media['media'] == media_type].head(3)
            print(f"\n{media_type} ({len(pc_media[pc_media['media'] == media_type])} total):")
            for _, row in sample.iterrows():
                print(f"  - {row['raw_message'][:100]}...")
    
    # Show sample mobile media messages
    print("\nMobile media samples:")
    mobile_media_samples = mobile_media[mobile_media['media'] == 'media'].head(10)
    print(f"\nGeneric 'media' ({len(mobile_media[mobile_media['media'] == 'media'])} total):")
    for _, row in mobile_media_samples.iterrows():
        print(f"  - {row['raw_message'][:100]}...")
    
    # Check for potential missed patterns in mobile
    print("\nChecking for potential missed patterns in mobile messages...")
    
    # Look for messages that might contain media indicators but aren't detected
    mobile_all = mobile_df[mobile_df['media'] == '']  # Non-media messages
    
    potential_media_keywords = [
        'omitted', 'attached', 'image', 'video', 'audio', 'document', 
        'sticker', 'gif', 'IMG-', 'VID-', 'AUD-', 'DOC-', '.jpg', '.png', 
        '.mp4', '.mov', '.pdf', '.doc', 'file attached'
    ]
    
    missed_media = []
    for _, row in mobile_all.iterrows():
        raw_msg = row['raw_message'].lower()
        for keyword in potential_media_keywords:
            if keyword in raw_msg:
                missed_media.append(row)
                break
    
    if missed_media:
        print(f"\nFound {len(missed_media)} potential media messages missed in mobile:")
        for i, row in enumerate(missed_media[:10]):  # Show first 10
            print(f"  {i+1}. {row['raw_message'][:100]}...")
    else:
        print("\nNo obvious missed media patterns found in mobile messages.")
    
    # Compare timestamps to see if it's the same messages
    print("\nComparing timestamps of media messages...")
    
    # Get timestamps from both formats
    pc_media_times = set(pc_media['datetime_ist'].tolist())
    mobile_media_times = set(mobile_media['datetime_ist'].tolist())
    
    # Find differences
    pc_only_times = pc_media_times - mobile_media_times
    mobile_only_times = mobile_media_times - pc_media_times
    common_times = pc_media_times & mobile_media_times
    
    print(f"Common media message timestamps: {len(common_times)}")
    print(f"PC-only media message timestamps: {len(pc_only_times)}")
    print(f"Mobile-only media message timestamps: {len(mobile_only_times)}")
    
    # Show examples of PC-only media messages
    if pc_only_times:
        print(f"\nExamples of media messages only found in PC:")
        pc_only_messages = pc_media[pc_media['datetime_ist'].isin(list(pc_only_times))]
        for _, row in pc_only_messages.head(5).iterrows():
            print(f"  - {row['datetime_ist_human']} - {row['media']}: {row['raw_message'][:100]}...")

if __name__ == "__main__":
    analyze_media_patterns()

#!/usr/bin/env python3

from parser import parse_chat_file

def analyze_missed_media():
    """Analyze specific media patterns that are being missed in mobile parsing."""
    print("Analyzing missed media patterns...")
    
    # Parse both files
    pc_df = parse_chat_file('pc_pickleball_thane_chat.txt')
    mobile_df = parse_chat_file('mobile-pickleball-thane.txt')
    
    # Get media messages from both
    pc_media = pc_df[pc_df['media'] != '']
    mobile_media = mobile_df[mobile_df['media'] != '']
    
    print(f"PC media: {len(pc_media)} vs Mobile media: {len(mobile_media)}")
    print(f"Difference: {len(pc_media) - len(mobile_media)}")
    
    # Analyze mobile messages that are still marked as generic "media"
    mobile_generic_media = mobile_media[mobile_media['media'] == 'media']
    print(f"\nMobile generic media messages: {len(mobile_generic_media)}")
    
    print("\nSample mobile generic media messages:")
    for i, (_, row) in enumerate(mobile_generic_media.head(20).iterrows()):
        print(f"{i+1}. Raw: {row['raw_message'][:150]}...")
        print(f"   Msg: {row['message'][:100]}...")
        print()
    
    # Look for specific patterns in PC media that might help identify types
    print("PC media type samples for comparison:")
    for media_type in ['image', 'video', 'document', 'gif', 'sticker', 'audio']:
        pc_samples = pc_media[pc_media['media'] == media_type]
        if len(pc_samples) > 0:
            print(f"\n{media_type} samples from PC:")
            for _, row in pc_samples.head(3).iterrows():
                print(f"  Raw: {row['raw_message'][:100]}...")
                print(f"  Msg: {row['message'][:50]}...")
    
    # Check for potential patterns in mobile messages that could indicate media types
    print("\nChecking for media type indicators in mobile generic media...")
    
    type_indicators = {
        'image': ['jpg', 'jpeg', 'png', 'gif', 'image', 'photo', 'picture', 'pic'],
        'video': ['mp4', 'mov', 'avi', 'video', 'vid'],
        'document': ['pdf', 'doc', 'docx', 'txt', 'document', 'file'],
        'gif': ['gif'],
        'sticker': ['sticker'],
        'audio': ['mp3', 'wav', 'audio', 'voice']
    }
    
    for media_type, indicators in type_indicators.items():
        count = 0
        for _, row in mobile_generic_media.iterrows():
            raw_msg = row['raw_message'].lower()
            msg = row['message'].lower()
            
            for indicator in indicators:
                if indicator in raw_msg or indicator in msg:
                    count += 1
                    break
        
        if count > 0:
            print(f"  {media_type}: {count} potential matches")

if __name__ == "__main__":
    analyze_missed_media()

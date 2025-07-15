#!/usr/bin/env python3

from parser import parse_chat_file, enhance_mobile_media_with_pc_reference, parse_pc, parse_mobile
from datetime import datetime, timedelta
import pandas as pd
import os

def parse_chat_with_enhancement(file_path, pc_reference_file=None, utc_offset_hours=0):
    """
    Parse WhatsApp chat file with optional PC reference for mobile enhancement.
    
    Args:
        file_path: Path to the main chat file to parse
        pc_reference_file: Optional path to PC format file for mobile enhancement
        utc_offset_hours: UTC offset in hours
    
    Returns:
        pd.DataFrame: Enhanced parsed chat data
    """
    # Parse the main file
    df = parse_chat_file(file_path, utc_offset_hours)
    
    # If we have a PC reference file and the main file is mobile format, enhance it
    if pc_reference_file and os.path.exists(pc_reference_file):
        # Check if the main file is mobile format
        with open(file_path, "r", encoding="utf-8") as f:
            first_line = f.readline().strip()
        
        if not first_line.startswith('[') and '-' in first_line:
            print("\n🔧 Detected mobile format, applying PC reference enhancement...")
            
            # Parse PC reference file for media types
            pc_df = parse_chat_file(pc_reference_file, utc_offset_hours)
            
            # Convert back to message format for enhancement
            main_messages = df.to_dict('records')
            pc_messages = pc_df.to_dict('records')
            
            # Apply enhancement
            enhanced_messages = enhance_mobile_media_with_pc_reference(main_messages, pc_messages)
            
            # Convert back to DataFrame
            df = pd.DataFrame(enhanced_messages)
            
            # Re-apply the same post-processing as in parse_chat_file
            df["message"] = df["message"].astype(str).str.strip()
            df["message_modifier"] = df["message_modifier"].astype(str).str.strip()
            df["message"] = df["message"].str.replace(r'<This message was edited>', '', regex=True)
            df["message"] = df["message"].str.replace(r'\\(edited\\)', '', regex=True)
            df["message"] = df["message"].str.replace(r'\\[edited\\]', '', regex=True)
            df["message"] = df["message"].str.strip()
            
            print(f"\n📊 Enhanced DataFrame Statistics:")
            print(f"Total rows in DataFrame: {len(df)}")
            print(f"Media messages: {len(df[df['media'] != ''])}")
            print(f"Group notifications: {len(df[df['sender'] == 'group_notification'])}")
            print(f"Unique senders: {df['sender'].nunique()}")
    
    return df

def compare_enhanced_results():
    """Compare parsing results with and without enhancement."""
    print("Comparing enhanced vs standard mobile parsing...")
    
    # Standard mobile parsing
    mobile_df = parse_chat_file('mobile-pickleball-thane.txt')
    
    # Enhanced mobile parsing with PC reference
    enhanced_df = parse_chat_with_enhancement('mobile-pickleball-thane.txt', 
                                            'pc_pickleball_thane_chat.txt')
    
    # Compare media counts
    mobile_media = mobile_df[mobile_df['media'] != '']
    enhanced_media = enhanced_df[enhanced_df['media'] != '']
    
    print(f"\nStandard mobile media: {len(mobile_media)}")
    print(f"Enhanced mobile media: {len(enhanced_media)}")
    
    # Compare media type distribution
    mobile_media_types = mobile_media['media'].value_counts()
    enhanced_media_types = enhanced_media['media'].value_counts()
    
    print(f"\nStandard mobile media types:")
    for media_type, count in mobile_media_types.items():
        print(f"  {media_type}: {count}")
    
    print(f"\nEnhanced mobile media types:")
    for media_type, count in enhanced_media_types.items():
        print(f"  {media_type}: {count}")
    
    return mobile_df, enhanced_df

if __name__ == "__main__":
    mobile_df, enhanced_df = compare_enhanced_results()

#!/usr/bin/env python3
"""
Test script to verify media caption extraction
"""

import pandas as pd
from parser import parse_chat_file

def test_media_captions():
    """Test media caption extraction functionality"""
    
    # Test with the chat file
    test_file = "temp_chat.txt"
    
    try:
        # Parse the file
        master_df = parse_chat_file(test_file)
        
        # Filter media messages
        media_messages = master_df[master_df['media'] != ''].copy()
        
        print(f"📊 Total messages: {len(master_df)}")
        print(f"📱 Media messages: {len(media_messages)}")
        
        # Check for media messages with captions
        media_with_captions = media_messages[media_messages['message'] != '']
        media_without_captions = media_messages[media_messages['message'] == '']
        
        print(f"\n📋 Caption Analysis:")
        print(f"- Media with captions: {len(media_with_captions)}")
        print(f"- Media without captions: {len(media_without_captions)}")
        
        if len(media_with_captions) > 0:
            print(f"\n🔍 Sample Media Messages WITH Captions:")
            print("=" * 60)
            for idx, row in media_with_captions.head(10).iterrows():
                print(f"{row['datetime_ist_human']} | {row['sender'][:20]:20} | [{row['media'].upper()}] | Caption: '{row['message']}'")
        
        if len(media_without_captions) > 0:
            print(f"\n🔍 Sample Media Messages WITHOUT Captions:")
            print("=" * 60)
            for idx, row in media_without_captions.head(10).iterrows():
                print(f"{row['datetime_ist_human']} | {row['sender'][:20]:20} | [{row['media'].upper()}] | No caption")
        
        # Show breakdown by media type
        print(f"\n📊 Caption Breakdown by Media Type:")
        print("=" * 40)
        
        for media_type in media_messages['media'].unique():
            type_messages = media_messages[media_messages['media'] == media_type]
            with_captions = len(type_messages[type_messages['message'] != ''])
            without_captions = len(type_messages[type_messages['message'] == ''])
            total = len(type_messages)
            
            print(f"{media_type:10} | Total: {total:3} | With captions: {with_captions:3} | Without: {without_captions:3}")
        
        # Show some examples of different message types
        print(f"\n🎯 Message Type Examples:")
        print("=" * 50)
        
        # Text messages
        text_messages = master_df[(master_df['media'] == '') & (master_df['sender'] != 'group_notification')]
        if len(text_messages) > 0:
            sample = text_messages.head(3)
            print("💬 Text Messages:")
            for _, row in sample.iterrows():
                print(f"   {row['datetime_ist_human']} | {row['sender'][:20]:20} | Message: '{row['message'][:50]}...'")
        
        # Media with captions
        if len(media_with_captions) > 0:
            print("\n📱 Media with Captions:")
            sample = media_with_captions.head(3)
            for _, row in sample.iterrows():
                print(f"   {row['datetime_ist_human']} | {row['sender'][:20]:20} | [{row['media'].upper()}] Caption: '{row['message']}'")
        
        # Media without captions
        if len(media_without_captions) > 0:
            print("\n📱 Media without Captions:")
            sample = media_without_captions.head(3)
            for _, row in sample.iterrows():
                print(f"   {row['datetime_ist_human']} | {row['sender'][:20]:20} | [{row['media'].upper()}] No caption")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Media Caption Extraction")
    print("=" * 40)
    
    test_media_captions()

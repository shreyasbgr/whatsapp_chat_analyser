#!/usr/bin/env python3
"""
Test script to verify media detection functionality
"""

import pandas as pd
from parser import parse_chat_file

def test_media_detection():
    """Test and display media detection results"""
    
    # Test with the chat file
    test_file = "temp_chat.txt"
    
    try:
        # Parse the file
        master_df = parse_chat_file(test_file)
        
        # Filter media messages
        media_messages = master_df[master_df['media'] != ''].copy()
        
        print(f"📊 Total messages: {len(master_df)}")
        print(f"📱 Media messages: {len(media_messages)}")
        print(f"💬 Text messages: {len(master_df) - len(media_messages)}")
        
        if len(media_messages) > 0:
            print(f"\n📋 Media Type Breakdown:")
            print("=" * 30)
            
            media_counts = media_messages['media'].value_counts()
            for media_type, count in media_counts.items():
                print(f"• {media_type}: {count}")
            
            print(f"\n🔍 Sample Media Messages:")
            print("=" * 50)
            
            for idx, row in media_messages.head(10).iterrows():
                print(f"{row['datetime_ist_human']} | {row['sender'][:20]:20} | [{row['media'].upper()}]")
            
            # Show mixed content (text + media) from a specific user
            user_messages = master_df[master_df['sender'] != 'group_notification'].copy()
            if len(user_messages) > 0:
                # Find a user with both text and media
                for user in user_messages['sender'].unique()[:5]:
                    user_data = user_messages[user_messages['sender'] == user]
                    text_count = len(user_data[user_data['media'] == ''])
                    media_count = len(user_data[user_data['media'] != ''])
                    
                    if text_count > 0 and media_count > 0:
                        print(f"\n👤 Sample from {user}:")
                        print(f"   Text messages: {text_count}, Media messages: {media_count}")
                        sample = user_data[['datetime_ist_human', 'message', 'media']].head(5)
                        for _, row in sample.iterrows():
                            content = f"[{row['media'].upper()}]" if row['media'] else row['message'][:50]
                            print(f"   {row['datetime_ist_human']}: {content}")
                        break
                
        else:
            print("No media messages found.")
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Media Detection")
    print("=" * 30)
    
    test_media_detection()

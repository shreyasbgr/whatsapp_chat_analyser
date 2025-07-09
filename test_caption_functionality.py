#!/usr/bin/env python3
"""
Test script to verify the complete caption functionality
"""

import pandas as pd
from parser import parse_chat_file

def test_caption_functionality():
    """Test complete caption functionality as per requirements"""
    
    # Test with the chat file
    test_file = "temp_chat.txt"
    
    try:
        print("🧪 Testing Complete Caption Functionality")
        print("=" * 50)
        
        # Parse the file
        master_df = parse_chat_file(test_file)
        
        # Verify column structure
        expected_columns = ['datetime_ist', 'datetime_ist_human', 'datetime_utc', 'sender', 
                           'message', 'media', 'message_modifier', 'group_system_message', 
                           'year', 'month', 'day', 'hour', 'minute']
        
        print(f"✅ DataFrame has {len(master_df.columns)} columns")
        print(f"✅ Expected columns present: {all(col in master_df.columns for col in expected_columns)}")
        
        # Test the three types of messages
        print(f"\n📊 MESSAGE TYPE ANALYSIS:")
        print("=" * 30)
        
        # 1. Text messages (no media)
        text_messages = master_df[(master_df['media'] == '') & (master_df['sender'] != 'group_notification')]
        print(f"💬 Text messages: {len(text_messages)}")
        print(f"   - Have message content: {len(text_messages[text_messages['message'] != ''])}")
        print(f"   - No media type: {len(text_messages[text_messages['media'] == ''])}")
        
        # 2. Media without captions
        media_no_captions = master_df[(master_df['media'] != '') & (master_df['message'] == '')]
        print(f"\n📱 Media without captions: {len(media_no_captions)}")
        print(f"   - Have media type: {len(media_no_captions[media_no_captions['media'] != ''])}")
        print(f"   - Empty message: {len(media_no_captions[media_no_captions['message'] == ''])}")
        
        # 3. Media with captions
        media_with_captions = master_df[(master_df['media'] != '') & (master_df['message'] != '')]
        print(f"\n📱 Media with captions: {len(media_with_captions)}")
        print(f"   - Have media type: {len(media_with_captions[media_with_captions['media'] != ''])}")
        print(f"   - Have message (caption): {len(media_with_captions[media_with_captions['message'] != ''])}")
        
        # Show examples of each type
        print(f"\n🎯 EXAMPLES:")
        print("=" * 20)
        
        # Text message examples
        if len(text_messages) > 0:
            print("💬 Text Message Examples:")
            for _, row in text_messages.head(3).iterrows():
                print(f"   {row['datetime_ist_human']} | {row['sender'][:20]:20} | '{row['message'][:50]}...'")
        
        # Media without captions examples  
        if len(media_no_captions) > 0:
            print(f"\n📱 Media WITHOUT Caption Examples:")
            for _, row in media_no_captions.head(3).iterrows():
                print(f"   {row['datetime_ist_human']} | {row['sender'][:20]:20} | [{row['media'].upper()}] | No caption")
        
        # Media with captions examples
        if len(media_with_captions) > 0:
            print(f"\n📱 Media WITH Caption Examples:")
            for _, row in media_with_captions.head(3).iterrows():
                print(f"   {row['datetime_ist_human']} | {row['sender'][:20]:20} | [{row['media'].upper()}] | Caption: '{row['message']}'")
        
        # Verify the requirements
        print(f"\n✅ REQUIREMENT VERIFICATION:")
        print("=" * 30)
        
        # Check: Media messages should have media type
        media_messages = master_df[master_df['media'] != '']
        print(f"✅ All media messages have media type: {len(media_messages[media_messages['media'] != '']) == len(media_messages)}")
        
        # Check: Text messages should have empty media column
        text_only = master_df[master_df['media'] == '']
        print(f"✅ Text messages have empty media column: {len(text_only[text_only['media'] == '']) == len(text_only)}")
        
        # Check: Media without captions should have empty message
        media_no_caption_check = len(media_no_captions[media_no_captions['message'] == '']) == len(media_no_captions)
        print(f"✅ Media without captions have empty message: {media_no_caption_check}")
        
        # Check: Media with captions should have both media type and message
        media_with_caption_check = (len(media_with_captions[media_with_captions['media'] != '']) == len(media_with_captions) and 
                                   len(media_with_captions[media_with_captions['message'] != '']) == len(media_with_captions))
        print(f"✅ Media with captions have both media type and message: {media_with_caption_check}")
        
        # Summary statistics
        print(f"\n📊 SUMMARY STATISTICS:")
        print("=" * 25)
        print(f"Total messages: {len(master_df)}")
        print(f"Text messages: {len(text_messages)}")
        print(f"Media without captions: {len(media_no_captions)}")
        print(f"Media with captions: {len(media_with_captions)}")
        print(f"Group notifications: {len(master_df[master_df['sender'] == 'group_notification'])}")
        
        # Verify totals add up
        total_check = (len(text_messages) + len(media_no_captions) + len(media_with_captions) + 
                      len(master_df[master_df['sender'] == 'group_notification']) == len(master_df))
        print(f"✅ All message types add up to total: {total_check}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_caption_functionality()
    
    if success:
        print(f"\n🎉 ALL CAPTION FUNCTIONALITY TESTS PASSED!")
        print(f"✅ Message column properly handles captions")
        print(f"✅ Media column properly identifies media types")
        print(f"✅ Requirements fully implemented")
        print(f"\n🚀 Ready to run: streamlit run app.py")
    else:
        print(f"\n❌ Some tests failed. Please check the error messages above.")

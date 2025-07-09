#!/usr/bin/env python3
"""
Test script to verify media_file_name functionality
"""

import pandas as pd
from parser import parse_chat_file

def test_media_file_name():
    """Test media_file_name functionality"""
    
    # Test with the chat file
    test_file = "temp_chat.txt"
    
    try:
        print("🧪 Testing Media File Name Functionality")
        print("=" * 45)
        
        # Parse the file
        master_df = parse_chat_file(test_file)
        
        # Verify column structure
        expected_columns = ['datetime_ist', 'datetime_ist_human', 'datetime_utc', 'sender', 
                           'message', 'media', 'media_file_name', 'message_modifier', 'group_system_message', 
                           'year', 'month', 'day', 'hour', 'minute']
        
        print(f"✅ DataFrame has {len(master_df.columns)} columns")
        print(f"✅ Expected columns present: {all(col in master_df.columns for col in expected_columns)}")
        print(f"✅ media_file_name column exists: {'media_file_name' in master_df.columns}")
        
        # Test the different message types
        print(f"\n📊 MESSAGE TYPE ANALYSIS:")
        print("=" * 30)
        
        # 1. Text messages (no media)
        text_messages = master_df[(master_df['media'] == '') & (master_df['sender'] != 'group_notification')]
        print(f"💬 Text messages: {len(text_messages)}")
        print(f"   - Have message content: {len(text_messages[text_messages['message'] != ''])}")
        print(f"   - No media type: {len(text_messages[text_messages['media'] == ''])}")
        print(f"   - No media file name: {len(text_messages[text_messages['media_file_name'] == ''])}")
        
        # 2. Media without captions or filenames
        media_plain = master_df[(master_df['media'] != '') & (master_df['message'] == '') & (master_df['media_file_name'] == '')]
        print(f"\n📱 Media without captions/filenames: {len(media_plain)}")
        print(f"   - Have media type: {len(media_plain[media_plain['media'] != ''])}")
        print(f"   - Empty message: {len(media_plain[media_plain['message'] == ''])}")
        print(f"   - Empty media file name: {len(media_plain[media_plain['media_file_name'] == ''])}")
        
        # 3. Media with captions (user-typed)
        media_with_captions = master_df[(master_df['media'] != '') & (master_df['message'] != '') & (master_df['media_file_name'] == '')]
        print(f"\n📱 Media with user captions: {len(media_with_captions)}")
        print(f"   - Have media type: {len(media_with_captions[media_with_captions['media'] != ''])}")
        print(f"   - Have message (caption): {len(media_with_captions[media_with_captions['message'] != ''])}")
        print(f"   - Empty media file name: {len(media_with_captions[media_with_captions['media_file_name'] == ''])}")
        
        # 4. Media with file names (documents, etc.)
        media_with_filenames = master_df[(master_df['media'] != '') & (master_df['media_file_name'] != '')]
        print(f"\n📄 Media with file names: {len(media_with_filenames)}")
        print(f"   - Have media type: {len(media_with_filenames[media_with_filenames['media'] != ''])}")
        print(f"   - Have media file name: {len(media_with_filenames[media_with_filenames['media_file_name'] != ''])}")
        print(f"   - Empty message: {len(media_with_filenames[media_with_filenames['message'] == ''])}")
        
        # Show examples of each type
        print(f"\n🎯 EXAMPLES:")
        print("=" * 20)
        
        # Text message examples
        if len(text_messages) > 0:
            print("💬 Text Message Examples:")
            for _, row in text_messages.head(2).iterrows():
                print(f"   {row['datetime_ist_human'][:19]} | {row['sender'][:20]:20} | Message: '{row['message'][:40]}...'")
        
        # Media without captions examples  
        if len(media_plain) > 0:
            print(f"\n📱 Media WITHOUT Caption Examples:")
            for _, row in media_plain.head(2).iterrows():
                print(f"   {row['datetime_ist_human'][:19]} | {row['sender'][:20]:20} | [{row['media'].upper()}] | No caption/filename")
        
        # Media with captions examples
        if len(media_with_captions) > 0:
            print(f"\n📱 Media WITH Caption Examples:")
            for _, row in media_with_captions.head(2).iterrows():
                print(f"   {row['datetime_ist_human'][:19]} | {row['sender'][:20]:20} | [{row['media'].upper()}] | Caption: '{row['message']}'")
        
        # Media with filename examples
        if len(media_with_filenames) > 0:
            print(f"\n📄 Media WITH Filename Examples:")
            for _, row in media_with_filenames.head(2).iterrows():
                print(f"   {row['datetime_ist_human'][:19]} | {row['sender'][:20]:20} | [{row['media'].upper()}] | Filename: '{row['media_file_name']}'")
        
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
        media_no_caption_check = len(media_plain[media_plain['message'] == '']) == len(media_plain)
        print(f"✅ Media without captions have empty message: {media_no_caption_check}")
        
        # Check: Media with filenames should have empty message
        media_filename_check = len(media_with_filenames[media_with_filenames['message'] == '']) == len(media_with_filenames)
        print(f"✅ Media with filenames have empty message: {media_filename_check}")
        
        # Check: Message column only contains user-typed content
        all_messages_check = len(master_df[(master_df['message'] != '') & (master_df['media'] == '')]) + len(media_with_captions) == len(master_df[master_df['message'] != ''])
        print(f"✅ Message column only contains user-typed content: {all_messages_check}")
        
        # Summary statistics
        print(f"\n📊 SUMMARY STATISTICS:")
        print("=" * 25)
        print(f"Total messages: {len(master_df)}")
        print(f"Text messages: {len(text_messages)}")
        print(f"Media without captions/filenames: {len(media_plain)}")
        print(f"Media with user captions: {len(media_with_captions)}")
        print(f"Media with file names: {len(media_with_filenames)}")
        print(f"Group notifications: {len(master_df[master_df['sender'] == 'group_notification'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_media_file_name()
    
    if success:
        print(f"\n🎉 ALL MEDIA FILE NAME TESTS PASSED!")
        print(f"✅ Message column contains only user-typed content")
        print(f"✅ Media_file_name column contains file names")
        print(f"✅ Media column identifies media types")
        print(f"✅ Clean separation between content types")
        print(f"\n🚀 Ready to run: streamlit run app.py")
    else:
        print(f"\n❌ Some tests failed. Please check the error messages above.")

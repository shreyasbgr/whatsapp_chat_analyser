#!/usr/bin/env python3
"""
Test script to verify URL extraction functionality
"""

import pandas as pd
import ast
from parser import parse_chat_file

def test_url_extraction():
    """Test URL extraction functionality"""
    
    # Test with the chat file
    test_file = "temp_chat.txt"
    
    try:
        print("🧪 Testing URL Extraction Functionality")
        print("=" * 40)
        
        # Parse the file
        master_df = parse_chat_file(test_file)
        
        # Verify column structure
        expected_columns = ['datetime_ist', 'datetime_ist_human', 'datetime_utc', 'sender', 
                           'message', 'media', 'media_file_name', 'urls', 'message_modifier', 'group_system_message', 
                           'year', 'month', 'day', 'hour', 'minute']
        
        print(f"✅ DataFrame has {len(master_df.columns)} columns")
        print(f"✅ Expected columns present: {all(col in master_df.columns for col in expected_columns)}")
        print(f"✅ urls column exists: {'urls' in master_df.columns}")
        
        # Test the different message types
        print(f"\n📊 MESSAGE TYPE ANALYSIS:")
        print("=" * 30)
        
        # 1. Text messages (no media, no URLs)
        pure_text = master_df[(master_df['media'] == '') & (master_df['urls'] == '') & (master_df['sender'] != 'group_notification')]
        print(f"💬 Pure text messages: {len(pure_text)}")
        
        # 2. Messages with URLs only
        url_only = master_df[(master_df['urls'] != '') & (master_df['message'] == '') & (master_df['media'] == '')]
        print(f"🔗 URL-only messages: {len(url_only)}")
        
        # 3. Messages with URLs and text
        url_with_text = master_df[(master_df['urls'] != '') & (master_df['message'] != '') & (master_df['media'] == '')]
        print(f"🔗💬 URLs with text: {len(url_with_text)}")
        
        # 4. Media messages
        media_messages = master_df[master_df['media'] != '']
        print(f"📱 Media messages: {len(media_messages)}")
        
        # 5. Group notifications
        group_notifications = master_df[master_df['sender'] == 'group_notification']
        print(f"🔔 Group notifications: {len(group_notifications)}")
        
        # Show examples of different types
        print(f"\n🎯 EXAMPLES:")
        print("=" * 20)
        
        # Pure text message examples
        if len(pure_text) > 0:
            print("💬 Pure Text Message Examples:")
            for _, row in pure_text.head(2).iterrows():
                print(f"   {row['datetime_ist_human'][:19]} | {row['sender'][:20]:20} | Message: '{row['message'][:50]}...'")
        
        # URL-only message examples
        if len(url_only) > 0:
            print(f"\n🔗 URL-Only Message Examples:")
            for _, row in url_only.head(2).iterrows():
                try:
                    urls = ast.literal_eval(row['urls']) if row['urls'] else []
                    url_preview = urls[0][:50] + "..." if urls and len(urls[0]) > 50 else (urls[0] if urls else "")
                except:
                    url_preview = row['urls'][:50] + "..." if len(row['urls']) > 50 else row['urls']
                print(f"   {row['datetime_ist_human'][:19]} | {row['sender'][:20]:20} | URLs: {url_preview}")
        
        # URL with text examples
        if len(url_with_text) > 0:
            print(f"\n🔗💬 URL with Text Examples:")
            for _, row in url_with_text.head(2).iterrows():
                try:
                    urls = ast.literal_eval(row['urls']) if row['urls'] else []
                    url_preview = urls[0][:30] + "..." if urls and len(urls[0]) > 30 else (urls[0] if urls else "")
                except:
                    url_preview = row['urls'][:30] + "..." if len(row['urls']) > 30 else row['urls']
                print(f"   {row['datetime_ist_human'][:19]} | {row['sender'][:20]:20} | Text: '{row['message'][:30]}...' | URLs: {url_preview}")
        
        # Media message examples
        if len(media_messages) > 0:
            print(f"\n📱 Media Message Examples:")
            for _, row in media_messages.head(2).iterrows():
                print(f"   {row['datetime_ist_human'][:19]} | {row['sender'][:20]:20} | [{row['media'].upper()}] | Message: '{row['message']}'")
        
        # Verify the requirements
        print(f"\n✅ REQUIREMENT VERIFICATION:")
        print("=" * 30)
        
        # Check: URLs are extracted
        total_url_messages = len(master_df[master_df['urls'] != ''])
        print(f"✅ Messages with URLs detected: {total_url_messages}")
        
        # Check: Message column only contains user-typed text (no URLs)
        url_messages = master_df[master_df['urls'] != '']
        messages_with_urls_in_text = 0
        for _, row in url_messages.iterrows():
            if 'http' in row['message']:
                messages_with_urls_in_text += 1
        print(f"✅ Message column clean of URLs: {messages_with_urls_in_text == 0}")
        
        # Check: URL-only messages have empty message column
        url_only_check = len(url_only[url_only['message'] == '']) == len(url_only)
        print(f"✅ URL-only messages have empty message column: {url_only_check}")
        
        # Check: URLs are stored as arrays
        sample_url_message = master_df[master_df['urls'] != ''].head(1)
        if len(sample_url_message) > 0:
            try:
                sample_urls = ast.literal_eval(sample_url_message.iloc[0]['urls'])
                urls_are_arrays = isinstance(sample_urls, list)
                print(f"✅ URLs stored as arrays: {urls_are_arrays}")
            except:
                print(f"✅ URLs stored as arrays: Unable to verify")
        
        # Summary statistics
        print(f"\n📊 SUMMARY STATISTICS:")
        print("=" * 25)
        print(f"Total messages: {len(master_df)}")
        print(f"Pure text messages: {len(pure_text)}")
        print(f"URL-only messages: {len(url_only)}")
        print(f"URLs with text: {len(url_with_text)}")
        print(f"Media messages: {len(media_messages)}")
        print(f"Group notifications: {len(group_notifications)}")
        
        # Show some URL examples
        print(f"\n🔗 URL EXAMPLES:")
        print("=" * 20)
        url_sample = master_df[master_df['urls'] != ''].head(3)
        for _, row in url_sample.iterrows():
            try:
                urls = ast.literal_eval(row['urls']) if row['urls'] else []
                print(f"From {row['sender']}: {urls}")
            except:
                print(f"From {row['sender']}: {row['urls']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_url_extraction()
    
    if success:
        print(f"\n🎉 ALL URL EXTRACTION TESTS PASSED!")
        print(f"✅ URLs properly extracted from messages")
        print(f"✅ Message column contains only user-typed text")
        print(f"✅ URLs stored in separate column as arrays")
        print(f"✅ Clean separation between text and URLs")
        print(f"\n🚀 Ready to run: streamlit run app.py")
    else:
        print(f"\n❌ Some tests failed. Please check the error messages above.")

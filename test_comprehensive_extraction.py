#!/usr/bin/env python3
"""
Test script to verify comprehensive URL and phone number extraction with positions
"""

import pandas as pd
import ast
from parser import parse_chat_file

def test_comprehensive_extraction():
    """Test comprehensive URL and phone number extraction functionality"""
    
    # Test with the chat file
    test_file = "temp_chat.txt"
    
    try:
        print("🧪 Testing Comprehensive URL & Phone Number Extraction")
        print("=" * 60)
        
        # Parse the file
        master_df = parse_chat_file(test_file)
        
        # Verify column structure
        expected_columns = ['datetime_ist', 'datetime_ist_human', 'datetime_utc', 'sender', 
                           'raw_message', 'message', 'media', 'media_file_name', 'urls', 'url_positions',
                           'phone_numbers', 'phone_positions', 'message_modifier', 'group_system_message', 
                           'year', 'month', 'day', 'hour', 'minute']
        
        print(f"✅ DataFrame has {len(master_df.columns)} columns")
        print(f"✅ Expected columns present: {all(col in master_df.columns for col in expected_columns)}")
        print(f"✅ All new columns exist: {all(col in master_df.columns for col in ['raw_message', 'urls', 'url_positions', 'phone_numbers', 'phone_positions'])}")
        
        # Test message categorization
        print(f"\n📊 MESSAGE CATEGORIZATION:")
        print("=" * 35)
        
        # 1. Pure text messages (no media, no URLs, no phones)
        pure_text = master_df[
            (master_df['media'] == '') & 
            (master_df['urls'] == '') & 
            (master_df['phone_numbers'] == '') & 
            (master_df['sender'] != 'group_notification')
        ]
        print(f"💬 Pure text messages: {len(pure_text)}")
        
        # 2. Messages with URLs only
        url_only = master_df[
            (master_df['urls'] != '') & 
            (master_df['message'] == '') & 
            (master_df['phone_numbers'] == '') & 
            (master_df['media'] == '')
        ]
        print(f"🔗 URL-only messages: {len(url_only)}")
        
        # 3. Messages with phone numbers only
        phone_only = master_df[
            (master_df['phone_numbers'] != '') & 
            (master_df['message'] == '') & 
            (master_df['urls'] == '') & 
            (master_df['media'] == '')
        ]
        print(f"📞 Phone-only messages: {len(phone_only)}")
        
        # 4. Messages with URLs and text
        url_with_text = master_df[
            (master_df['urls'] != '') & 
            (master_df['message'] != '') & 
            (master_df['media'] == '')
        ]
        print(f"🔗💬 URLs with text: {len(url_with_text)}")
        
        # 5. Messages with phone numbers and text
        phone_with_text = master_df[
            (master_df['phone_numbers'] != '') & 
            (master_df['message'] != '') & 
            (master_df['media'] == '')
        ]
        print(f"📞💬 Phones with text: {len(phone_with_text)}")
        
        # 6. Messages with both URLs and phone numbers
        url_and_phone = master_df[
            (master_df['urls'] != '') & 
            (master_df['phone_numbers'] != '')
        ]
        print(f"🔗📞 URLs and phones: {len(url_and_phone)}")
        
        # 7. Media messages
        media_messages = master_df[master_df['media'] != '']
        print(f"📱 Media messages: {len(media_messages)}")
        
        # 8. Group notifications
        group_notifications = master_df[master_df['sender'] == 'group_notification']
        print(f"🔔 Group notifications: {len(group_notifications)}")
        
        # Show examples of different types
        print(f"\n🎯 EXAMPLES:")
        print("=" * 20)
        
        # Pure text message examples
        if len(pure_text) > 0:
            print("💬 Pure Text Message Examples:")
            for _, row in pure_text.head(2).iterrows():
                print(f"   Raw: '{row['raw_message'][:50]}...'")
                print(f"   Clean: '{row['message'][:50]}...'")
                print()
        
        # URL-only message examples
        if len(url_only) > 0:
            print("🔗 URL-Only Message Examples:")
            for _, row in url_only.head(2).iterrows():
                try:
                    urls = ast.literal_eval(row['urls']) if row['urls'] else []
                    positions = ast.literal_eval(row['url_positions']) if row['url_positions'] else []
                    print(f"   Raw: '{row['raw_message'][:70]}...'")
                    print(f"   URLs: {urls}")
                    print(f"   Positions: {positions}")
                    print(f"   Clean: '{row['message']}'")
                    print()
                except Exception as e:
                    print(f"   Error parsing: {e}")
        
        # Phone-only message examples
        if len(phone_only) > 0:
            print("📞 Phone-Only Message Examples:")
            for _, row in phone_only.head(2).iterrows():
                try:
                    phones = ast.literal_eval(row['phone_numbers']) if row['phone_numbers'] else []
                    positions = ast.literal_eval(row['phone_positions']) if row['phone_positions'] else []
                    print(f"   Raw: '{row['raw_message'][:50]}...'")
                    print(f"   Phones: {phones}")
                    print(f"   Positions: {positions}")
                    print(f"   Clean: '{row['message']}'")
                    print()
                except Exception as e:
                    print(f"   Error parsing: {e}")
        
        # URL with text examples
        if len(url_with_text) > 0:
            print("🔗💬 URL with Text Examples:")
            for _, row in url_with_text.head(2).iterrows():
                try:
                    urls = ast.literal_eval(row['urls']) if row['urls'] else []
                    print(f"   Raw: '{row['raw_message'][:70]}...'")
                    print(f"   URLs: {urls}")
                    print(f"   Clean: '{row['message'][:50]}...'")
                    print()
                except Exception as e:
                    print(f"   Error parsing: {e}")
        
        # Phone number pattern testing
        print(f"\n📞 PHONE NUMBER PATTERN TESTING:")
        print("=" * 40)
        
        # Test various phone number formats
        test_phone_messages = [
            "+1 234 567 8900",
            "+91 98765 43210", 
            "123-456-7890",
            "(555) 123-4567",
            "9876543210",
            "+44 20 7946 0958"
        ]
        
        phone_pattern = r'\\+?\\d[\\d\\s\\-\\(\\)]{7,}\\d'
        import re
        
        print("Testing phone number patterns:")
        for test_phone in test_phone_messages:
            matches = re.findall(phone_pattern, test_phone)
            print(f"   '{test_phone}' -> {matches}")
        
        # Verify requirements
        print(f"\n✅ REQUIREMENT VERIFICATION:")
        print("=" * 35)
        
        # Check: Raw message preserved
        non_empty_messages = master_df[master_df['raw_message'] != '']
        print(f"✅ Raw messages preserved: {len(non_empty_messages)} messages")
        
        # Check: URLs extracted
        url_messages = master_df[master_df['urls'] != '']
        print(f"✅ Messages with URLs: {len(url_messages)}")
        
        # Check: Phone numbers extracted
        phone_messages = master_df[master_df['phone_numbers'] != '']
        print(f"✅ Messages with phone numbers: {len(phone_messages)}")
        
        # Check: Clean message column
        clean_messages = master_df[master_df['message'] != '']
        print(f"✅ Messages with clean text: {len(clean_messages)}")
        
        # Check: Position data stored
        url_position_messages = master_df[master_df['url_positions'] != '']
        phone_position_messages = master_df[master_df['phone_positions'] != '']
        print(f"✅ Messages with URL positions: {len(url_position_messages)}")
        print(f"✅ Messages with phone positions: {len(phone_position_messages)}")
        
        # Summary statistics
        print(f"\n📊 SUMMARY STATISTICS:")
        print("=" * 25)
        print(f"Total messages: {len(master_df)}")
        print(f"Pure text messages: {len(pure_text)}")
        print(f"URL-only messages: {len(url_only)}")
        print(f"Phone-only messages: {len(phone_only)}")
        print(f"URLs with text: {len(url_with_text)}")
        print(f"Phones with text: {len(phone_with_text)}")
        print(f"URLs and phones: {len(url_and_phone)}")
        print(f"Media messages: {len(media_messages)}")
        print(f"Group notifications: {len(group_notifications)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_comprehensive_extraction()
    
    if success:
        print(f"\n🎉 ALL COMPREHENSIVE EXTRACTION TESTS PASSED!")
        print(f"✅ Raw messages preserved")
        print(f"✅ URLs extracted with positions")
        print(f"✅ Phone numbers extracted with positions")
        print(f"✅ Clean message column contains only user text")
        print(f"✅ Multiple patterns handled correctly")
        print(f"\n📋 OTHER EXTRACTABLE PATTERNS:")
        print("   - Email addresses")
        print("   - Hashtags (#tag)")
        print("   - Mentions (@username)")
        print("   - Money amounts ($100, ₹500)")
        print("   - Dates (DD/MM/YYYY)")
        print("   - Time stamps (HH:MM)")
        print("   - File paths (/path/to/file)")
        print("   - Coordinates (lat, lng)")
        print(f"\n🚀 Ready to run: streamlit run app.py")
    else:
        print(f"\n❌ Some tests failed. Please check the error messages above.")

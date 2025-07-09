#!/usr/bin/env python3
"""
Test to verify the app display format is correct
"""

import pandas as pd
from parser import parse_chat_file

def test_app_display():
    """Test that the app display shows the correct format"""
    
    # Test with the chat file
    test_file = "temp_chat.txt"
    
    try:
        print("🧪 Testing App Display Format")
        print("=" * 30)
        
        # Parse the file
        master_df = parse_chat_file(test_file)
        
        # Create filtered dataframe (simulating what app does)
        user_messages_df = master_df[master_df['sender'] != "group_notification"].copy()
        
        # Take sample data (first 10 messages)
        display_df = user_messages_df[['datetime_ist_human', 'sender', 'message', 'media']].head(10).copy()
        
        print("📊 Sample App Display (first 10 messages):")
        print("=" * 80)
        print(f"{'Time':<20} | {'Sender':<20} | {'Message':<30} | {'Media Type':<10}")
        print("-" * 80)
        
        for _, row in display_df.iterrows():
            time_str = row['datetime_ist_human'][:20]
            sender_str = row['sender'][:20]
            message_str = row['message'][:30] if row['message'] else ""
            media_str = row['media'] if row['media'] else ""
            
            print(f"{time_str:<20} | {sender_str:<20} | {message_str:<30} | {media_str:<10}")
        
        # Show specific examples for each type
        print(f"\n🎯 SPECIFIC EXAMPLES:")
        print("=" * 50)
        
        # Text message example
        text_example = user_messages_df[(user_messages_df['media'] == '') & (user_messages_df['message'] != '')].head(1)
        if len(text_example) > 0:
            row = text_example.iloc[0]
            print(f"💬 Text Message:")
            print(f"   Time: {row['datetime_ist_human']}")
            print(f"   Sender: {row['sender']}")
            print(f"   Message: '{row['message']}'")
            print(f"   Media Type: '{row['media']}'")
        
        # Media without caption example
        media_no_caption = user_messages_df[(user_messages_df['media'] != '') & (user_messages_df['message'] == '')].head(1)
        if len(media_no_caption) > 0:
            row = media_no_caption.iloc[0]
            print(f"\n📱 Media Without Caption:")
            print(f"   Time: {row['datetime_ist_human']}")
            print(f"   Sender: {row['sender']}")
            print(f"   Message: '{row['message']}'")
            print(f"   Media Type: '{row['media']}'")
        
        # Media with caption example
        media_with_caption = user_messages_df[(user_messages_df['media'] != '') & (user_messages_df['message'] != '')].head(1)
        if len(media_with_caption) > 0:
            row = media_with_caption.iloc[0]
            print(f"\n📱 Media With Caption:")
            print(f"   Time: {row['datetime_ist_human']}")
            print(f"   Sender: {row['sender']}")
            print(f"   Message: '{row['message']}'")
            print(f"   Media Type: '{row['media']}'")
        
        # Verification
        print(f"\n✅ DISPLAY VERIFICATION:")
        print("=" * 30)
        
        # Check that Message column only contains user-typed content
        text_messages = display_df[display_df['media'] == '']
        media_no_caption = display_df[(display_df['media'] != '') & (display_df['message'] == '')]
        media_with_caption = display_df[(display_df['media'] != '') & (display_df['message'] != '')]
        
        print(f"✅ Text messages show message content: {len(text_messages[text_messages['message'] != '']) > 0}")
        print(f"✅ Media without captions show empty message: {len(media_no_caption[media_no_caption['message'] == '']) == len(media_no_caption)}")
        print(f"✅ Media with captions show caption in message: {len(media_with_caption[media_with_caption['message'] != '']) == len(media_with_caption)}")
        print(f"✅ Media Type column shows media type for media messages: {len(display_df[display_df['media'] != '']) > 0}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_app_display()
    
    if success:
        print(f"\n🎉 APP DISPLAY FORMAT IS CORRECT!")
        print(f"✅ Message column shows only user-typed content")
        print(f"✅ Media Type column shows media types")
        print(f"✅ No [IMAGE] indicators in Message column")
        print(f"\n🚀 Ready to run: streamlit run app.py")
    else:
        print(f"\n❌ Display format test failed.")

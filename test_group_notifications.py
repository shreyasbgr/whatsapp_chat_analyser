#!/usr/bin/env python3
"""
Test script to show what messages are classified as group notifications
"""

import pandas as pd
from parser import parse_chat_file

def test_group_notifications():
    """Test and display group notification classification"""
    
    # Test with the chat file
    test_file = "temp_chat.txt"
    
    try:
        # Parse the file
        master_df = parse_chat_file(test_file)
        
        # Filter group notifications
        group_notifications = master_df[master_df['sender'] == 'group_notification'].copy()
        
        print(f"📊 Total messages: {len(master_df)}")
        print(f"🔔 Group notifications: {len(group_notifications)}")
        print(f"👥 User messages: {len(master_df) - len(group_notifications)}")
        
        if len(group_notifications) > 0:
            print(f"\n🔍 Sample Group Notifications:")
            print("=" * 50)
            
            # Show unique types of group notifications
            unique_messages = group_notifications['message'].value_counts()
            
            for message, count in unique_messages.head(10).items():
                print(f"• {message[:80]}{'...' if len(message) > 80 else ''} ({count} times)")
            
            print(f"\n📋 Full Group Notifications (first 20):")
            print("=" * 50)
            
            for idx, row in group_notifications.head(20).iterrows():
                print(f"{row['datetime_ist_human']} - {row['message'][:100]}{'...' if len(row['message']) > 100 else ''}")
                
        else:
            print("No group notifications found.")
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Group Notification Classification")
    print("=" * 50)
    
    test_group_notifications()

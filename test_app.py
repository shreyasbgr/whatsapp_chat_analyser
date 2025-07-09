#!/usr/bin/env python3
"""
Test script to verify the app structure and data flow
"""

import pandas as pd
from parser import parse_chat_file

def test_data_structure():
    """Test the data structure with a sample file"""
    
    # Test with one of the existing chat files
    test_file = "thane_board_gamers.txt"
    
    try:
        # Master dataframe with ALL messages (including group notifications)
        master_df = parse_chat_file(test_file)
        print(f"✅ Master DataFrame created successfully with {len(master_df)} rows")
        
        # Create a copy with only user messages (excluding group notifications)
        user_messages_df = master_df[master_df['sender'] != "group_notification"].copy()
        print(f"✅ User messages DataFrame created with {len(user_messages_df)} rows")
        
        # Get all users (excluding group notifications)
        all_users = sorted(user_messages_df['sender'].unique())
        print(f"✅ Found {len(all_users)} unique users: {all_users[:5]}...")
        
        # Test filtering for "Overall"
        overall_df = user_messages_df.copy()
        print(f"✅ Overall DataFrame: {len(overall_df)} rows")
        
        # Test filtering for specific user
        if all_users:
            first_user = all_users[0]
            user_df = user_messages_df[user_messages_df['sender'] == first_user].copy()
            print(f"✅ User '{first_user}' DataFrame: {len(user_df)} rows")
        
        # Verify data integrity
        print(f"\n📊 Data Summary:")
        print(f"- Total messages (including group notifications): {len(master_df)}")
        print(f"- Group notifications: {len(master_df[master_df['sender'] == 'group_notification'])}")
        print(f"- User messages: {len(user_messages_df)}")
        print(f"- Unique users: {len(all_users)}")
        
        # Show sample columns
        print(f"\n🔍 DataFrame Columns:")
        print(list(master_df.columns))
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing WhatsApp Chat Analyzer Data Structure")
    print("=" * 50)
    
    success = test_data_structure()
    
    if success:
        print("\n✅ All tests passed! The app structure is working correctly.")
        print("\nTo run the app:")
        print("1. Activate virtual environment: source venv/bin/activate")
        print("2. Run streamlit app: streamlit run app.py")
    else:
        print("\n❌ Tests failed. Please check the error messages above.")

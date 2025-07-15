#!/usr/bin/env python3
"""
Compare parsing results between PC and mobile formats to identify discrepancies
"""

import pandas as pd
from parser import parse_chat_file
import sys

def analyze_parsing_differences(pc_file, mobile_file):
    """Analyze differences between PC and mobile parsing results."""
    
    print("🔍 Analyzing parsing differences between PC and mobile formats...")
    
    # Parse both files
    print("\n📱 Parsing mobile format...")
    mobile_df = parse_chat_file(mobile_file)
    
    print("\n💻 Parsing PC format...")
    pc_df = parse_chat_file(pc_file)
    
    print("\n📊 Comparison Results:")
    print("=" * 60)
    
    # Basic statistics comparison
    stats = [
        ("Total Messages", len(mobile_df), len(pc_df)),
        ("Media Messages", len(mobile_df[mobile_df['media'] != '']), len(pc_df[pc_df['media'] != ''])),
        ("Group Notifications", len(mobile_df[mobile_df['sender'] == 'group_notification']), len(pc_df[pc_df['sender'] == 'group_notification'])),
        ("Unique Senders", mobile_df['sender'].nunique(), pc_df['sender'].nunique()),
    ]
    
    for stat_name, mobile_val, pc_val in stats:
        diff = pc_val - mobile_val
        print(f"{stat_name:20} | Mobile: {mobile_val:6} | PC: {pc_val:6} | Diff: {diff:+4}")
    
    # Word count analysis
    mobile_words = mobile_df['message'].str.split().str.len().sum()
    pc_words = pc_df['message'].str.split().str.len().sum()
    word_diff = pc_words - mobile_words
    print(f"{'Total Words':20} | Mobile: {mobile_words:6} | PC: {pc_words:6} | Diff: {word_diff:+4}")
    
    # Contact analysis
    mobile_contacts = mobile_df['phone_numbers'].str.len().sum()
    pc_contacts = pc_df['phone_numbers'].str.len().sum()
    contact_diff = pc_contacts - mobile_contacts
    print(f"{'Contact Count':20} | Mobile: {mobile_contacts:6} | PC: {pc_contacts:6} | Diff: {contact_diff:+4}")
    
    # Emoji analysis
    mobile_emojis = mobile_df['emojis'].str.len().sum()
    pc_emojis = pc_df['emojis'].str.len().sum()
    emoji_diff = pc_emojis - mobile_emojis
    print(f"{'Emoji Count':20} | Mobile: {mobile_emojis:6} | PC: {pc_emojis:6} | Diff: {emoji_diff:+4}")
    
    # Find message differences
    print("\n🔍 Analyzing message content differences:")
    
    # Sample messages that might be different
    if len(mobile_df) != len(pc_df):
        print(f"⚠️  Row count difference: Mobile has {len(mobile_df)}, PC has {len(pc_df)}")
        
        # Check for duplicate messages in PC
        pc_duplicates = pc_df[pc_df.duplicated(subset=['datetime_ist', 'sender', 'message'], keep=False)]
        if len(pc_duplicates) > 0:
            print(f"🔄 PC has {len(pc_duplicates)} duplicate messages")
            print("Sample duplicates:")
            print(pc_duplicates[['datetime_ist_human', 'sender', 'message']].head())
    
    # Check for media type differences
    mobile_media_types = mobile_df['media'].value_counts()
    pc_media_types = pc_df['media'].value_counts()
    
    print("\n📺 Media type comparison:")
    all_media_types = set(mobile_media_types.index) | set(pc_media_types.index)
    for media_type in sorted(all_media_types):
        mobile_count = mobile_media_types.get(media_type, 0)
        pc_count = pc_media_types.get(media_type, 0)
        diff = pc_count - mobile_count
        if diff != 0:
            print(f"  {media_type:15} | Mobile: {mobile_count:4} | PC: {pc_count:4} | Diff: {diff:+3}")
    
    # Check for sender differences
    mobile_senders = set(mobile_df['sender'].unique())
    pc_senders = set(pc_df['sender'].unique())
    
    if mobile_senders != pc_senders:
        print(f"\n👥 Sender differences:")
        only_mobile = mobile_senders - pc_senders
        only_pc = pc_senders - mobile_senders
        
        if only_mobile:
            print(f"  Only in mobile: {only_mobile}")
        if only_pc:
            print(f"  Only in PC: {only_pc}")
    
    # Sample of high word count messages
    print("\n📝 Messages with high word counts (top 5):")
    print("Mobile format:")
    mobile_word_counts = mobile_df['message'].str.split().str.len()
    top_mobile = mobile_df.loc[mobile_word_counts.nlargest(5).index]
    for _, row in top_mobile.iterrows():
        words = len(row['message'].split())
        print(f"  {words:3} words | {row['sender'][:20]:20} | {row['message'][:60]}...")
    
    print("\nPC format:")
    pc_word_counts = pc_df['message'].str.split().str.len()
    top_pc = pc_df.loc[pc_word_counts.nlargest(5).index]
    for _, row in top_pc.iterrows():
        words = len(row['message'].split())
        print(f"  {words:3} words | {row['sender'][:20]:20} | {row['message'][:60]}...")
    
    return mobile_df, pc_df

def main():
    if len(sys.argv) != 3:
        print("Usage: python compare_formats.py <pc_file> <mobile_file>")
        sys.exit(1)
    
    pc_file = sys.argv[1]
    mobile_file = sys.argv[2]
    
    mobile_df, pc_df = analyze_parsing_differences(pc_file, mobile_file)

if __name__ == "__main__":
    main()

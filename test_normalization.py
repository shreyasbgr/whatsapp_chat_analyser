#!/usr/bin/env python3

from parser import parse_chat_file

def test_contact_normalization():
    """Test that contact normalization produces consistent results between PC and mobile."""
    
    print("Testing contact normalization...")
    
    # Parse both files
    pc_df = parse_chat_file('pc_pickleball_thane_chat.txt')
    mobile_df = parse_chat_file('mobile-pickleball-thane.txt')
    
    # Get unique contacts
    pc_contacts = set(pc_df[pc_df['sender'] != 'group_notification']['sender'].unique())
    mobile_contacts = set(mobile_df[mobile_df['sender'] != 'group_notification']['sender'].unique())
    
    # Compare counts
    print(f"PC contacts: {len(pc_contacts)}")
    print(f"Mobile contacts: {len(mobile_contacts)}")
    print(f"Same count: {len(pc_contacts) == len(mobile_contacts)}")
    
    # Compare media messages
    pc_media = len(pc_df[pc_df['media'] != ''])
    mobile_media = len(mobile_df[mobile_df['media'] != ''])
    print(f"PC media messages: {pc_media}")
    print(f"Mobile media messages: {mobile_media}")
    
    # Compare contact messages
    pc_contact_msgs = len(pc_df[pc_df['media'] == 'contact'])
    mobile_contact_msgs = len(mobile_df[mobile_df['media'] == 'contact'])
    print(f"PC contact messages: {pc_contact_msgs}")
    print(f"Mobile contact messages: {mobile_contact_msgs}")
    print(f"Same contact message count: {pc_contact_msgs == mobile_contact_msgs}")
    
    # Test phone number normalization
    test_numbers = [
        "+1 (202) 746‑4586",  # with en-dash
        "+1 (202) 746-4586",  # with regular dash  
        "+91 91 364 019 21",  # with spaces
        "+91 91364 01921",    # without spaces
        "~Sunita",            # with tilde
        "Sunita"              # without tilde
    ]
    
    print("\nPhone number normalization test:")
    for num in test_numbers:
        from parser import normalize_contact_name
        normalized = normalize_contact_name(num)
        print(f"  '{num}' -> '{normalized}'")
    
    return pc_contacts, mobile_contacts

if __name__ == "__main__":
    test_contact_normalization()

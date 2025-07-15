#!/usr/bin/env python3
"""
Compare contact messages between PC and mobile WhatsApp parsing outputs.
This script will help identify why mobile parsing shows fewer contacts than PC.
"""

import json
from datetime import timedelta
from parser import parse_chat_file

def parse_whatsapp_chat(file_path):
    """Wrapper function to parse WhatsApp chat and return dict with messages and contacts."""
    df = parse_chat_file(file_path)
    
    # Convert DataFrame to list of dictionaries
    messages = df.to_dict('records')
    
    # Extract unique contacts (senders)
    contacts = df[df['sender'] != 'group_notification']['sender'].unique().tolist()
    
    return {
        'messages': messages,
        'contacts': contacts
    }

def compare_contact_messages():
    """Compare contact messages between PC and mobile parsing outputs."""
    
    # Parse both files using the unified parser
    print("Parsing PC chat...")
    try:
        pc_result = parse_whatsapp_chat('pc_pickleball_thane_chat.txt')
        pc_messages = pc_result['messages']
        pc_contacts_list = pc_result['contacts']
    except FileNotFoundError:
        print("PC chat file not found!")
        return
    
    print("Parsing mobile chat...")
    try:
        mobile_result = parse_whatsapp_chat('mobile-pickleball-thane.txt')
        mobile_messages = mobile_result['messages']
        mobile_contacts_list = mobile_result['contacts']
    except FileNotFoundError:
        print("Mobile chat file not found!")
        return
    
    # Extract contact messages
    pc_contacts = [msg for msg in pc_messages if msg.get('media') == 'contact']
    mobile_contacts = [msg for msg in mobile_messages if msg.get('media') == 'contact']
    
    print(f"\nSummary:")
    print(f"PC total messages: {len(pc_messages)}")
    print(f"Mobile total messages: {len(mobile_messages)}")
    print(f"PC contact messages: {len(pc_contacts)}")
    print(f"Mobile contact messages: {len(mobile_contacts)}")
    print(f"Contact difference: {len(pc_contacts) - len(mobile_contacts)}")
    
    # Compare contact lists (unique senders)
    print(f"\nContact List Comparison:")
    print(f"PC unique contacts: {len(pc_contacts_list)}")
    print(f"Mobile unique contacts: {len(mobile_contacts_list)}")
    print(f"Contact list difference: {len(pc_contacts_list) - len(mobile_contacts_list)}")
    
    # Find differences in contact lists
    pc_contacts_set = set(pc_contacts_list)
    mobile_contacts_set = set(mobile_contacts_list)
    
    pc_only_contacts = pc_contacts_set - mobile_contacts_set
    mobile_only_contacts = mobile_contacts_set - pc_contacts_set
    common_contacts = pc_contacts_set & mobile_contacts_set
    
    print(f"\nContact List Details:")
    print(f"Common contacts: {len(common_contacts)}")
    print(f"PC-only contacts: {len(pc_only_contacts)}")
    print(f"Mobile-only contacts: {len(mobile_only_contacts)}")
    
    if pc_only_contacts:
        print(f"\nContacts only found in PC parsing:")
        for contact in sorted(pc_only_contacts):
            print(f"  - '{contact}'")
    
    if mobile_only_contacts:
        print(f"\nContacts only found in mobile parsing:")
        for contact in sorted(mobile_only_contacts):
            print(f"  - '{contact}'")
    
    # Show sample contact messages from each
    print(f"\nSample PC contact messages (first 5):")
    for i, msg in enumerate(pc_contacts[:5]):
        print(f"{i+1}. {msg['datetime_ist_human']} - {msg['sender']}: {msg['raw_message'][:100]}...")
    
    print(f"\nSample mobile contact messages (first 5):")
    for i, msg in enumerate(mobile_contacts[:5]):
        print(f"{i+1}. {msg['datetime_ist_human']} - {msg['sender']}: {msg['raw_message'][:100]}...")
    
    # Find messages that appear in PC but not in mobile
    print(f"\nAnalyzing discrepancies...")
    
    # Create sets of message identifiers for comparison
    pc_contact_ids = set()
    mobile_contact_ids = set()
    
    for msg in pc_contacts:
        # Use timestamp + sender + first 50 chars of raw message as identifier
        identifier = f"{msg['datetime_ist']}_{msg['sender']}_{msg['raw_message'][:50]}"
        pc_contact_ids.add(identifier)
    
    for msg in mobile_contacts:
        identifier = f"{msg['datetime_ist']}_{msg['sender']}_{msg['raw_message'][:50]}"
        mobile_contact_ids.add(identifier)
    
    # Find messages only in PC
    only_in_pc = pc_contact_ids - mobile_contact_ids
    only_in_mobile = mobile_contact_ids - pc_contact_ids
    
    print(f"Messages only detected as contacts in PC: {len(only_in_pc)}")
    print(f"Messages only detected as contacts in mobile: {len(only_in_mobile)}")
    
    # Show some examples of PC-only contact messages
    if only_in_pc:
        print(f"\nExamples of contact messages only found in PC parsing:")
        count = 0
        for msg in pc_contacts:
            if count >= 10:  # Show max 10 examples
                break
            identifier = f"{msg['datetime_ist']}_{msg['sender']}_{msg['raw_message'][:50]}"
            if identifier in only_in_pc:
                print(f"- {msg['datetime_ist_human']} - {msg['sender']}: {msg['raw_message']}")
                count += 1
    
    # Show some examples of mobile-only contact messages
    if only_in_mobile:
        print(f"\nExamples of contact messages only found in mobile parsing:")
        count = 0
        for msg in mobile_contacts:
            if count >= 10:  # Show max 10 examples
                break
            identifier = f"{msg['datetime_ist']}_{msg['sender']}_{msg['raw_message'][:50]}"
            if identifier in only_in_mobile:
                print(f"- {msg['datetime_ist_human']} - {msg['sender']}: {msg['raw_message']}")
                count += 1
    
    # Check for patterns in messages that might be missed in mobile
    print(f"\nChecking for patterns in PC contacts that might be missed in mobile...")
    
    # Look for common patterns in PC contacts that might not be detected in mobile
    pc_contact_patterns = {}
    for msg in pc_contacts:
        raw_msg = msg['raw_message'].lower()
        # Check for common contact-related patterns
        if 'contact card' in raw_msg:
            pc_contact_patterns['contact card'] = pc_contact_patterns.get('contact card', 0) + 1
        if 'vcf' in raw_msg:
            pc_contact_patterns['vcf'] = pc_contact_patterns.get('vcf', 0) + 1
        if 'omitted' in raw_msg:
            pc_contact_patterns['omitted'] = pc_contact_patterns.get('omitted', 0) + 1
        if 'file attached' in raw_msg:
            pc_contact_patterns['file attached'] = pc_contact_patterns.get('file attached', 0) + 1
    
    mobile_contact_patterns = {}
    for msg in mobile_contacts:
        raw_msg = msg['raw_message'].lower()
        if 'contact card' in raw_msg:
            mobile_contact_patterns['contact card'] = mobile_contact_patterns.get('contact card', 0) + 1
        if 'vcf' in raw_msg:
            mobile_contact_patterns['vcf'] = mobile_contact_patterns.get('vcf', 0) + 1
        if 'omitted' in raw_msg:
            mobile_contact_patterns['omitted'] = mobile_contact_patterns.get('omitted', 0) + 1
        if 'file attached' in raw_msg:
            mobile_contact_patterns['file attached'] = mobile_contact_patterns.get('file attached', 0) + 1
    
    print(f"\nPC contact patterns:")
    for pattern, count in pc_contact_patterns.items():
        print(f"  {pattern}: {count}")
    
    print(f"\nMobile contact patterns:")
    for pattern, count in mobile_contact_patterns.items():
        print(f"  {pattern}: {count}")
    
    # Check for potential media type misclassification in mobile
    print(f"\nChecking for potential contact messages classified as other media types in mobile...")
    
    # Look for messages containing contact-related keywords but classified as other media
    potential_contacts = []
    for msg in mobile_messages:
        if msg.get('media') and msg.get('media') != 'contact':
            raw_msg = msg['raw_message'].lower()
            if any(keyword in raw_msg for keyword in ['contact card', 'vcf', '.vcf']):
                potential_contacts.append(msg)
    
    if potential_contacts:
        print(f"Found {len(potential_contacts)} potential contact messages classified as other media types:")
        for msg in potential_contacts[:10]:  # Show first 10
            print(f"  {msg['datetime_ist_human']} - {msg['sender']} - Media: {msg['media']} - {msg['raw_message'][:100]}...")
    else:
        print("No potential contact messages found classified as other media types.")

if __name__ == "__main__":
    compare_contact_messages()

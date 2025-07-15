#!/usr/bin/env python3
import re
from parser import parse_chat_file

# Test contact pattern matching directly
test_messages = [
    "Contact card omitted",
    "contact card omitted",
    "CONTACT CARD OMITTED",
    "example.vcf (file attached)",
    "John Doe.vcf (file attached)",
    "Media omitted",
    "<Media omitted>",
    "\\u003cMedia omitted\\u003e"
]

media_patterns = [
    (r"image omitted", "image"),
    (r"video omitted", "video"),
    (r"gif omitted", "gif"),
    (r"audio omitted", "audio"),
    (r"voice message omitted", "voice"),
    (r"document omitted", "document"),
    (r"sticker omitted", "sticker"),
    (r"contact card omitted", "contact"),
    (r"location omitted", "location"),
    (r"poll omitted", "poll"),
    (r"\u003cMedia omitted\u003e", "media"),
    (r"\u003cattached: .\u003e", "attachment"),
    # Additional patterns for PC format
    (r"\\u003cMedia omitted\\u003e", "media"),
    (r"\\u003cattached: .\\u003e", "attachment"),
    (r"\\u003cimage omitted\\u003e", "image"),
    (r"\\u003cvideo omitted\\u003e", "video"),
    (r"\\u003caudio omitted\\u003e", "audio"),
    (r"\\u003cdocument omitted\\u003e", "document"),
    (r"\\u003csticker omitted\\u003e", "sticker"),
    (r"\\u003cvoice message omitted\\u003e", "voice"),
    (r"\\u003cgif omitted\\u003e", "gif"),
    (r"\\u003ccontact card omitted\\u003e", "contact"),
    (r"\\u003clocation omitted\\u003e", "location"),
    (r"\\u003cpoll omitted\\u003e", "poll"),
    # File attachment patterns - PC format
    (r".*\.(pdf|doc|docx|txt|xlsx|ppt|pptx|zip|rar).*pages.*document omitted", "document"),
    (r".*\.(pdf|doc|docx|txt|xlsx|ppt|pptx|zip|rar).*document omitted", "document"),
    # File attachment patterns - Mobile format (split vcf from other files)
    (r".*\.vcf.*\(file attached\)", "contact"),
    (r".*\.(pdf|doc|docx|txt|xlsx|ppt|pptx|zip|rar).*\(file attached\)", "document"),
    # Image/media files with (file attached) pattern - Mobile format
    (r".*\.(jpg|jpeg|png|gif|bmp|webp).*\(file attached\)", "image"),
    (r".*\.(mp4|mov|avi|mkv|wmv|flv).*\(file attached\)", "video"),
    (r".*\.(mp3|wav|aac|flac|m4a|wma).*\(file attached\)", "audio"),
    # Common file attachment patterns
    (r"attached: .*\.(jpg|jpeg|png|gif|mp4|mov|pdf|doc|docx|txt|zip|rar)", "attachment"),
    (r"IMG-\d+", "image"),
    (r"VID-\d+", "video"),
    (r"AUD-\d+", "audio"),
    (r"DOC-\d+", "document")
]

print("Testing contact pattern matching:")
print("=" * 50)

for test_msg in test_messages:
    print(f"\nTesting: '{test_msg}'")
    matched = False
    for pattern, media_name in media_patterns:
        if re.search(pattern, test_msg, re.IGNORECASE):
            print(f"  ✓ Matched pattern: {pattern} -> {media_name}")
            matched = True
            break
    if not matched:
        print(f"  ✗ No pattern matched")

print("\n" + "=" * 50)
print("Now testing actual chat files:")

# Test with actual PC chat file
print("\nTesting PC chat file:")
try:
    pc_data = parse_chat_file("pc_pickleball_thane_chat.txt", 5.5)
    print(f"PC data type: {type(pc_data)}")
    
    # Handle DataFrame structure
    if hasattr(pc_data, 'media'):
        pc_contact_count = len(pc_data[pc_data['media'] == 'contact'])
        pc_media_count = len(pc_data[pc_data['media'] == 'media'])
        print(f"PC format - Contact messages: {pc_contact_count}")
        print(f"PC format - Generic media messages: {pc_media_count}")
        
        # Show some examples of contact messages
        contact_messages = pc_data[pc_data['media'] == 'contact'].head(3)
        print(f"Sample PC contact messages:")
        for idx, row in contact_messages.iterrows():
            print(f"  Raw: {row['raw_message']}")
            print(f"  Media: {row['media']}")
            print()
    else:
        # Handle list of dictionaries structure
        pc_contact_count = sum(1 for msg in pc_data if msg.get('media') == 'contact')
        pc_media_count = sum(1 for msg in pc_data if msg.get('media') == 'media')
        print(f"PC format - Contact messages: {pc_contact_count}")
        print(f"PC format - Generic media messages: {pc_media_count}")
        
        # Show some examples of contact messages
        contact_messages = [msg for msg in pc_data if msg.get('media') == 'contact'][:3]
        print(f"Sample PC contact messages:")
        for msg in contact_messages:
            print(f"  Raw: {msg['raw_message']}")
            print(f"  Media: {msg['media']}")
            print()
        
except Exception as e:
    print(f"Error parsing PC file: {e}")

# Test with actual Mobile chat file
print("\nTesting Mobile chat file:")
try:
    mobile_data = parse_chat_file("mobile-pickleball-thane.txt", 5.5)
    print(f"Mobile data type: {type(mobile_data)}")
    
    # Handle DataFrame structure
    if hasattr(mobile_data, 'media'):
        mobile_contact_count = len(mobile_data[mobile_data['media'] == 'contact'])
        mobile_media_count = len(mobile_data[mobile_data['media'] == 'media'])
        print(f"Mobile format - Contact messages: {mobile_contact_count}")
        print(f"Mobile format - Generic media messages: {mobile_media_count}")
        
        # Show some examples of contact messages
        contact_messages = mobile_data[mobile_data['media'] == 'contact'].head(3)
        print(f"Sample Mobile contact messages:")
        for idx, row in contact_messages.iterrows():
            print(f"  Raw: {row['raw_message']}")
            print(f"  Media: {row['media']}")
            print()
    else:
        # Handle list of dictionaries structure
        mobile_contact_count = sum(1 for msg in mobile_data if msg.get('media') == 'contact')
        mobile_media_count = sum(1 for msg in mobile_data if msg.get('media') == 'media')
        print(f"Mobile format - Contact messages: {mobile_contact_count}")
        print(f"Mobile format - Generic media messages: {mobile_media_count}")
        
        # Show some examples of contact messages
        contact_messages = [msg for msg in mobile_data if msg.get('media') == 'contact'][:3]
        print(f"Sample Mobile contact messages:")
        for msg in contact_messages:
            print(f"  Raw: {msg['raw_message']}")
            print(f"  Media: {msg['media']}")
            print()
        
except Exception as e:
    print(f"Error parsing Mobile file: {e}")

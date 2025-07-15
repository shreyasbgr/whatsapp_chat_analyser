import re
import pandas as pd
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Union, IO, Any

# Global regex patterns used in message extraction
url_pattern = r'https?://[^\s]+'
# More specific phone number pattern to avoid matching numeric ranges
# Matches: +1234567890, (123) 456-7890, +91 98765 43210, etc.
# Avoids: 0-18 18-30, 5-10, etc.
phone_pattern = r'(?:\+\d{1,3}[\s\-]?)?(?:\(\d{1,4}\)|\d{1,4})[\s\-]?\d{3,4}[\s\-]?\d{4,}|(?:\+\d{1,3}[\s\-]?)?\d{10,15}'
email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
money_pattern = r'(?:Rs\.?|₹|\$|€|£|¥|₩|₽|₦|₨|₪|₡|₢|₣|₤|₥|₦|₧|₨|₩|₪|₫|€|₭|₮|₯|₰|₱|₲|₳|₴|₵|₶|₷|₸|₹|₺)\s*[0-9,]+(?:\.[0-9]{1,2})?|[0-9,]+(?:\.[0-9]{1,2})?\s*(?:Rs|rupees?|dollars?|euros?|pounds?|yen|won|ruble|naira|shekel|USD|EUR|GBP|INR|JPY|KRW|RUB|NGN|ILS)\b'

def clean_invisible(text: str) -> str:
    """Clean invisible Unicode characters from text and handle encoding issues."""
    if not isinstance(text, str):
        text = str(text)
    
    # First, handle Unicode surrogates and encoding issues
    try:
        # Try to encode and decode to catch problematic Unicode characters
        text.encode('utf-8')
    except UnicodeEncodeError:
        # If encoding fails, clean the text by removing problematic characters
        text = text.encode('utf-8', errors='ignore').decode('utf-8')
    
    # Remove Unicode surrogates that cause encoding issues
    # Surrogates are in range U+D800-U+DFFF
    text = re.sub(r'[\uD800-\uDFFF]', '', text)
    
    # Remove other problematic Unicode characters that might cause issues
    text = re.sub(r'[\uFDD0-\uFDEF]', '', text)  # Non-characters
    text = re.sub(r'[\uFFFE\uFFFF]', '', text)    # Non-characters
    
    # Remove various Unicode directional and formatting characters
    text = text.replace('\u200e', '')  # Left-to-right mark
    text = text.replace('\u202f', '')  # Narrow no-break space
    text = text.replace('\u202a', '')  # Left-to-right embedding
    text = text.replace('\u202c', '')  # Pop directional formatting
    text = text.replace('\u202d', '')  # Left-to-right override
    text = text.replace('\u202e', '')  # Right-to-left override
    text = text.replace('\u200f', '')  # Right-to-left mark
    text = text.replace('\u061c', '')  # Arabic letter mark
    
    # Additional invisible and formatting characters
    text = text.replace('\u200b', '')  # Zero-width space
    text = text.replace('\u200c', '')  # Zero-width non-joiner
    text = text.replace('\u200d', '')  # Zero-width joiner
    text = text.replace('\u2060', '')  # Word joiner
    text = text.replace('\u2066', '')  # Left-to-right isolate
    text = text.replace('\u2067', '')  # Right-to-left isolate
    text = text.replace('\u2068', '')  # First strong isolate
    text = text.replace('\u2069', '')  # Pop directional isolate
    text = text.replace('\u180e', '')  # Mongolian vowel separator
    text = text.replace('\u034f', '')  # Combining grapheme joiner
    text = text.replace('\u202b', '')  # Right-to-left embedding
    text = text.replace('\u2028', '')  # Line separator
    text = text.replace('\u2029', '')  # Paragraph separator
    text = text.replace('\u00ad', '')  # Soft hyphen
    text = text.replace('\u115f', '')  # Hangul choseong filler
    text = text.replace('\u1160', '')  # Hangul jungseong filler
    text = text.replace('\u17b4', '')  # Khmer vowel inherent aq
    text = text.replace('\u17b5', '')  # Khmer vowel inherent aa
    text = text.replace('\u3164', '')  # Hangul filler
    text = text.replace('\ufeff', '')  # Zero-width no-break space (BOM)
    text = text.replace('\uffa0', '')  # Halfwidth hangul filler
    
    # Remove all control characters except common ones like tab and newline
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    
    # Normalize whitespace - replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def normalize_contact_name(contact_name):
    """Normalize contact names to ensure consistent output between PC and mobile formats."""
    if not contact_name:
        return contact_name
    
    # Clean invisible characters first
    contact_name = clean_invisible(contact_name)
    
    # Remove tilde prefix if present
    if contact_name.startswith('~'):
        contact_name = contact_name[1:]
    
    # Normalize phone numbers
    if contact_name.startswith('+'):
        # Remove all spaces, dashes, and special characters from phone numbers
        # but preserve the + prefix and parentheses structure
        normalized = '+'
        rest = contact_name[1:]
        
        # Replace en-dash and em-dash with regular hyphen
        rest = rest.replace('\u2011', '-').replace('\u2014', '-')
        
        # For US numbers, preserve parentheses structure
        if '(' in rest and ')' in rest:
            # Extract parts: +1 (XXX) XXX-XXXX
            parts = rest.split(')')
            if len(parts) == 2:
                country_and_area = parts[0].strip()
                remaining = parts[1].strip()
                
                # Clean country code and area code - remove all non-digits except parentheses
                country_area_clean = re.sub(r'[^0-9()]', '', country_and_area)
                remaining_clean = re.sub(r'[^0-9]', '', remaining)
                
                # Extract just the digits for processing
                all_digits = re.sub(r'[^0-9]', '', country_area_clean + remaining_clean)
                
                # Handle US numbers (+1 format)
                if len(all_digits) == 11 and all_digits.startswith('1'):
                    country_code = all_digits[0]  # 1
                    area_code = all_digits[1:4]  # XXX
                    exchange = all_digits[4:7]   # XXX
                    number = all_digits[7:]      # XXXX
                    return f"+{country_code} ({area_code}) {exchange}-{number}"
                elif len(all_digits) == 10:  # US number without country code
                    area_code = all_digits[0:3]  # XXX
                    exchange = all_digits[3:6]   # XXX
                    number = all_digits[6:]      # XXXX
                    return f"+1 ({area_code}) {exchange}-{number}"
                elif len(remaining_clean) >= 7:
                    # Fallback to original logic for other formats
                    formatted = f"+{country_area_clean[:-3]} ({country_area_clean[-3:]}) {remaining_clean[:3]}-{remaining_clean[3:]}"
                    return formatted
        
        # For Indian numbers and others, remove spaces but keep structure
        # Convert +91 91 364 019 21 to +91 91364 01921
        clean_digits = re.sub(r'[^0-9]', '', rest)
        if clean_digits.startswith('91') and len(clean_digits) >= 10:
            # Indian number format
            country_code = clean_digits[:2]  # 91
            number = clean_digits[2:]  # remaining digits
            
            # Format as +91 XXXXX XXXXX
            if len(number) == 10:
                return f"+{country_code} {number[:5]} {number[5:]}"
            else:
                return f"+{country_code} {number}"
        else:
            # Other international numbers - just remove extra spaces
            return '+' + clean_digits
    
    # For non-phone number names, just trim whitespace
    return contact_name.strip()

def extract_message_data(match, raw_message, dt_obj, dt_utc):
    """Extract message data from regex match."""
    urls, url_matches = [], []
    phone_numbers, phone_matches = [], []
    emails, email_matches = [], []
    mentions, mention_matches = [], []
    emojis, emoji_matches = [], []
    money_amounts, money_matches = [], []
    message_modifier = ""
    group_system_keywords = [
        "created this group", "Messages and calls are end-to-end encrypted",
        "changed their phone number", "You were added", "You added",
        "left the group", "was removed", "pinned a message",
        "unpinned a message", "changed the group description", 
        "changed the group icon", "changed the group settings",
        "changed the subject to", "joined using this group's invite link",
        "became an admin", "is no longer an admin", "removed",
        "added", "Security code changed", "Your security code with",
        "Tap to learn more", "Disappearing messages", "turned on disappearing messages",
        "turned off disappearing messages", "set disappearing messages",
        "group invite link", "reset group invite link",
        "changed to", "changed from", "now allows", "now only allows"
    ]
    # More comprehensive emoji pattern
    emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002600-\U000026FF\U00002700-\U000027BF\U0001F900-\U0001F9FF\U0001F018-\U0001F270\U0001F000-\U0001F02F\U0001F0A0-\U0001F0FF\U0001F100-\U0001F64F\U0001F170-\U0001F251]', re.UNICODE)

    # Extract sender and message from match - ensure consistent extraction
    sender = clean_invisible(match.group(4)) if match.group(4) else "unknown"
    # Normalize the sender name for consistent contact handling
    sender = normalize_contact_name(sender)
    # Ensure sender is never empty or None
    if not sender or sender.strip() == "":
        sender = "unknown"
    message = clean_invisible(match.group(5)) if match.group(5) else ""
    
    # Detect and extract message modifiers - comprehensive patterns for all formats
    modifier_patterns = [
        r"<This message was edited>",
        r"\<This message was edited\>",  # Escaped version
        r"This message was deleted.*",
        r"changed their phone number.*",
        r"This message was deleted",
        r"\bThis message was edited\b",  # Word boundary version
        r"message was edited",
        r"was edited",
        r"\(edited\)",
        r"\[edited\]",
        r"edited"
    ]
    
    # More aggressive modifier removal with multiple passes
    modifier_regex = re.compile(r"|".join(modifier_patterns), re.IGNORECASE)
    message_modifier = ""
    
    # First pass: find and extract modifier
    modifier_match = modifier_regex.search(message)
    if modifier_match:
        message_modifier = modifier_match.group()
        message = modifier_regex.sub('', message).strip()
    
    # Second pass: remove any remaining modifier fragments
    # Remove common modifier patterns that might be left over
    message = re.sub(r'\s*<[^>]*edited[^>]*>\s*', '', message, flags=re.IGNORECASE)
    message = re.sub(r'\s*\([^)]*edited[^)]*\)\s*', '', message, flags=re.IGNORECASE)
    message = re.sub(r'\s*\[[^\]]*edited[^\]]*\]\s*', '', message, flags=re.IGNORECASE)
    
    # Clean up any trailing/leading whitespace and punctuation after modifier removal
    message = re.sub(r'^[\s\-:,\.]+|[\s\-:,\.]+$', '', message).strip()

    # Detect and extract patterns
    for pattern, container, collection in [
        (url_pattern, urls, url_matches),
        (phone_pattern, phone_numbers, phone_matches),
        (email_pattern, emails, email_matches),
        (money_pattern, money_amounts, money_matches),
        (r'@\w+', mentions, mention_matches)
    ]:
        for match_obj in re.finditer(pattern, message):
            item = match_obj.group()
            start_pos = match_obj.start()
            end_pos = match_obj.end()

            container.append(item)
            collection.append({
                'item': item,
                'start': start_pos,
                'end': end_pos
            })

    for match_obj in re.finditer(emoji_pattern, message):
        emoji = match_obj.group().strip()
        start_pos = match_obj.start()
        end_pos = match_obj.end()

        emojis.append(emoji)
        emoji_matches.append({
            'emoji': emoji,
            'start': start_pos,
            'end': end_pos
        })

    # Convert data to JSON strings for storage
    urls_json = json.dumps(urls) if urls else ""
    url_positions_json = json.dumps(url_matches) if url_matches else ""
    phone_numbers_json = json.dumps(phone_numbers) if phone_numbers else ""
    phone_positions_json = json.dumps(phone_matches) if phone_matches else ""
    emails_json = json.dumps(emails) if emails else ""
    email_positions_json = json.dumps(email_matches) if email_matches else ""
    money_amounts_json = json.dumps(money_amounts) if money_amounts else ""
    money_positions_json = json.dumps(money_matches) if money_matches else ""
    mentions_json = json.dumps(mentions) if mentions else ""
    mention_positions_json = json.dumps(mention_matches) if mention_matches else ""
    emojis_json = json.dumps(emojis) if emojis else ""
    emoji_positions_json = json.dumps(emoji_matches) if emoji_matches else ""

    # Remove extracted patterns from message to get clean text
    message_clean = message

    # Remove URLs
    message_clean = re.sub(url_pattern, '', message_clean)

    # Remove phone numbers
    message_clean = re.sub(phone_pattern, '', message_clean)

    # Remove email addresses
    message_clean = re.sub(email_pattern, '', message_clean)

    # Remove money amounts
    message_clean = re.sub(money_pattern, '', message_clean, flags=re.IGNORECASE)

    # Remove mentions, including standalone '@'
    message_clean = re.sub(r'@+', '', message_clean)

    # Remove emojis
    message_clean = re.sub(emoji_pattern, '', message_clean)

    # Clean up extra spaces, newlines, and other whitespace
    message_clean = re.sub(r'\s+', ' ', message_clean).strip()

    # Remove common separators left behind
    message_clean = re.sub(r'^[\s\-:,\.]+|[\s\-:,\.]+$', '', message_clean)

    # If message becomes empty after pattern removal, but there were extracted patterns
    if not message_clean and (urls or phone_numbers or emails or money_amounts or mentions or emojis):
        # Message was just extracted patterns, keep message empty
        message = ""
    else:
        # Message had actual text content besides extracted patterns
        message = message_clean

    # Detect media messages and extract captions/filenames
    media_type = ""
    media_file_name = ""
    # Ensure original_message is always a string
    original_message = str(message) if message else (str(urls[0]) if urls else "")

    # Common media patterns in WhatsApp exports (expanded for different formats)
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

    # Check for media patterns and extract captions/filenames
    # First check the raw message for media patterns to handle Unicode issues
    raw_message_check = clean_invisible(raw_message)
    
    for pattern, media_name in media_patterns:
        if re.search(pattern, message, re.IGNORECASE) or re.search(pattern, raw_message_check, re.IGNORECASE):
            media_type = media_name

            # Extract text after removing the media pattern
            remaining_text = re.sub(pattern, "", message, flags=re.IGNORECASE).strip()

            # Clean up any extra whitespace or separators
            remaining_text = re.sub(r'^[\s\-:]*', '', remaining_text)
            remaining_text = re.sub(r'[\s\-:]*$', '', remaining_text)

            # For documents, check if the remaining text looks like a filename
            if media_name == "document" and remaining_text:
                # Check if it contains file extension patterns or file size indicators
                if re.search(r'\.(pdf|doc|docx|txt|xlsx|ppt|pptx|zip|rar|jpg|png|mp4|mp3|wav)\s*[•·]?\s*\d+\s*(pages?|MB|KB|GB)', remaining_text, re.IGNORECASE):
                    # This looks like a filename, not a user caption
                    media_file_name = remaining_text
                    message = ""  # No user caption
                else:
                    # This might be a user caption
                    message = remaining_text
            else:
                # For other media types, treat as user caption
                message = remaining_text

            break

    # If no specific media type found but message looks like media, mark as general media
    # Be more specific to avoid false positives like "<This message was edited>"
    # Only detect as media if it's actually a media omitted pattern, not a message modifier
    if not media_type and not message_modifier:
        # Check both the cleaned message and raw message for patterns
        for search_text in [message, raw_message_check]:
            if re.search(r"omitted|<Media omitted>|<attached:", search_text, re.IGNORECASE):
                media_type = "media"
                # Try to extract caption from general media pattern
                remaining_text = re.sub(r"omitted|<Media omitted>|<attached:[^>]*>", "", message, flags=re.IGNORECASE).strip()
                remaining_text = re.sub(r'^[\s\-:]*', '', remaining_text)
                remaining_text = re.sub(r'[\s\-:]*$', '', remaining_text)
                message = remaining_text
                break

    group_system_flag = any(kw.lower() in original_message.lower() for kw in group_system_keywords)
    actual_sender = "group_notification" if group_system_flag else sender

    return {
        "datetime_ist": dt_obj.isoformat(),
        "datetime_ist_human": dt_obj.strftime("%d %b %Y, %I:%M %p"),
        "datetime_utc": dt_utc.isoformat(),
        "sender": actual_sender,
        "raw_message": raw_message,
        "message": message,
        "media": media_type,
        "media_file_name": media_file_name,
        "urls": urls_json,
        "url_positions": url_positions_json,
        "phone_numbers": phone_numbers_json,
        "phone_positions": phone_positions_json,
        "emails": emails_json,
        "email_positions": email_positions_json,
        "money_amounts": money_amounts_json,
        "money_positions": money_positions_json,
        "mentions": mentions_json,
        "mention_positions": mention_positions_json,
        "emojis": emojis_json,
        "emoji_positions": emoji_positions_json,
        "message_modifier": message_modifier,
        "group_system_message": group_system_flag,
        "year": dt_obj.year,
        "month": dt_obj.month,
        "day": dt_obj.day,
        "hour": dt_obj.hour,
        "minute": dt_obj.minute
    }

def parse_pc(lines, dt_utc_offset):
    """Parse PC format WhatsApp chat lines."""
    messages = []
    pc_message_regex = re.compile(r"\[(\d{2}/\d{2}/\d{2}),\s*(\d{1,2}:\d{2}:\d{2})\s?(AM|PM)\]\s*(.*?):\s*(.*)")
    
    for raw_message in lines:
        # Clean Unicode characters from the line before processing
        line = clean_invisible(raw_message.strip())
        if not line:
            continue
            
        match = pc_message_regex.match(line)
        if match:
            try:
                dt_obj = datetime.strptime(f"{match.group(1)} {match.group(2)} {match.group(3)}", "%d/%m/%y %I:%M:%S %p")
                dt_utc = dt_obj - dt_utc_offset
                msg_data = extract_message_data(match, raw_message, dt_obj, dt_utc)
                messages.append(msg_data)
            except ValueError:
                # Skip malformed date/time entries
                continue
        else:
            # Handle continuation lines with consistent cleaning
            if messages and "message" in messages[-1]:
                cleaned_line = clean_invisible(line)
                if isinstance(messages[-1]["message"], str):
                    messages[-1]["message"] += " " + cleaned_line
                else:
                    messages[-1]["message"] = str(messages[-1]["message"]) + " " + cleaned_line
    
    # Normalize pre/post processing for both PC and Mobile
    for msg in messages:
        original_msg = msg['raw_message']
        # Check for various media patterns in raw message
        # Only set generic 'media' if no specific media type was already detected
        if not msg.get('media'):
            media_indicators = [
                '\u003cMedia omitted\u003e', '\u003cattached:', 'image omitted', 'video omitted', 'audio omitted', 'document omitted',
                'Media omitted', 'omitted', 'attached:', 'IMG-', 'VID-', 'AUD-', 'DOC-'
            ]
            
            for indicator in media_indicators:
                if indicator in original_msg:
                    msg['media'] = 'media'
                    break

        # Ensure media message consistency
        if msg.get('media', ''):
            msg['message'] = msg['message'] or '[Media message]'

    # Filter out group notifications
    filtered_messages = [msg for msg in messages if msg.get('sender') != 'group_notification']
    return filtered_messages

def parse_mobile(lines, dt_utc_offset):
    """Parse mobile format WhatsApp chat lines."""
    messages = []
    # Updated regex pattern to handle different mobile formats with flexible whitespace
    mobile_message_regex = re.compile(r"(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2})\s?(am|pm|AM|PM)\s*-\s*(.*?):\s*(.*)")
    
    # Regex to detect group notification lines without explicit sender
    mobile_group_notification_regex = re.compile(r"(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2})\s?(am|pm|AM|PM)\s*-\s*(.*)")
    
    for raw_message in lines:
        # Apply same Unicode cleaning as PC format
        line = clean_invisible(raw_message.strip())
        if not line:
            continue
            
        match = mobile_message_regex.match(line)
        if match:
            try:
                date_str, time_str, am_pm, sender, message = match.groups()
                
                # Handle different date formats (DD/MM/YY or D/M/YY or DD/MM/YYYY)
                if len(date_str.split('/')[2]) == 2:
                    # Two-digit year
                    dt_obj = datetime.strptime(f"{date_str} {time_str} {am_pm.upper()}", "%d/%m/%y %I:%M %p")
                else:
                    # Four-digit year
                    dt_obj = datetime.strptime(f"{date_str} {time_str} {am_pm.upper()}", "%d/%m/%Y %I:%M %p")
                    
                dt_utc = dt_obj - dt_utc_offset
                
                # Create a mock match object for extract_message_data
                class MockMatch:
                    def __init__(self, groups):
                        self._groups = groups
                    def group(self, n):
                        return self._groups[n-1] if n <= len(self._groups) else None
                    def groups(self):
                        return self._groups
                
                mock_match = MockMatch([date_str, time_str, am_pm, sender, message])
                msg_data = extract_message_data(mock_match, raw_message, dt_obj, dt_utc)
                messages.append(msg_data)
            except ValueError as e:
                # Skip malformed date/time entries
                print(f"Error parsing mobile message: {e} - Line: {line}")
                continue
        else:
            # Handle group notifications without explicit senders
            group_notification_match = mobile_group_notification_regex.match(line)
            if group_notification_match:
                try:
                    date_str, time_str, am_pm, message = group_notification_match.groups()
                    
                    # Handle different date formats (DD/MM/YY or D/M/YY or DD/MM/YYYY)
                    if len(date_str.split('/')[2]) == 2:
                        # Two-digit year
                        dt_obj = datetime.strptime(f"{date_str} {time_str} {am_pm.upper()}", "%d/%m/%y %I:%M %p")
                    else:
                        # Four-digit year
                        dt_obj = datetime.strptime(f"{date_str} {time_str} {am_pm.upper()}", "%d/%m/%Y %I:%M %p")

                    dt_utc = dt_obj - dt_utc_offset

                    msg_data = {
                        'datetime_ist': dt_obj.isoformat(),
                        'datetime_ist_human': dt_obj.strftime("%d %b %Y, %I:%M %p"),
                        'datetime_utc': dt_utc.isoformat(),
                        'sender': 'group_notification',
                        'raw_message': raw_message,
                        'message': message,
                        'media': '',
                        'media_file_name': '',
                        'urls': '',
                        'url_positions': '',
                        'phone_numbers': '',
                        'phone_positions': '',
                        'emails': '',
                        'email_positions': '',
                        'money_amounts': '',
                        'money_positions': '',
                        'mentions': '',
                        'mention_positions': '',
                        'emojis': '',
                        'emoji_positions': '',
                        'message_modifier': '',
                        'group_system_message': True,
                        'year': dt_obj.year,
                        'month': dt_obj.month,
                        'day': dt_obj.day,
                        'hour': dt_obj.hour,
                        'minute': dt_obj.minute
                    }
                    messages.append(msg_data)
                except ValueError as e:
                    # Skip malformed date/time entries
                    print(f"Error parsing mobile group notification: {e} - Line: {line}")
                    continue
            else:
                # Handle continuation lines with consistent cleaning
                if messages and "message" in messages[-1]:
                    cleaned_line = clean_invisible(line)
                    if isinstance(messages[-1]["message"], str):
                        messages[-1]["message"] += " " + cleaned_line
                    else:
                        messages[-1]["message"] = str(messages[-1]["message"]) + " " + cleaned_line

    # Enhanced media detection for mobile format - use advanced pattern matching
    for msg in messages:
        original_msg = msg['raw_message']
        message_content = msg['message']
        
        # If no specific media type was detected, try to detect from raw message
        if not msg.get('media'):
            # First, check for direct patterns in the raw message
            media_patterns = [
                # Specific media type patterns for mobile (if they exist)
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
                # File type patterns
                (r"IMG-\d+", "image"),
                (r"VID-\d+", "video"),
                (r"AUD-\d+", "audio"),
                (r"DOC-\d+", "document"),
                # File extension patterns
                (r"\.(jpg|jpeg|png|bmp|webp)", "image"),
                (r"\.(mp4|mov|avi|mkv|wmv|flv)", "video"),
                (r"\.(gif)", "gif"),
                (r"\.(mp3|wav|aac|flac|m4a|wma)", "audio"),
                (r"\.(pdf|doc|docx|txt|xlsx|ppt|pptx)", "document"),
                # Additional mobile patterns
                (r"\u003cattached:", "attachment"),
                (r"attached:", "attachment"),
                # Generic mobile pattern - this will be refined further
                (r"\u003cMedia omitted\u003e", "media"),
                (r"Media omitted", "media"),
                # Generic fallback
                (r"omitted", "media")
            ]
            
            # Check both message content and raw message
            for pattern, media_type in media_patterns:
                if (re.search(pattern, message_content, re.IGNORECASE) or 
                    re.search(pattern, original_msg, re.IGNORECASE)):
                    msg['media'] = media_type
                    break
        
        # For messages detected as generic "media", try to infer the type
        if msg.get('media') == 'media':
            # Use timestamp-based matching with PC format patterns
            # This is a heuristic approach based on the observation that 
            # mobile and PC formats have similar timestamps
            
            # Check for context clues in surrounding messages or captions
            # Look for file extensions or media-related keywords
            inference_patterns = [
                # Document patterns
                (r"\b(pdf|doc|docx|txt|xlsx|ppt|pptx|zip|rar)\b", "document"),
                (r"\b(pages?)\b", "document"),
                (r"\b(rulebook|rules|document|file)\b", "document"),
                
                # Image patterns
                (r"\b(jpg|jpeg|png|gif|bmp|webp)\b", "image"),
                (r"\b(image|photo|picture|pic|screenshot)\b", "image"),
                
                # Video patterns
                (r"\b(mp4|mov|avi|mkv|wmv|flv)\b", "video"),
                (r"\b(video|vid|movie|clip)\b", "video"),
                
                # Audio patterns
                (r"\b(mp3|wav|aac|flac|m4a|wma)\b", "audio"),
                (r"\b(audio|voice|sound|music)\b", "audio"),
                
                # GIF patterns
                (r"\b(gif|animated)\b", "gif"),
                
                # Sticker patterns
                (r"\b(sticker|emoji)\b", "sticker")
            ]
            
            # Check the raw message for these patterns
            for pattern, media_type in inference_patterns:
                if re.search(pattern, original_msg, re.IGNORECASE):
                    msg['media'] = media_type
                    break
        
        # Additional heuristic: analyze message context for media type inference
        if msg.get('media') == 'media':
            # Look at the timestamp and try to match with known patterns
            # This is based on the observation that PC and mobile have similar timestamps
            
            # For now, let's use a simple heuristic based on message length and content
            # Most generic media messages are short and contain only "<Media omitted>"
            if len(message_content.strip()) <= 20:  # Very short messages
                # Use statistical distribution from PC format as a fallback
                # PC format shows: images (97), videos (30), documents (11), etc.
                # We can use a simple probability-based assignment
                
                # For now, keep as generic "media" but this could be enhanced
                # with more sophisticated pattern matching
                pass
        
        # Additional check for messages that might contain media references in context
        if not msg.get('media'):
            # Check for media-related keywords in the message
            media_keywords = [
                (r"\bvideo\b", "video"),
                (r"\bimage\b", "image"),
                (r"\bphoto\b", "image"),
                (r"\bpicture\b", "image"),
                (r"\bgif\b", "gif"),
                (r"\baudio\b", "audio"),
                (r"\bvoice\b", "voice"),
                (r"\bdocument\b", "document"),
                (r"\bpdf\b", "document"),
                (r"\bsticker\b", "sticker")
            ]
            
            # Only apply this if the message is short and likely refers to media
            if len(message_content) < 200:  # Avoid false positives in long messages
                for pattern, media_type in media_keywords:
                    if re.search(pattern, message_content, re.IGNORECASE):
                        # Additional validation to avoid false positives
                        if any(word in message_content.lower() for word in ['share', 'send', 'attach', 'upload', 'good', 'nice', 'see', 'watch', 'look']):
                            msg['media'] = media_type
                            break

        # Ensure media message consistency
        if msg.get('media', ''):
            msg['message'] = msg['message'] or '[Media message]'

    # Filter out group notifications
    filtered_messages = [msg for msg in messages if msg.get('sender') != 'group_notification']
    return filtered_messages

def enhance_mobile_media_with_pc_reference(mobile_messages, pc_messages):
    """Enhance mobile media detection using PC format as reference with fuzzy timestamp matching."""
    if not pc_messages:
        return mobile_messages
    
    # Create timestamp-based mapping from PC media types with fuzzy matching
    pc_media_timestamps = []
    for msg in pc_messages:
        if msg.get('media') and msg.get('media') != '':
            timestamp = msg['datetime_ist']
            media_type = msg['media']
            dt = datetime.fromisoformat(timestamp)
            pc_media_timestamps.append((dt, media_type))
    
    # Apply fuzzy timestamp matching to mobile generic media messages
    enhanced_count = 0
    matched_pairs = []
    unmatched_mobile = []
    
    for msg in mobile_messages:
        if msg.get('media') == 'media':  # Generic media that needs enhancement
            timestamp = msg['datetime_ist']
            dt = datetime.fromisoformat(timestamp)
            
            # Find the closest PC media message within 30 seconds
            best_match = None
            min_diff = timedelta(seconds=30)
            
            for pc_dt, pc_media_type in pc_media_timestamps:
                diff = abs(dt - pc_dt)
                if diff <= min_diff:
                    min_diff = diff
                    best_match = pc_media_type
            
            if best_match:
                msg['media'] = best_match
                msg['enhanced_from_pc'] = True  # Mark as enhanced
                enhanced_count += 1
                matched_pairs.append((msg['datetime_ist'], best_match, min_diff.total_seconds()))
            else:
                unmatched_mobile.append(msg['datetime_ist'])
    
    # Debug logging
    if enhanced_count > 0:
        print(f"\n🔧 Enhanced {enhanced_count} mobile media messages using PC reference")
        print(f"   Matched pairs (timestamp, type, diff_seconds):")
        for timestamp, media_type, diff in matched_pairs[:5]:  # Show first 5
            print(f"   - {timestamp} -> {media_type} (±{diff:.1f}s)")
        if len(matched_pairs) > 5:
            print(f"   ... and {len(matched_pairs) - 5} more matches")
    
    if unmatched_mobile:
        print(f"\n⚠️  {len(unmatched_mobile)} mobile media messages could not be matched")
        if len(unmatched_mobile) <= 3:
            print(f"   Unmatched timestamps: {unmatched_mobile}")
    
    return mobile_messages

def parse_chat_file(file: Union[str, IO, Any], utc_offset_hours=0, pc_reference_file=None) -> pd.DataFrame:
    """
    Parse WhatsApp chat file from filepath or uploaded file object.
    Supports both PC and Android formats.
    
    Args:
        file: The main chat file to parse
        utc_offset_hours: UTC offset for timezone conversion
        pc_reference_file: Optional PC format file to enhance mobile media detection
    """
    # Read lines from file or uploaded file object
    if isinstance(file, str):
        with open(file, "r", encoding="utf-8") as f:
            lines = f.readlines()
    else:
        # Handle Streamlit UploadedFile or similar
        try:
            content = file.read()
            if isinstance(content, bytes):
                content = content.decode("utf-8")
            elif isinstance(content, bytearray):
                content = content.decode("utf-8")
            elif isinstance(content, memoryview):
                content = content.tobytes().decode("utf-8")
            elif not isinstance(content, str):
                content = str(content)
            lines = content.splitlines()
        except Exception as e:
            raise ValueError(f"Error reading file: {e}")
        
    if not lines:
        return pd.DataFrame(columns=[
            "datetime_ist", "datetime_ist_human", "datetime_utc", "sender", 
            "raw_message", "message", "media", "media_file_name", "urls", "url_positions", 
            "phone_numbers", "phone_positions", "emails", "email_positions", 
            "money_amounts", "money_positions", "mentions", "mention_positions",
            "emojis", "emoji_positions", "message_modifier", "group_system_message", 
            "year", "month", "day", "hour", "minute"
        ])

    dt_utc_offset = timedelta(hours=utc_offset_hours)

    # Detect format by first non-empty line
    first_line = next((ln for ln in lines if ln.strip()), "")
    format_detected = ""

    # Clean first line for detection
    clean_first_line = clean_invisible(first_line)

    if clean_first_line.startswith('['):
        # PC format: [DD/MM/YY, HH:MM:SS AM/PM] Sender: Message
        format_detected = "PC"
        messages = parse_pc(lines, dt_utc_offset)
    elif "-" in clean_first_line and "," in clean_first_line:
        # Mobile format: DD/MM/YY, HH:MM AM/PM - Sender: Message
        format_detected = "Mobile"
        messages = parse_mobile(lines, dt_utc_offset)
    else:
        # Default to PC format
        format_detected = "PC (default)"
        messages = parse_pc(lines, dt_utc_offset)

    # If PC reference file is provided and current format is mobile, enhance media detection
    if pc_reference_file and format_detected.startswith("Mobile"):
        print(f"\n🔗 Processing PC reference file for mobile media enhancement...")
        try:
            # Parse PC reference file
            if isinstance(pc_reference_file, str):
                with open(pc_reference_file, "r", encoding="utf-8") as f:
                    pc_lines = f.readlines()
            else:
                # Handle uploaded file object
                try:
                    pc_content = pc_reference_file.read()
                    if isinstance(pc_content, bytes):
                        pc_content = pc_content.decode("utf-8")
                    elif isinstance(pc_content, bytearray):
                        pc_content = pc_content.decode("utf-8")
                    elif isinstance(pc_content, memoryview):
                        pc_content = pc_content.tobytes().decode("utf-8")
                    elif not isinstance(pc_content, str):
                        pc_content = str(pc_content)
                    pc_lines = pc_content.splitlines()
                except Exception as e:
                    print(f"⚠️  Error reading PC reference file: {e}")
                    pc_lines = []
            
            if pc_lines:
                # Parse PC messages
                pc_messages = parse_pc(pc_lines, dt_utc_offset)
                print(f"   PC reference file parsed: {len(pc_messages)} messages")
                
                # Count PC media messages
                pc_media_count = len([msg for msg in pc_messages if msg.get('media') and msg.get('media') != ''])
                print(f"   PC media messages: {pc_media_count}")
                
                # Enhance mobile messages with PC reference
                messages = enhance_mobile_media_with_pc_reference(messages, pc_messages)
            else:
                print(f"   ⚠️  No valid lines found in PC reference file")
                
        except Exception as e:
            print(f"⚠️  Error processing PC reference file: {e}")
            print(f"   Continuing with original mobile parsing...")
    
    # Debug information
    print(f"\n🔍 Debug Information:")
    print(f"Format detected: {format_detected}")
    print(f"Total lines in file: {len(lines)}")
    print(f"First line sample: {repr(clean_first_line[:100])}")
    print(f"Raw messages parsed: {len(messages)}")
    
    # Filter out malformed messages - ensure all required fields are present
    required_fields = ['sender', 'message', 'datetime_ist', 'datetime_utc']
    valid_messages = []
    malformed_messages = []
    
    for message in messages:
        if isinstance(message, dict):
            missing_fields = [field for field in required_fields if field not in message]
            if not missing_fields:
                valid_messages.append(message)
            else:
                malformed_messages.append((message, missing_fields))
        else:
            malformed_messages.append((message, ['not_dict']))
    
    malformed_count = len(malformed_messages)
    
    print(f"Valid messages after filtering: {len(valid_messages)}")
    print(f"Malformed messages filtered out: {malformed_count}")
    
    # Debug: show details of malformed messages
    if malformed_count > 0:
        print(f"\n⚠️  Malformed message details:")
        for i, (msg, missing) in enumerate(malformed_messages[:3]):  # Show first 3
            print(f"   Message {i+1}: Missing fields: {missing}")
            if isinstance(msg, dict):
                print(f"   Available fields: {list(msg.keys())}")
            else:
                print(f"   Message type: {type(msg)}")
        if malformed_count > 3:
            print(f"   ... and {malformed_count - 3} more malformed messages")
    
    # Debug: Inspect keys of valid_messages BEFORE DataFrame creation
    print(f"\n🔍 Raw message dict keys inspection:")
    if valid_messages:
        # Check the keys of the first few message dictionaries
        for i, msg in enumerate(valid_messages[:5]):
            print(f"  Message {i} keys: {[repr(k) for k in msg.keys()]}")

        # Clean the keys just in case, before creating the DataFrame
        clean_valid_messages = []
        for msg in valid_messages:
            clean_msg = {str(k).strip().strip("'\""): v for k, v in msg.items()}
            clean_valid_messages.append(clean_msg)
        valid_messages = clean_valid_messages

    if not valid_messages:
        return pd.DataFrame(columns=[
            "datetime_ist", "datetime_ist_human", "datetime_utc", "sender", 
            "raw_message", "message", "media", "media_file_name", "urls", "url_positions", 
            "phone_numbers", "phone_positions", "emails", "email_positions", 
            "money_amounts", "money_positions", "mentions", "mention_positions",
            "emojis", "emoji_positions", "message_modifier", "group_system_message", 
            "year", "month", "day", "hour", "minute"
        ])

    # ===== CRITICAL FIX: Ensure all dictionary keys are clean strings =====
    cleaned_valid_messages = []
    for msg in valid_messages:
        cleaned_msg = {}
        for k, v in msg.items():
            # Clean the key more aggressively - remove all quotes and whitespace
            clean_key = str(k).strip().strip("'").strip('"').strip()
            cleaned_msg[clean_key] = v
        cleaned_valid_messages.append(cleaned_msg)
    valid_messages = cleaned_valid_messages
    
    try:
        df = pd.DataFrame(valid_messages)
        
        # Debug: Check DataFrame columns and sample data
        print(f"\n🔍 DataFrame Debug Info:")
        print(f"DataFrame columns: {list(df.columns)}")
        print(f"DataFrame shape: {df.shape}")
        
        # Check for invisible characters in column names
        print(f"Column names with repr: {[repr(col) for col in df.columns]}")
        
        # More detailed column name analysis
        print(f"\n🔍 Column Name Analysis:")
        for i, col in enumerate(df.columns):
            print(f"  {i}: {repr(col)} (type: {type(col)}, len: {len(col)})")
            if not col.isascii():
                print(f"    ⚠️  Non-ASCII characters detected in column name!")
            # Check for invisible characters
            if col != col.strip():
                print(f"    ⚠️  Leading/trailing whitespace detected!")
            if "'" in col:
                print(f"    ⚠️  Quote characters detected in column name!")
        
        # Check if specific columns exist
        required_cols = ['datetime_ist', 'sender', 'message']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            print(f"⚠️  Missing required columns: {missing_cols}")
            print(f"Available columns: {list(df.columns)}")
            raise KeyError(f"Missing required columns: {missing_cols}")
        
        if len(df) > 0:
            print(f"Sample row keys: {list(df.iloc[0].keys()) if hasattr(df.iloc[0], 'keys') else 'N/A'}")
            print(f"First few rows sender values: {df['sender'].head(3).tolist() if 'sender' in df.columns else 'sender column missing'}")
            
            # Check for null values in key columns
            for col in required_cols:
                null_count = df[col].isnull().sum()
                if null_count > 0:
                    print(f"⚠️  Column '{col}' has {null_count} null values")
            
            # Debug sender column specifically
            print(f"\n🔍 Sender Column Debug:")
            print(f"Sender column dtype: {df['sender'].dtype}")
            print(f"Sender column type: {type(df['sender'])}")
            print(f"First sender value type: {type(df['sender'].iloc[0])}")
            print(f"First sender value repr: {repr(df['sender'].iloc[0])}")
            
            # Check if any sender values are None/NaN
            none_senders = df['sender'].isnull().sum()
            empty_senders = (df['sender'] == '').sum()
            print(f"None/NaN senders: {none_senders}")
            print(f"Empty string senders: {empty_senders}")
            
            # Show unique sender values for debugging
            unique_senders = df['sender'].unique()
            print(f"Unique sender count: {len(unique_senders)}")
            print(f"Sample unique senders: {unique_senders[:5].tolist()}")
        
        df["message"] = df["message"].astype(str).str.strip()
        df["message_modifier"] = df["message_modifier"].astype(str).str.strip()

        # Post-processing cleaning step to remove any message modifiers
        df["message"] = df["message"].str.replace(r'<This message was edited>', '', regex=True)
        df["message"] = df["message"].str.replace(r'\(edited\)', '', regex=True)
        df["message"] = df["message"].str.replace(r'\[edited\]', '', regex=True)
        # Strip leading/trailing whitespace again in case any new whitespace is introduced
        df["message"] = df["message"].str.strip()
        
        # ===== CRITICAL FIX: Clean column names and data before groupby =====
        print(f"\n🧹 Cleaning DataFrame before groupby...")
        
        # Clean column names more aggressively
        new_columns = []
        for col in df.columns:
            # Convert to string and strip all quotes and whitespace
            clean_col = str(col).strip().strip("'").strip('"').strip()
            new_columns.append(clean_col)
        
        print(f"Before cleaning: {[repr(col) for col in df.columns]}")
        df.columns = new_columns
        print(f"After cleaning: {[repr(col) for col in df.columns]}")
        
        # Force reassign the DataFrame with cleaned columns to ensure it takes effect
        df = df.copy()
        df.columns = [str(col).strip().strip("'").strip('"').strip() for col in df.columns]
        
        # Verify the column names are clean
        quote_check = all(isinstance(col, str) and "'" not in col for col in df.columns)
        print(f"Column names are clean: {quote_check}")
        
        # Ensure critical columns are string type and handle null values
        critical_columns = ['sender', 'message', 'media']
        for col in critical_columns:
            if col in df.columns:
                # Convert to string and handle null values
                df[col] = df[col].astype(str)
                df[col] = df[col].fillna('').str.strip()
                
                # Log any remaining issues
                null_count = df[col].isnull().sum()
                empty_count = (df[col] == '').sum()
                print(f"Column '{col}': {null_count} nulls, {empty_count} empty strings")
        
        # Final verification before groupby
        print(f"\n🔍 Pre-groupby verification:")
        print(f"DataFrame columns after cleaning: {list(df.columns)}")
        print(f"'sender' column exists: {'sender' in df.columns}")
        print(f"'message' column exists: {'message' in df.columns}")
        print(f"'media' column exists: {'media' in df.columns}")
        
        # TEMPORARILY DISABLE DEDUPLICATION TO ISOLATE THE ISSUE
        print(f"\n🔍 DEBUG: Skipping deduplication to isolate the issue...")
        print(f"🔍 DEBUG: Current columns: {list(df.columns)}")
        
        # Add enhanced flag column if it doesn't exist
        if 'enhanced_from_pc' not in df.columns:
            df['enhanced_from_pc'] = False
        
        # Sort by datetime first to ensure consistent ordering
        df = df.sort_values('datetime_ist')
        
        print(f"🔍 DEBUG: Columns after sorting: {list(df.columns)}")
        
        # Additional debug info about the DataFrame
        print(f"\n📊 DataFrame Statistics:")
        print(f"Total rows in DataFrame: {len(df)}")
        
        # Safely access columns for statistics
        media_col = None
        sender_col = None
        for col in df.columns:
            if 'media' in col and len(col) <= 7:  # media column
                media_col = col
            if 'sender' in col and len(col) <= 8:  # sender column
                sender_col = col
        
        if media_col:
            print(f"Media messages: {len(df[df[media_col] != ''])}")
        else:
            print("Media messages: Unable to find media column")
        
        if sender_col:
            print(f"Group notifications: {len(df[df[sender_col] == 'group_notification'])}")
            print(f"Unique senders: {df[sender_col].nunique()}")
        else:
            print("Group notifications: Unable to find sender column")
            print("Unique senders: Unable to find sender column")
        
        return df
    except Exception as e:
        raise ValueError(f"Error creating DataFrame: {e}")


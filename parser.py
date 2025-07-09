import re
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Union, IO, Any

def clean_invisible(text: str) -> str:
    """Clean invisible Unicode characters from text."""
    if not isinstance(text, str):
        text = str(text)
    return text.replace('\u200e', '').replace('\u202f', '').strip()

def parse_chat_file(file: Union[str, Any]) -> pd.DataFrame:
    """Parse WhatsApp chat file from either a file path or uploaded file object."""
    # Read lines from a file path or UploadedFile (binary stream)
    if isinstance(file, str):
        # File path case
        with open(file, "r", encoding="utf-8") as f:
            lines = f.readlines()
    else:
        # Streamlit UploadedFile case
        try:
            # Read content from uploaded file
            content = file.read()
            
            # Handle different content types
            if isinstance(content, bytes):
                content = content.decode("utf-8")
            elif isinstance(content, bytearray):
                content = content.decode("utf-8")
            elif isinstance(content, memoryview):
                content = content.tobytes().decode("utf-8")
            elif not isinstance(content, str):
                content = str(content)
            
            # Split into lines
            lines = content.splitlines()
        except Exception as e:
            raise ValueError(f"Error reading file: {e}")

    msg_pattern = re.compile(r'^\[(\d{2}/\d{2}/\d{2}), (\d{1,2}:\d{2}:\d{2})\s?(AM|PM)\] (.*?): (.*)')
    modifier_patterns = [
        r"<This message was edited>",
        r"This message was deleted.*",
        r"changed their phone number.*"
    ]
    modifier_regex = re.compile(r"|".join(modifier_patterns), re.IGNORECASE)

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

    messages = []
    current = None

    for line in lines:
        # Ensure line is a string and clean it
        if not isinstance(line, str):
            line = str(line)
        line = clean_invisible(line.strip())
        match = msg_pattern.match(line)

        if match:
            if current:
                messages.append(current)

            date_str, time_str, am_pm, sender, message = match.groups()
            try:
                dt_str = f"{date_str} {time_str} {am_pm}"
                # Parse using correct DD/MM/YY format (not YY/MM/DD)
                dt_obj = datetime.strptime(dt_str, "%d/%m/%y %I:%M:%S %p").replace(tzinfo=ZoneInfo("Asia/Kolkata"))
                dt_utc = dt_obj.astimezone(ZoneInfo("UTC"))
            except Exception:
                continue

            modifier_match = modifier_regex.search(message)
            modifier = ""
            if modifier_match:
                modifier = modifier_match.group()
                message = modifier_regex.sub('', message).strip()

            # Store the raw message before any processing
            raw_message = message
            
            # Extract URLs with their positions
            url_pattern = r'https?://[^\s]+'
            url_matches = []
            urls = []
            
            for match in re.finditer(url_pattern, message):
                url = match.group()
                start_pos = match.start()
                end_pos = match.end()
                
                urls.append(url)
                url_matches.append({
                    'url': url,
                    'start': start_pos,
                    'end': end_pos
                })
            
            # Extract phone numbers with their positions
            phone_pattern = r'\+?\d[\d\s\-\(\)]{7,}\d'
            phone_matches = []
            phone_numbers = []
            
            for match in re.finditer(phone_pattern, message):
                phone = match.group().strip()
                start_pos = match.start()
                end_pos = match.end()
                
                phone_numbers.append(phone)
                phone_matches.append({
                    'phone': phone,
                    'start': start_pos,
                    'end': end_pos
                })
            
            # Extract email addresses with their positions
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            email_matches = []
            emails = []
            
            for match in re.finditer(email_pattern, message):
                email = match.group().strip()
                start_pos = match.start()
                end_pos = match.end()
                
                emails.append(email)
                email_matches.append({
                    'email': email,
                    'start': start_pos,
                    'end': end_pos
                })
            
            # Extract money amounts with their positions (multiple currencies)
            money_pattern = r'(?:Rs\.?|₹|\$|€|£|¥|₩|₽|₦|₨|₪|₡|₢|₣|₤|₥|₦|₧|₨|₩|₪|₫|€|₭|₮|₯|₰|₱|₲|₳|₴|₵|₶|₷|₸|₹|₺)\s*[0-9,]+(?:\.[0-9]{1,2})?|[0-9,]+(?:\.[0-9]{1,2})?\s*(?:Rs|rupees?|dollars?|euros?|pounds?|yen|won|ruble|naira|shekel|USD|EUR|GBP|INR|JPY|KRW|RUB|NGN|ILS)\b'
            money_matches = []
            money_amounts = []
            
            for match in re.finditer(money_pattern, message, re.IGNORECASE):
                money = match.group().strip()
                start_pos = match.start()
                end_pos = match.end()
                
                money_amounts.append(money)
                money_matches.append({
                    'money': money,
                    'start': start_pos,
                    'end': end_pos
                })
            
            # Extract mentions with their positions (@username)
            mention_pattern = r'@[\dA-Za-z_]+'
            mention_matches = []
            mentions = []
            
            for match in re.finditer(mention_pattern, message):
                mention = match.group().strip()
                start_pos = match.start()
                end_pos = match.end()
                
                mentions.append(mention)
                mention_matches.append({
                    'mention': mention,
                    'start': start_pos,
                    'end': end_pos
                })
            
            # Extract emojis with their positions
            # Unicode ranges for emojis
            emoji_pattern = r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002600-\U000026FF\U00002700-\U000027BF\U0001F900-\U0001F9FF\U0001F018-\U0001F270\U0001F000-\U0001F02F\U0001F0A0-\U0001F0FF\U0001F100-\U0001F64F\U0001F170-\U0001F251]'
            emoji_matches = []
            emojis = []
            
            for match in re.finditer(emoji_pattern, message):
                emoji = match.group().strip()
                start_pos = match.start()
                end_pos = match.end()
                
                emojis.append(emoji)
                emoji_matches.append({
                    'emoji': emoji,
                    'start': start_pos,
                    'end': end_pos
                })
            
            # Convert data to JSON strings for storage
            urls_json = str(urls) if urls else ""
            url_positions_json = str(url_matches) if url_matches else ""
            phone_numbers_json = str(phone_numbers) if phone_numbers else ""
            phone_positions_json = str(phone_matches) if phone_matches else ""
            emails_json = str(emails) if emails else ""
            email_positions_json = str(email_matches) if email_matches else ""
            money_amounts_json = str(money_amounts) if money_amounts else ""
            money_positions_json = str(money_matches) if money_matches else ""
            mentions_json = str(mentions) if mentions else ""
            mention_positions_json = str(mention_matches) if mention_matches else ""
            emojis_json = str(emojis) if emojis else ""
            emoji_positions_json = str(emoji_matches) if emoji_matches else ""
            
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
            original_message = message if message else (urls[0] if urls else "")
            
            # Common media patterns in WhatsApp exports
            media_patterns = {
                r"image omitted": "image",
                r"video omitted": "video", 
                r"gif omitted": "gif",
                r"audio omitted": "audio",
                r"voice message omitted": "voice",
                r"document omitted": "document",
                r"sticker omitted": "sticker",
                r"contact card omitted": "contact",
                r"location omitted": "location",
                r"poll omitted": "poll",
                r"<Media omitted>": "media",
                r"<attached: .*>": "attachment"
            }
            
            # Check for media patterns and extract captions/filenames
            for pattern, media_name in media_patterns.items():
                if re.search(pattern, message, re.IGNORECASE):
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
            if not media_type and re.search(r"omitted|<.*>", message, re.IGNORECASE):
                media_type = "media"
                # Try to extract caption from general media pattern
                remaining_text = re.sub(r"omitted|<.*>", "", message, flags=re.IGNORECASE).strip()
                remaining_text = re.sub(r'^[\s\-:]*', '', remaining_text)
                remaining_text = re.sub(r'[\s\-:]*$', '', remaining_text)
                message = remaining_text

            group_system_flag = any(kw.lower() in original_message.lower() for kw in group_system_keywords)
            actual_sender = "group_notification" if group_system_flag else sender

            current = {
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
                "message_modifier": modifier,
                "group_system_message": group_system_flag,
                "year": dt_obj.year,
                "month": dt_obj.month,
                "day": dt_obj.day,
                "hour": dt_obj.hour,
                "minute": dt_obj.minute
            }

        else:
            if current:
                mod_match = modifier_regex.search(line)
                if mod_match:
                    current["message_modifier"] += " " + mod_match.group()
                else:
                    current["message"] += "\n" + line

    if current:
        messages.append(current)

    # Create DataFrame with error handling
    if not messages:
        # Return empty DataFrame with expected columns if no messages found
        return pd.DataFrame(columns=[
            "datetime_ist", "datetime_ist_human", "datetime_utc", "sender", 
            "raw_message", "message", "media", "media_file_name", "urls", "url_positions", 
            "phone_numbers", "phone_positions", "emails", "email_positions", 
            "money_amounts", "money_positions", "mentions", "mention_positions",
            "emojis", "emoji_positions", "message_modifier", "group_system_message", 
            "year", "month", "day", "hour", "minute"
        ])
    
    try:
        df = pd.DataFrame(messages)
        df["message"] = df["message"].astype(str).str.strip()
        df["message_modifier"] = df["message_modifier"].astype(str).str.strip()
        return df
    except Exception as e:
        raise ValueError(f"Error creating DataFrame: {e}")

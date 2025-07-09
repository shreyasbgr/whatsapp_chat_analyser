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
                dt_obj = datetime.strptime(dt_str, "%y/%m/%d %I:%M:%S %p").replace(tzinfo=ZoneInfo("Asia/Kolkata"))
                dt_utc = dt_obj.astimezone(ZoneInfo("UTC"))
            except Exception:
                continue

            modifier_match = modifier_regex.search(message)
            modifier = ""
            if modifier_match:
                modifier = modifier_match.group()
                message = modifier_regex.sub('', message).strip()

            # Detect media messages
            media_type = ""
            original_message = message
            
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
            
            # Check for media patterns
            for pattern, media_name in media_patterns.items():
                if re.search(pattern, message, re.IGNORECASE):
                    media_type = media_name
                    # Clear the message content for media messages
                    message = ""
                    break
            
            # If no specific media type found but message looks like media, mark as general media
            if not media_type and re.search(r"omitted|<.*>", message, re.IGNORECASE):
                media_type = "media"
                message = ""

            group_system_flag = any(kw.lower() in original_message.lower() for kw in group_system_keywords)
            actual_sender = "group_notification" if group_system_flag else sender

            current = {
                "datetime_ist": dt_obj.isoformat(),
                "datetime_ist_human": dt_obj.strftime("%d %b %Y, %I:%M %p"),
                "datetime_utc": dt_utc.isoformat(),
                "sender": actual_sender,
                "message": message,
                "media": media_type,
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
            "message", "media", "message_modifier", "group_system_message", 
            "year", "month", "day", "hour", "minute"
        ])
    
    try:
        df = pd.DataFrame(messages)
        df["message"] = df["message"].astype(str).str.strip()
        df["message_modifier"] = df["message_modifier"].astype(str).str.strip()
        return df
    except Exception as e:
        raise ValueError(f"Error creating DataFrame: {e}")

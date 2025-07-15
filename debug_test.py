#!/usr/bin/env python3

import sys
import pandas as pd
from parser import parse_chat_file
import io

# Test with a simple sample message
sample_chat = """[25/12/23, 10:30:45 AM] John: Hello there!
[25/12/23, 10:31:22 AM] Alice: Hi John, how are you?
[25/12/23, 10:32:15 AM] John: I'm good, thanks!
"""

print("Testing parser with sample chat data...")
try:
    # Create a file-like object
    chat_file = io.StringIO(sample_chat)
    
    # Parse the chat
    df = parse_chat_file(chat_file)
    
    print(f"Successfully parsed! DataFrame shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    if len(df) > 0:
        print(f"First few rows:")
        # Check if the required columns exist
        available_cols = []
        for col in ['sender', 'message', 'datetime_ist_human']:
            if col in df.columns:
                available_cols.append(col)
        
        if available_cols:
            print(df[available_cols].head())
        else:
            print("Required columns not found. Showing all columns:")
            print(df.head())
    
except Exception as e:
    print(f"Error occurred: {e}")
    import traceback
    traceback.print_exc()

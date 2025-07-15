#!/usr/bin/env python3

import pandas as pd
import sys
sys.path.append('.')

from parser import extract_message_data
from datetime import datetime

# Create a simple test case
class MockMatch:
    def __init__(self, groups):
        self._groups = groups
    def group(self, n):
        return self._groups[n-1] if n <= len(self._groups) else None

# Test data
mock_match = MockMatch(['25/12/23', '10:30:45', 'AM', 'John', 'Hello there!'])
raw_message = '[25/12/23, 10:30:45 AM] John: Hello there!'
dt_obj = datetime.strptime('25/12/23 10:30:45 AM', '%d/%m/%y %I:%M:%S %p')
dt_utc = dt_obj

# Extract message data
msg_data = extract_message_data(mock_match, raw_message, dt_obj, dt_utc)

print("Message data keys:")
for i, key in enumerate(msg_data.keys()):
    print(f"  {i}: {repr(key)} (type: {type(key)}, len: {len(key)})")
    
print("\nCreating DataFrame...")
df = pd.DataFrame([msg_data])
print("DataFrame columns:")
for i, col in enumerate(df.columns):
    print(f"  {i}: {repr(col)} (type: {type(col)}, len: {len(col)})")
    
print(f"\nDataFrame shape: {df.shape}")
print(f"'sender' in df.columns: {'sender' in df.columns}")
print(f"List of columns: {list(df.columns)}")

# Try to access the sender column
try:
    print(f"Sender values: {df['sender'].tolist()}")
except Exception as e:
    print(f"Error accessing sender: {e}")
    
# Show the first row
print("\nFirst row:")
print(df.iloc[0])

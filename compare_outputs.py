import pandas as pd
import re

def count_words(text):
    """Count words in a message text."""
    if pd.isna(text) or text == '':
        return 0
    return len(text.split())

def compare_pc_mobile_outputs(pc_df: pd.DataFrame, mobile_df: pd.DataFrame):
    """
    Compare PC and Mobile DataFrame outputs message-by-message to identify discrepancies.
    """
    print(f"PC DataFrame: {len(pc_df)} messages")
    print(f"Mobile DataFrame: {len(mobile_df)} messages")
    print()
    
    # Calculate total word counts
    pc_total_words = pc_df['message'].apply(count_words).sum()
    mobile_total_words = mobile_df['message'].apply(count_words).sum()
    
    print(f"PC total words: {pc_total_words}")
    print(f"Mobile total words: {mobile_total_words}")
    print(f"Word count difference: {pc_total_words - mobile_total_words}")
    print()
    
    # Check for length mismatch
    if len(pc_df) != len(mobile_df):
        print(f"WARNING: DataFrames have different lengths!")
        print(f"PC: {len(pc_df)} vs Mobile: {len(mobile_df)}")
        print()
    
    # Compare messages line by line
    mismatch_count = 0
    word_diff_total = 0
    max_len = min(len(pc_df), len(mobile_df))
    
    for i in range(max_len):
        pc_message = pc_df.iloc[i]['message']
        mobile_message = mobile_df.iloc[i]['message']
        
        pc_words = count_words(pc_message)
        mobile_words = count_words(mobile_message)
        word_diff = pc_words - mobile_words
        
        if pc_message != mobile_message:
            mismatch_count += 1
            word_diff_total += word_diff
            print(f"Mismatch in message {i}:")
            print(f"PC ({pc_words} words): {repr(pc_message)}")
            print(f"Mobile ({mobile_words} words): {repr(mobile_message)}")
            print(f"Word difference: {word_diff}")
            print("---")
        elif word_diff != 0:
            # Same message content but different word counts (shouldn't happen)
            print(f"Same message but different word counts at index {i}:")
            print(f"PC ({pc_words} words): {repr(pc_message)}")
            print(f"Mobile ({mobile_words} words): {repr(mobile_message)}")
            print("---")
    
    # Check if there are extra messages in either DataFrame
    if len(pc_df) > len(mobile_df):
        print(f"Extra messages in PC DataFrame (indices {max_len} to {len(pc_df)-1}):")
        for i in range(max_len, len(pc_df)):
            extra_words = count_words(pc_df.iloc[i]['message'])
            word_diff_total += extra_words
            print(f"PC[{i}] ({extra_words} words): {repr(pc_df.iloc[i]['message'])}")
    elif len(mobile_df) > len(pc_df):
        print(f"Extra messages in Mobile DataFrame (indices {max_len} to {len(mobile_df)-1}):")
        for i in range(max_len, len(mobile_df)):
            extra_words = count_words(mobile_df.iloc[i]['message'])
            word_diff_total -= extra_words
            print(f"Mobile[{i}] ({extra_words} words): {repr(mobile_df.iloc[i]['message'])}")
    
    print(f"\nSummary:")
    print(f"Text mismatches: {mismatch_count}")
    print(f"Word count difference from mismatches: {word_diff_total}")
    print(f"Expected total difference: {pc_total_words - mobile_total_words}")
    
    if mismatch_count == 0 and pc_total_words == mobile_total_words:
        print("✓ Perfect match!")
    elif word_diff_total == (pc_total_words - mobile_total_words):
        print("✓ Word count difference explained by message differences")
    else:
        print("⚠ Word count difference NOT fully explained by message differences")

# Example usage (assuming pc_df and mobile_df are available as DataFrame variables):
# compare_pc_mobile_outputs(pc_df, mobile_df)


#!/usr/bin/env python3
"""
Script to compare PC and mobile WhatsApp chat parsing outputs
Usage: python run_comparison.py <pc_chat_file> <mobile_chat_file>
"""

import sys
from parser import parse_chat_file
from compare_outputs import compare_pc_mobile_outputs

def main():
    if len(sys.argv) != 3:
        print("Usage: python run_comparison.py <pc_chat_file> <mobile_chat_file>")
        sys.exit(1)
    
    pc_file = sys.argv[1]
    mobile_file = sys.argv[2]
    
    print(f"Parsing PC file: {pc_file}")
    pc_df = parse_chat_file(pc_file)
    print(f"PC parsing complete: {len(pc_df)} messages")
    
    print(f"\nParsing Mobile file: {mobile_file}")
    mobile_df = parse_chat_file(mobile_file)
    print(f"Mobile parsing complete: {len(mobile_df)} messages")
    
    print("\n" + "="*50)
    print("COMPARISON RESULTS")
    print("="*50)
    
    # Run the comparison
    compare_pc_mobile_outputs(pc_df, mobile_df)

if __name__ == "__main__":
    main()

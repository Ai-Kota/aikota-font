#!/usr/bin/env python3
"""
Regenerate WOFF2 from TTF with correct head.flags bit3.

This script ensures that when converting TTF to WOFF2, the bit3 flag
is always set to 1, preventing the upside-down text rendering issue.

Usage:
    python regenerate_woff2.py <input.ttf> [output.woff2]
"""
import sys
import os
from fontTools.ttLib import TTFont

def fix_and_convert(input_ttf: str, output_woff2: str) -> bool:
    """Load TTF, fix bit3, save as WOFF2."""
    try:
        f = TTFont(input_ttf)
        
        # Fix head.flags bit3
        old_flags = f['head'].flags
        new_flags = old_flags | (1 << 3)
        
        if old_flags != new_flags:
            print(f'  Fixed bit3: {bin(old_flags)} -> {bin(new_flags)}')
        else:
            print(f'  bit3 already correct: {bin(new_flags)}')
        
        f['head'].flags = new_flags
        
        # Save as WOFF2
        f.save(output_woff2)
        print(f'  Saved: {output_woff2}')
        return True
    except Exception as e:
        print(f'ERROR: {e}')
        return False

def main():
    if len(sys.argv) < 2:
        print('Usage: python regenerate_woff2.py <input.ttf> [output.woff2]')
        sys.exit(1)
    
    input_ttf = sys.argv[1]
    
    # Auto-generate output path if not provided
    if len(sys.argv) >= 3:
        output_woff2 = sys.argv[2]
    else:
        base, _ = os.path.splitext(input_ttf)
        output_woff2 = base + '.woff2'
    
    if not os.path.exists(input_ttf):
        print(f'ERROR: Input file not found: {input_ttf}')
        sys.exit(1)
    
    print(f'Input: {input_ttf}')
    print(f'Output: {output_woff2}')
    print()
    
    if fix_and_convert(input_ttf, output_woff2):
        print()
        print('SUCCESS: Font converted with bit3=1')
    else:
        print()
        print('FAILED: Could not convert font')
        sys.exit(1)

if __name__ == '__main__':
    main()

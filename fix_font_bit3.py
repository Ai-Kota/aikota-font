#!/usr/bin/env python3
"""
Fix head.flags bit3 in TrueType/WOFF2 fonts.

This script fixes fonts that have bit3=0 in head.flags, which causes
browsers to render glyphs with inverted Y coordinates (upside-down text).

Usage:
    python fix_font_bit3.py <path/to/font.ttf> [path/to/font2.ttf ...]
    python fix_font_bit3.py <directory/>
"""
import os
import sys
from fontTools.ttLib import TTFont

def fix_font(font_path: str) -> bool:
    """Fix bit3 in head.flags. Returns True if fixed."""
    try:
        f = TTFont(font_path)
        old_flags = f['head'].flags
        new_flags = old_flags | (1 << 3)  # Set bit3
        if old_flags != new_flags:
            f['head'].flags = new_flags
            f.save(font_path)
            return True
        return False
    except Exception as e:
        print(f'ERROR: {font_path}: {e}')
        return False

def main():
    if len(sys.argv) < 2:
        print('Usage: python fix_font_bit3.py <font_file.ttf> [font_file2.ttf ...]')
        print('   or: python fix_font_bit3.py <directory/>')
        sys.exit(1)
    
    fixed = 0
    for arg in sys.argv[1:]:
        if os.path.isdir(arg):
            # Fix all ttf/woff2 files in directory
            for fname in os.listdir(arg):
                if fname.endswith('.ttf') or fname.endswith('.woff2'):
                    path = os.path.join(arg, fname)
                    if fix_font(path):
                        fixed += 1
                        print(f'Fixed: {path}')
        elif os.path.isfile(arg):
            if arg.endswith('.ttf') or arg.endswith('.woff2'):
                if fix_font(arg):
                    fixed += 1
                    print(f'Fixed: {arg}')
    
    print(f'Total fixed: {fixed}')

if __name__ == '__main__':
    main()

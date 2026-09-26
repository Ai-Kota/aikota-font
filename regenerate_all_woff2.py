#!/usr/bin/env python3
"""Regenerate all aikota woff2 files with correct bit3."""
import os
from fontTools.ttLib import TTFont

# Source TTF directory
ttf_dir = r'E:/AImlyForge/tools/media-factory/AimlyVideo/resource/fonts'
# Output woff2 directory
woff2_dir = r'E:/AImlyForge/tools/media-factory/cut/cut-motion/jobs/font-test-job/hyperframes/assets/fonts'

# Also update AimlyVideo woff2 dir
aimlywoff_dir = r'E:/AImlyForge/tools/media-factory/AimlyVideo/resource/fonts'

fixed = 0
for fname in os.listdir(ttf_dir):
    if not fname.startswith('aikota-c-') or not fname.endswith('.ttf'):
        continue
    if fname.endswith('_hinted.ttf'):
        continue
    
    style = fname.replace('aikota-c-', '').replace('.ttf', '')
    ttf_path = os.path.join(ttf_dir, fname)
    woff2_path = os.path.join(woff2_dir, f'aikota-c-{style}.woff2')
    aimlywoff_path = os.path.join(aimlywoff_dir, f'aikota-c-{style}.woff2')
    
    try:
        f = TTFont(ttf_path)
        old_flags = f['head'].flags
        new_flags = old_flags | (1 << 3)
        f['head'].flags = new_flags
        f.save(woff2_path)
        # Copy to AimlyVideo too
        import shutil
        shutil.copy2(woff2_path, aimlywoff_path)
        fixed += 1
        print(f'Generated: aikota-c-{style}.woff2')
    except Exception as e:
        print(f'ERROR {fname}: {e}')

print(f'Total regenerated: {fixed}')

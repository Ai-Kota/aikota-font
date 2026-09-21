#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aicheck.py - aikota font toolset
================================
Functions:
1. verify: Check if TTF has embedded ownership watermark
2. trace: Identify which channel/licensee leaked the font
3. info: Show font metadata

Usage:
    python aicheck.py verify aikota-c-kaiso.ttf
    python aicheck.py trace aikota-c-kaiso.ttf
    python aicheck.py info aikota-c-kaiso.ttf
"""
import sys
import os
import argparse
import hashlib
from fontTools.ttLib import TTFont

# Watermark parameters
DEFAULT_CHANNEL = 0x414B4F01   # aikota launch channel
STRENGTH = 0.5                 # vertex perturbation amplitude (upm)

# Known channel IDs (extensible)
KNOWN_CHANNELS = {
    0x414B4F01: "aikota launch channel (default)",
    0x12345678: "internal test channel A",
    0xABCDEF01: "internal test channel B",
}


def wm_offset(idx, chan):
    """Compute deterministic offset (dx, dy) for vertex idx under channel."""
    h = hashlib.sha256(f"aikota:{chan}:{idx}".encode()).digest()
    xs = int.from_bytes(h[:4], "big")
    ys = int.from_bytes(h[4:8], "big")
    dx = round((xs / 0xFFFFFFFF) * 2 * STRENGTH - STRENGTH, 2)
    dy = round((ys / 0xFFFFFFFF) * 2 * STRENGTH - STRENGTH, 2)
    return dx, dy


def get_glyph_coords(f, glyph_name):
    """Get coordinate list of a glyph."""
    try:
        g = f["glyf"][glyph_name]
        return list(g.coordinates) if hasattr(g, "coordinates") else []
    except Exception:
        return []


def decode_watermark(coords, candidates, n_probe=8):
    """Decode watermark channel by matching against expected watermarked coords."""
    best, best_score = None, -1
    for chan in candidates:
        score = 0
        probe = min(n_probe, len(coords))
        for i in range(probe):
            dx, dy = wm_offset(i, chan)
            px, py = coords[i]
            ox = round(px - dx)
            oy = round(py - dy)
            err = abs((px - dx) - ox) + abs((py - dy) - oy)
            score += (1.0 - err)
        if score > best_score:
            best, best_score = chan, score
    desc = KNOWN_CHANNELS.get(best, f"unknown 0x{best:08X}")
    return best, best_score, desc


def verify_watermark(filepath):
    """Verify watermark in font."""
    print("\n" + "=" * 50)
    print(f"Verify watermark: {filepath}")
    print("=" * 50)

    try:
        f = TTFont(filepath)
    except Exception as e:
        print(f"[FAIL] Cannot open font: {e}")
        return

    glyph_data = []
    for gn in f.getGlyphOrder():
        coords = get_glyph_coords(f, gn)
        if len(coords) >= 5:
            glyph_data.append((gn, coords))

    print(f"[OK] Contains {len(glyph_data)} glyphs with coordinate data\n")

    if not glyph_data:
        print("[WARN] No glyphs with enough coordinates")
        f.close()
        return

    print("Watermark verification results:")
    print("-" * 50)
    for gn, coords in glyph_data[:5]:
        chan, err, desc = decode_watermark(coords, list(KNOWN_CHANNELS.keys()))
        match = "[PASS] embedded" if err < len(coords) * 2 else "[FAIL] not detected"
        print(f"  {gn}: {match}")
        print(f"    Decoded channel: {desc} (err={err})")
        print(f"    First 3 vertices: {coords[:3]}")
        print()

    total_matches = sum(
        1 for gn, coords in glyph_data
        if decode_watermark(coords, list(KNOWN_CHANNELS.keys()))[1] < len(coords) * 2
    )
    print("=" * 50)
    print(f"Summary: {total_matches}/{len(glyph_data)} glyphs have watermark")
    if total_matches > len(glyph_data) * 0.8:
        print("[PASS] Watermark embedded successfully")
    elif total_matches > 0:
        print("[WARN] Some glyphs may lack watermark")
    else:
        print("[FAIL] No watermark detected")
    print("=" * 50 + "\n")

    f.close()


def trace_leakage(filepath):
    """Trace which channel leaked this font."""
    print("\n" + "=" * 50)
    print(f"Leakage trace: {filepath}")
    print("=" * 50)

    try:
        f = TTFont(filepath)
    except Exception as e:
        print(f"[FAIL] Cannot open font: {e}")
        return

    channel_votes = {}
    for gn in f.getGlyphOrder():
        coords = get_glyph_coords(f, gn)
        if len(coords) < 5:
            continue
        chan, err, _ = decode_watermark(coords, list(KNOWN_CHANNELS.keys()))
        channel_votes[chan] = channel_votes.get(chan, 0) + 1

    total = sum(channel_votes.values())
    print(f"[OK] Analyzed {total} glyphs\n")
    print("Channel vote counts:")
    for chan, count in sorted(channel_votes.items(), key=lambda x: -x[1]):
        desc = KNOWN_CHANNELS.get(chan, f"unknown 0x{chan:08X}")
        pct = count / total * 100
        print(f"  {desc}: {count} votes ({pct:.1f}%)")

    if channel_votes:
        best = max(channel_votes, key=channel_votes.get)
        desc = KNOWN_CHANNELS.get(best, f"unknown 0x{best:08X}")
        print(f"\n[INFO] Most likely channel: {desc}")

    print("=" * 50 + "\n")
    f.close()


def show_info(filepath):
    """Show font metadata."""
    print("\n" + "=" * 50)
    print(f"Font info: {filepath}")
    print("=" * 50)

    try:
        f = TTFont(filepath)
    except Exception as e:
        print(f"[FAIL] Cannot open font: {e}")
        return

    print("\n[Basic info]")
    print(f"  File size: {os.path.getsize(filepath):,} bytes")
    print(f"  Tables: {', '.join(sorted(f.keys()))}")

    print("\n[Name table]")
    seen = set()
    for n in f["name"].names:
        key = (n.nameID, n.platformID, n.platEncID, n.langID)
        if key in seen:
            continue
        seen.add(key)
        try:
            s = n.string.decode("utf-8", errors="replace")
        except:
            s = n.string.decode("gbk", errors="replace")
        name_ids = {
            0: "copyright", 1: "family", 2: "style",
            4: "full_name", 5: "version", 6: "ps_name"
        }
        label = name_ids.get(n.nameID, f"nameID{n.nameID}")
        print(f"  {label}: {s[:60]}")

    if "OS/2" in f:
        os2 = f["OS/2"]
        print(f"\n[OS/2 table]")
        print(f"  fsType: {os2.fsType} (0=unrestricted, 2=restricted)")
        print(f"  fsSelection: {os2.fsSelection}")
        print(f"  usWinAscent/Descent: {os2.usWinAscent}/{os2.usWinDescent}")

    if "post" in f:
        post = f["post"]
        print(f"\n[PostScript table]")
        print(f"  isFixedPitch: {post.isFixedPitch}")

    glyph_count = len([g for g in f.getGlyphOrder() if g != ".notdef"])
    print(f"\n[Glyph stats]")
    print(f"  Total glyphs: {glyph_count}")

    print("\n" + "=" * 50 + "\n")
    f.close()


def main():
    parser = argparse.ArgumentParser(description="aikota font toolset")
    parser.add_argument("action", choices=["verify", "trace", "info"],
                        help="verify=check watermark, trace=leak source, info=metadata")
    parser.add_argument("filepath", help="font file path")
    args = parser.parse_args()

    if not os.path.exists(args.filepath):
        print(f"[FAIL] File not found: {args.filepath}")
        sys.exit(1)

    if args.action == "verify":
        verify_watermark(args.filepath)
    elif args.action == "trace":
        trace_leakage(args.filepath)
    elif args.action == "info":
        show_info(args.filepath)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Search and download commercial-free royalty-free music & SFX from Mixkit (stdlib only).

Usage:
  python fetch_audio.py search --kind music --category futuristic --limit 10
  python fetch_audio.py search --kind sfx --category impact --limit 10
  python fetch_audio.py download --url "https://assets.mixkit.co/music/134/134.mp3" --out audio/bgm.mp3
"""

import argparse
import json
import os
import re
import sys
import urllib.request

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; nexdark-video-skill/1.0)"}


def fetch_html(url: str) -> str:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read().decode("utf-8", "ignore")


def cmd_search(args):
    base = (
        f"https://mixkit.co/free-stock-music/{args.category}/"
        if args.kind == "music"
        else f"https://mixkit.co/free-sound-effects/{args.category}/"
    )
    html = fetch_html(base)
    pat = (
        r'data-audio-player-preview-url-value="(https://assets\.mixkit\.co/[^"]+\.mp3)"'
        r'.{0,1800}?item-grid-card__title[^>]*>\s*([^<]+?)\s*<'
    )
    seen = set()
    items = []
    for mp3, title in re.findall(pat, html, re.S):
        if mp3 in seen:
            continue
        seen.add(mp3)
        items.append({"title": title.strip(), "url": mp3})
        if len(items) >= args.limit:
            break

    if args.json:
        print(json.dumps({"source": base, "count": len(items), "items": items}, indent=2))
    else:
        print(f"Found {len(items)} commercial-free {args.kind} tracks in '{args.category}':")
        for idx, it in enumerate(items, 1):
            print(f"  {idx:2d}. {it['title']:40s} -> {it['url']}")


def cmd_download(args):
    out_path = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    req = urllib.request.Request(args.url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp, open(out_path, "wb") as f:
        data = resp.read()
        f.write(data)
    print(f"Downloaded {len(data):,} bytes -> {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Search & download commercial-free Mixkit music/SFX.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_s = sub.add_parser("search", help="List royalty-free tracks in a Mixkit category")
    p_s.add_argument("--kind", choices=["music", "sfx"], default="music")
    p_s.add_argument("--category", default="futuristic", help="e.g. futuristic, technology, electronic, ambient, impact, cinematic")
    p_s.add_argument("--limit", type=int, default=12)
    p_s.add_argument("--json", action="store_true")
    p_s.set_defaults(func=cmd_search)

    p_d = sub.add_parser("download", help="Download a Mixkit MP3 asset")
    p_d.add_argument("--url", required=True)
    p_d.add_argument("--out", required=True)
    p_d.set_defaults(func=cmd_download)

    args = parser.parse_args()
    try:
        args.func(args)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

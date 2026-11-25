#!/usr/bin/env python3
"""FFmpeg cinema color-grading, 35mm organic grain, optional 4K upscale & QA frame extractor (stdlib only).

Presets:
  obsidian-gold  : Cool obsidian-teal shadows, champagne-gold highlights, light 35mm grain
  kodak-halation : Filmic S-curve, red-channel highlight halation, temporal-uniform grain
  apple-clean    : Pure OLED blacks, crisp UI/product fidelity, subtle micro-sharpening

Usage:
  python grade_master.py --input raw_master.mp4 --output final_1080p60.mp4 --preset obsidian-gold --qa-times 2.5,5.0,10.0,18.0
  python grade_master.py --input final_1080p60.mp4 --output final_4k60.mp4 --preset apple-clean --upscale-4k
"""

import argparse
import os
import subprocess
import sys


def build_filter_args(preset: str, upscale_4k: bool):
    scale_suffix = ",scale=3840:2160:flags=lanczos,unsharp=5:5:0.30:5:5:0.0" if upscale_4k else ""

    if preset == "obsidian-gold":
        vf = (
            "colorbalance=rs=-0.025:gs=-0.008:bs=0.032:rm=0.008:gm=0.0:bm=-0.008:"
            "rh=0.042:gh=0.016:bh=-0.032,"
            "eq=contrast=1.06:saturation=1.07:gamma=0.98,"
            "unsharp=5:5:0.42:5:5:0.0,"
            "noise=alls=3:allf=t"
            + scale_suffix
        )
        return ["-vf", vf]

    if preset == "apple-clean":
        vf = (
            "eq=contrast=1.04:saturation=1.03:gamma=0.99,"
            "unsharp=5:5:0.30:5:5:0.0"
            + scale_suffix
        )
        return ["-vf", vf]

    if preset == "kodak-halation":
        fc = (
            "[0:v]format=gbrp,"
            "curves=m='0/0.02 0.16/0.11 0.5/0.49 0.85/0.90 1/0.98':"
            "r='0/0 0.5/0.48 1/1':b='0/0.02 0.5/0.51 1/0.97'[graded];"
            "[graded]split=2[base][hl];"
            "[hl]lutyuv=y='if(gt(val,205),val,0)':u=128:v=128,"
            "gblur=sigma=14,colorbalance=rs=0.45:gs=-0.15:bs=-0.35[hal];"
            "[base][hal]blend=all_mode='screen':all_opacity=0.22[with_hal];"
            f"[with_hal]noise=alls=7:allf=t+u{scale_suffix},format=yuv420p[vout]"
        )
        return ["-filter_complex", fc, "-map", "[vout]", "-map", "0:a?"]

    raise ValueError(f"Unknown preset: {preset}")


def main():
    p = argparse.ArgumentParser(description="Cinema color grade & QA frame extractor via FFmpeg.")
    p.add_argument("--input", required=True, help="Input MP4 path")
    p.add_argument("--output", required=True, help="Output graded MP4 path")
    p.add_argument("--preset", choices=["obsidian-gold", "kodak-halation", "apple-clean"], default="obsidian-gold")
    p.add_argument("--crf", type=int, default=15)
    p.add_argument("--upscale-4k", action="store_true", help="Upscale cleanly to 3840x2160 Lanczos 4K")
    p.add_argument("--qa-times", default="", help="Comma-separated timestamps in seconds to extract QA PNGs into _qa/")
    args = p.parse_args()

    in_path = os.path.abspath(args.input)
    out_path = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    filter_args = build_filter_args(args.preset, args.upscale_4k)
    cmd = [
        "ffmpeg", "-y", "-i", in_path,
        *filter_args,
        "-c:v", "libx264", "-profile:v", "high", "-crf", str(args.crf),
        "-preset", "slow", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart",
        out_path,
    ]
    print(f"[grade_master] Grading ({args.preset}, crf={args.crf}, 4k={args.upscale_4k}) -> {out_path}")
    subprocess.run(cmd, check=True)

    if args.qa_times.strip():
        qa_dir = os.path.join(os.path.dirname(out_path), "_qa")
        os.makedirs(qa_dir, exist_ok=True)
        for idx, ts in enumerate(t.strip() for t in args.qa_times.split(",") if t.strip()):
            png = os.path.join(qa_dir, f"qa_{idx+1:02d}_{ts.replace('.', 'p')}s.png")
            subprocess.run(
                ["ffmpeg", "-y", "-ss", ts, "-i", out_path, "-frames:v", "1", png],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            print(f"[grade_master] Extracted QA frame -> {png}")

    print(f"[grade_master] Done: {out_path} ({os.path.getsize(out_path):,} bytes)")


if __name__ == "__main__":
    main()

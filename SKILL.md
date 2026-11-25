---
name: nexdark-video-skill
description: >
  Universal studio-grade video director, motion-graphics, and film-mastering skill for AI coding
  agents (Antigravity, Claude Code, Codex, Cursor, Gemini CLI). Directs, renders, and color-grades
  pro 16:9, 9:16 (Reels/Shorts/TikTok), and 4K product launch films, 3D/Blender showreels, SaaS/web
  promos, After Effects-style kinetic typography, and beat-locked clip edits using HyperFrames,
  GSAP, FFmpeg, and optional Blender — with strict zero-AI-slop design, real commercial-free audio,
  and mandatory visual QA frame inspection.
license: MIT
metadata:
  author: Mohammed Safwan (NexDark Labs)
  repository: https://github.com/MohammedSafwan10/nexdark-video-skill
---

# NexDark Video Director Skill (`nexdark-video-skill`)

Turn any AI coding agent into a **studio-grade creative director, motion designer, and finishing colorist** across **Windows, macOS, and Linux** — using 100% free, cross-platform tools (**HyperFrames + GSAP 3 + FFmpeg + optional Blender 4.2+/5.x**).

---

## Mandatory Operating Rules (Zero AI Slop)

Follow these non-negotiable standards on every single video:

1. **Research & Plan-Before-Render Gate (MANDATORY):**
   - Before writing composition code or rendering heavy footage, research reference studio pacing for the user's domain (e.g., Apple Hardware Films, Anthropic launch spots, ManvsMachine, Tendril, Porsche Design, Stripe/Linear SaaS films) and present a concise **Act-by-Act Shot Plan** (duration, aspect ratio, footage sources, audio vibe, typography, and color grade) for user approval.
2. **Real Motion First — Intentional Stills Only:**
   - **Never** build a lazy PowerPoint slideshow of static images slowly zooming.
   - Anchor every film with **real moving footage**: live 3D camera orbits (`scripts/blender_pass.py`), live 60fps browser/UI captures (`hyperframes capture`), or real user video clips.
   - Use high-resolution **static images intentionally** only where real commercial directors do: rapid-fire 4-frame macro match-cuts, 3-up vertical architectural strips, or 3D-perspective Bento/Vault mosaic wall pull-backs with parallax motion.
3. **Zero Synthetic Beeps & Zero Cheesy Whoosh Spam:**
   - **Never** synthesize robotic sine-wave music/SFX in Python, and **never** slap loud stock whooshes on every cut (that screams CapCut template).
   - Fetch real **commercial-free / royalty-free music** via `scripts/fetch_audio.py` (Mixkit / CC0), detect exact beat timestamps with `hyperframes beats`, normalize to **`-14 LUFS`**, and let **hard cuts snap silently right on the drum/bass transients** (at most 1 subtle low sub-hit on the final brand monument).
4. **Anti-Slop Visual & Typography Discipline:**
   - **Banned:** Generic neon blue/purple gradients, blurry fade-in slides, cluttered noisy HUD widgets, stock rounded SaaS pills, linear easing (`ease: "none"` on UI entrances), and unreadable low-contrast text.
   - **Required:** High-contrast editorial pairing (e.g., `Instrument Serif` / `Playfair Display` + `Space Grotesk` / `Inter` + disciplined `JetBrains Mono` micro-specs), razor-thin `1px` architectural hairlines, Apple-style baseline-masked reveals (`overflow: hidden` + `expo.out`), and generous negative space.
5. **Strict Aspect-Ratio & Framing Verification:**
   - Always adapt camera distance and layout to the target aspect ratio (**`16:9` `1920×1080`**, **`9:16` `1080×1920` Reels/Shorts/TikTok**, or **`1:1` `1080×1080`**).
   - For `9:16` vertical video, enforce the **Cross-Platform Golden Safe Zone** (see `references/formats-and-safezones.md` — keep all hooks, titles, and CTAs clear of Top `250px`, Bottom `380px`, Right `120px`).
   - For tall 3D subjects (characters/products) rendered from `4:3` studio cameras into `16:9`, pull camera distance back `1.32x–1.42x` so heads/tops are never cropped.
6. **Mandatory Visual QA Gate Before Delivery:**
   - Never deliver an uninspected MP4. Extract 4–5 key frames across every major act (`scripts/grade_master.py --qa-times ...`) and visually inspect them to verify framing, headroom, typography legibility, wipe alignment, and color grade before presenting the final video to the user.

---

## Supported Production Modes (Auto-Select by Request)

| Mode | Best For | Primary Footage Sources | Signature Motion Techniques |
|---|---|---|---|
| **A. 3D / Blender Showreel** | 3D asset stores, industrial design, game studios | `scripts/blender_pass.py` (dual-pass Beauty + Clay-Wireframe orbits) | Synchronized 2-up split-screens, diagonal laser Wireframe → Beauty wipes, 1s topology match-flashes, 3D vault mosaic wall |
| **B. Website / SaaS / App Launch** | Startups, dev tools, portfolios, product launches | `hyperframes capture` (live 60fps UI/scroll) + screen recordings | RSVP kinetic serif opener, baseline-masked feature callouts, floating 3D browser cards, dark-void OLED contrast |
| **C. Pure Motion Graphics / Promo** | Brand reveals, announcements, kinetic typography | HyperFrames + GSAP 3 + SVG + CSS 3D + high-res product stills | Waveform pacing (`Chaos → Calm → Climax`), ticking telemetry counters, 3-up vertical strips, architectural hairlines |
| **D. Raw Clip / Social Reels Edit** | User-supplied footage, vlogs, Reels/Shorts/TikTok | User MP4/MOV clips + `hyperframes beats` | Beat-locked hard cuts, speed-ramps, 9:16 Golden Safe Zone typography, analog Kodak halation grade |

---

## End-to-End Studio Workflow (6 Stages)

### Stage 0 — Prerequisite Check (Cross-Platform)
Verify `node`, `ffmpeg`, `ffprobe`, `python` (or `uv`), and `hyperframes` (`npm install -g hyperframes`).
- Keep all render caches inside the active project folder using `--frames-cache-dir ./.cache` so OS system drives stay clean.
- Read the deep-dive references before authoring:
  - `references/pacing-and-motion.md` — ManvsMachine / Tendril / Apple pacing, RSVP, easing curves, split-screens, laser wipes, 3D vault walls.
  - `references/formats-and-safezones.md` — `16:9`, `9:16` Reels/Shorts/TikTok safe-zone pixel budgets, `1:1`, and 4K YouTube mastering.
  - `references/color-and-audio.md` — FFmpeg film emulation (`obsidian-gold`, `kodak-halation`, `apple-clean`), 35mm grain, `-14 LUFS` audio mixing.

### Stage 1 — Research & Shot Plan Approval
1. Inspect the user's source assets (website URL, `.blend` files, product renders, or raw clips).
2. Propose a concise **Act-by-Act Blueprint** (target length `15–45s`, aspect ratio, music mood, footage plan, motion style, color preset) and wait for approval.

### Stage 2 — Source Footage & Real Audio Acquisition
- **Real Commercial-Free Audio:**
  ```bash
  python scripts/fetch_audio.py search --category futuristic --limit 10
  python scripts/fetch_audio.py download --url "https://assets.mixkit.co/music/134/134.mp3" --out audio/bgm.mp3
  hyperframes beats audio/bgm.mp3
  ```
- **Optional 3D Dual-Pass Footage (Blender 4.2+/5.x):**
  ```bash
  blender --background --python scripts/blender_pass.py -- --blend path/to/model.blend --out raw_clips/hero --res 1920x1080 --frames 54 --samples 36
  ```
  Produces pixel-aligned `hero_beauty.mp4` and `hero_wire.mp4` on the exact same animated camera orbit (automatically preserving original raw clips for the user!).
- **Mix Master Audio (`-14 LUFS`, zero whoosh spam):**
  Use FFmpeg `afade` + `loudnorm=I=-14:TP=-1.2:LRA=9` trimmed to exact bar multiples of the detected BPM (e.g., `125 BPM` = `0.48s/beat`, `1.92s/bar`).

### Stage 3 — Author the HyperFrames + GSAP Composition
- Match every `<video>` `data-duration` closely to its native clip length (`1.0x–1.25x` max) so there are **zero frozen frames and zero slow-mo stutter**.
- Register `window.__timelines["main"] = tl;` with `gsap.timeline({ paused: true })`.
- Apply exact safe-zone margins for `9:16` vertical projects (`width: 1080px; height: 1920px`).

### Stage 4 — Render 60fps Raw Master
```bash
hyperframes render --fps 60 --quality high --frames-cache-dir ./.cache -o raw_master.mp4
```

### Stage 5 — Cinema Color Grade, Optional 4K Upscale & Mandatory QA Frame Check
```bash
python scripts/grade_master.py --input raw_master.mp4 --output final_1080p60.mp4 --preset obsidian-gold --qa-times 2.5,5.0,8.0,12.5,19.0
```
- **Visually inspect every extracted PNG in `_qa/`**. If any subject head is clipped, text overlaps a `9:16` UI zone, or contrast looks muddy, fix and re-render before delivery.
- Only generate a **4K (`3840×2160`) YouTube master** (`--upscale-4k`) once the user approves the native `1080p60` master (or if explicitly requested upfront).

### Stage 6 — Cleanup & Delivery
- Delete temporary `.cache/`, `_qa/`, and `raw_master.mp4`.
- **Always preserve** the user's clean raw source clips (`raw_clips/`), editable composition (`index.html`), and final graded master MP4.

# Cinema Color Grading, Film Emulation & Broadcast Audio Mastering

Color grading and sound design are what separate a $50 template from a $50,000 commercial film.

---

## 1. The 3 Built-In FFmpeg Film Presets (`scripts/grade_master.py`)

### Preset 1: `obsidian-gold` (Luxury Hardware, 3D, Automotive, Architecture)
Cool obsidian-teal shadow depth + warm champagne-gold highlight roll-off + subtle micro-sharpening + light temporal 35mm grain (`alls=3`):
```text
colorbalance=rs=-0.025:gs=-0.008:bs=0.032:rm=0.008:gm=0.0:bm=-0.008:rh=0.042:gh=0.016:bh=-0.032,
eq=contrast=1.06:saturation=1.07:gamma=0.98,
unsharp=5:5:0.42:5:5:0.0,
noise=alls=3:allf=t
```

### Preset 2: `kodak-halation` (Analog 35mm Cinema, Brand Films, Live-Action / Reels)
Filmic S-curve (lifted matte blacks + protected highlights) + true analog **red-channel highlight halation** (`lutyuv` > 205 -> Gaussian blur `sigma=14` -> warm red-orange tint -> `screen` blend at `22%`) + organic temporal-uniform grain (`alls=7:allf=t+u`):
```text
[0:v]format=gbrp,curves=m='0/0.02 0.16/0.11 0.5/0.49 0.85/0.90 1/0.98':r='0/0 0.5/0.48 1/1':b='0/0.02 0.5/0.51 1/0.97'[graded];
[graded]split=2[base][hl];
[hl]lutyuv=y='if(gt(val,205),val,0)':u=128:v=128,gblur=sigma=14,colorbalance=rs=0.45:gs=-0.15:bs=-0.35[hal];
[base][hal]blend=all_mode='screen':all_opacity=0.22[with_hal];
[with_hal]noise=alls=7:allf=t+u,format=yuv420p[out]
```

### Preset 3: `apple-clean` (SaaS, Dev Tools, Minimal Product UI)
Pure OLED blacks, neutral accurate UI colors, gentle contrast polish, razor-sharp text edges, zero muddy color cast:
```text
eq=contrast=1.04:saturation=1.03:gamma=0.99,
unsharp=5:5:0.30:5:5:0.0
```

> **Encoding Rule:** Organic film grain defeats naive bitrate targets. Always encode graded masters with `-crf 15` to `-crf 17` and `-preset slow` so dark gradients never band or macroblock.

---

## 2. Audio Discipline (Zero AI-Slop Sound)

### Strict Rules
1. **NEVER synthesize music or SFX with Python sine waves** — synthetic beeps sound immediately amateur.
2. **NEVER spam stock whooshes on every cut** — real commercial films let the **music track's own drum/bass transients** carry 95% of the cuts silently.
3. **Use at most 1–2 restrained accents** across a 20–35s film (e.g., one subtle low-end sub-impact at `-9 dB` on the final brand monument reveal).

### Recommended Commercial-Free Workflow
1. Search & download a high-production royalty-free track via `scripts/fetch_audio.py` (Mixkit Commercial License — zero attribution required).
   - **Luxury Hardware / 3D / Tech:** `futuristic`, `technology`, `electronic` (look for minimal 118–128 BPM tracks like *Deep Techno Ambience* or *Cyberpunk City*).
   - **SaaS / Editorial / Calm:** `ambient`, `minimal`, `chill`.
2. Detect the exact beat grid:
   ```bash
   hyperframes beats audio/bgm.mp3
   ```
3. Skip slow ambient intros (`-ss`) so the groove enters immediately within the first 1–2 seconds, trim to an exact bar multiple, apply smooth `afade` in/out, and master to broadcast **`-14 LUFS`** (`-1.2 dBTP` true peak):
   ```bash
   ffmpeg -y -ss 15.36 -t 26.40 -i audio/bgm.mp3 \
     -af "afade=t=in:st=0:d=0.5,afade=t=out:st=23.6:d=2.8,loudnorm=I=-14:TP=-1.2:LRA=9" \
     -ar 48000 -ac 2 audio/master_audio.wav
   ```

# Aspect Ratios, 9:16 Safe Zones & Delivery Specifications

Always design composition geometry specifically for the target platform — **never** naively center-crop a 16:9 widescreen edit into 9:16 vertical without re-framing typography and subject distance.

---

## 1. Standard Master Resolutions

| Format | Aspect | Resolution | Frame Rate | Best Platforms |
|---|---|---|---|---|
| **Landscape Master** | `16:9` | `1920 x 1080` | `60 fps` | YouTube, X, LinkedIn, Product Hero Websites |
| **4K Archive / YouTube** | `16:9` | `3840 x 2160` | `60 fps` | YouTube (triggers high-bitrate VP9/AV1 4K stream), Vimeo |
| **Vertical Short-Form** | `9:16` | `1080 x 1920` | `60 fps` (or `30 fps`) | Instagram Reels, YouTube Shorts, TikTok |
| **Square Feed** | `1:1` | `1080 x 1080` | `60 fps` | Instagram Grid, LinkedIn Carousel, Product Cards |

---

## 2. Cross-Platform 9:16 "Golden Safe Zone" (`1080 x 1920`)

Instagram Reels, TikTok, and YouTube Shorts all overlay opaque UI buttons, captions, and channel info over the edges of vertical video. If a single vertical export must work cleanly across **all three platforms**, place ALL hooks, titles, captions, and CTAs strictly inside the **Golden Safe Box (`870 x 1360 px`)**:

```text
+------------------------------------------+  y = 0
|         TOP DANGER ZONE (250 px)         |  (Reels camera/header, Shorts tags)
+----+--------------------------------+----+  y = 250
|    |                                |    |
| 60 |                                | 150|
| px |       GOLDEN SAFE ZONE         | px |  (Right 120-150px: Like, Comment,
|    |         870 x 1290 px          |    |   Share, Bookmark icon stack)
|    |    (Center focal subject &     |    |
|    |     all typography here!)      |    |
+----+--------------------------------+----+  y = 1540
|                                          |
|       BOTTOM DANGER ZONE (380 px)        |  (Handle, caption, Subscribe, audio)
|                                          |
+------------------------------------------+  y = 1920
```

### CSS Safe-Zone Variables for `9:16` HyperFrames Projects
```css
:root {
  --safe-top: 250px;
  --safe-bottom: 380px;
  --safe-left: 64px;
  --safe-right: 150px;
}
```
- **Platform nuances:**
  - **YouTube Shorts** has the heaviest bottom-left crowding (`~380 px`) due to Subscribe button + title text.
  - **Instagram Reels** crops to `4:5` in the main feed and `1:1` on profile grids — keep the primary subject and hero hook vertically centered around `y = 650–1250 px`.
- **9:16 Split-Screens:** Switch horizontal 2-up (`left | right`) splits to **stacked vertical 2-up (`top / bottom`)** separated by a `1px` horizontal hairline so each half stays wide and readable on phones!

---

## 3. 3D / Blender Camera Framing by Aspect Ratio
- **4:3 Studio Cameras -> 16:9 Widescreen:** Pulling a tall vertical model (e.g., humanoid robot, bottle, standing character) from a `4:3` camera into `16:9` clips the top and bottom unless camera distance is multiplied by **`1.32x – 1.42x`**.
- **9:16 Vertical 3D Renders:** Keep horizontal products (cars, engines) pulled back `1.55x–1.75x` OR use a dynamic vertical pan/tilt + stacked top/bottom detail framing.

---

## 4. Encoding & Platform Delivery Targets
- **Master Archive (`1080p60`):** `libx264 -profile:v high -crf 15 -preset slow -pix_fmt yuv420p -c:a aac -b:a 320k -movflags +faststart`
- **4K YouTube Master (`2160p60`):** Upscale native 1080p master cleanly with `scale=3840:2160:flags=lanczos,unsharp=5:5:0.35:5:5:0.0` at `-crf 16` (or render native 4K for hero stills/overnight batches).
- **WhatsApp / Fast Social Share:** Keep under `16 MB` (`-crf 22`) or instruct the user to send the full master as **HD / Document** to avoid aggressive platform re-compression.

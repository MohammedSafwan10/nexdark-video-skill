# Studio Pacing, Motion Grammar & After Effects-Style Techniques

Distilled from top commercial studios (**ManvsMachine**, **Tendril**, **Apple Hardware Films**, **Anthropic**, **Porsche Design**) and engineered for **HyperFrames + GSAP 3 + CSS 3D**.

---

## 1. The Waveform Pacing Rule (`Chaos -> Calm -> Climax`)
Amateurs cut every shot at the exact same length (boring) or cut everything frantically (exhausting). Structure every 15–45s film like a musical waveform:
- **Hook (`0–4s`):** High-contrast minimal opener (OLED black + RSVP kinetic serif or hypnotic slow macro shot) that immediately proves studio taste.
- **Technical Escalation (`4–16s`):** Beat-locked hard cuts, 2-up synchronized split-screens, and short 1–2s wireframe/UI breakdown flashes.
- **Breathing Climax (`16–24s`):** Tighter 2.39:1 anamorphic bars + lingering hero shot with a single dramatic diagonal reveal wipe.
- **Scale Proof / Vault Wall (`24–30s`):** 3D-perspective pull-back revealing the full catalog, UI grid, or product family in counter-scrolling architectural rows.
- **Monument Outro (`last 4–5s`):** Clean negative space, hairline divider, wordmark, and URL fading smoothly to black.

---

## 2. Easing Curves (The "Apple / Studio Feel")
**Never** use `linear` (`ease: "none"`) on typography or UI entrances — linear motion looks robotic. Use `none` ONLY on continuous background parallax/scroll lanes.

| Motion Role | GSAP Ease | CSS Equivalent | Feel |
|---|---|---|---|
| Typography / Title Mask Reveal | `expo.out` | `cubic-bezier(0.16, 1, 0.3, 1)` | Fast authoritative snap, silky prolonged settle |
| Optical Scanner Wipe | `power2.inOut` | `cubic-bezier(0.45, 0, 0.55, 1)` | Weighted mechanical glide across the frame |
| Camera Dolly / Scale Drift | `power3.out` | `cubic-bezier(0.22, 1, 0.36, 1)` | Smooth physical camera deceleration |
| Exit / Clear Before Hard Cut | `power2.in` | `cubic-bezier(0.55, 0, 1, 0.45)` | Crisp whip-out into the next beat |

---

## 3. Signature Motion Patterns (Zero Cheesy Presets)

### A. Apple Baseline-Masked Line Reveal (No Blurry Fades!)
Wrap each heading line inside an `overflow: hidden` container and animate `yPercent: 110 -> 0` with `expo.out`:
```html
<span class="mask-line"><span class="mask-inner">Pure <em>geometry.</em></span></span>
```
```js
tl.fromTo(".mask-inner", { yPercent: 110 }, { yPercent: 0, duration: 0.65, ease: "expo.out" }, t);
```

### B. RSVP (Rapid Serial Visual Presentation) Opener
Flash 2–4 punchy words sequentially in the **exact same screen coordinate** (`0.48s–0.72s` apart, locked to musical beats). Zero eye travel = instant cognitive impact.

### C. ManvsMachine Synchronized 2-Up Split-Screen
Place Beauty and Wireframe/UI-Dev videos side-by-side (`grid-template-columns: 1fr 1fr`) separated by a razor-thin `1px` architectural divider. Both `<video>` elements share the exact same `data-start` and `data-duration` for 100% frame-locked motion.

### D. Diagonal Laser Scanner Wipe (`Wireframe -> Beauty`)
Layer `beauty` (`z-index: 3`) directly over `wireframe` (`z-index: 2`) on the exact same camera track, animate a tilted `clipPath` polygon with a `4px` glowing accent beam riding the leading edge:
```js
tl.fromTo("#beauty",
  { clipPath: "polygon(0% 0%, 0% 0%, -18% 100%, 0% 100%)" },
  { clipPath: "polygon(0% 0%, 118% 0%, 100% 100%, 0% 100%)", duration: 0.90, ease: "power2.inOut" },
  wipeAt
);
tl.fromTo("#beam", { x: -160, opacity: 1 }, { x: 2120, opacity: 0.95, duration: 0.90, ease: "power2.inOut" }, wipeAt);
```

### E. 3D Perspective Studio Vault Mosaic Wall Pull-Back
Show scale at the end of a product or 3D reel: start zoomed tightly on the center hero card (`scale: 1.75, rotateX: 0, z: 240`) and pull back in `perspective: 1500px` to `scale: 0.84, rotateX: 9, rotateY: -6, z: -80` while 3 rows of cards counter-scroll horizontally (`-120 -> +90`, `+110 -> -110`, `-90 -> +120`).

### F. Intentional Use of High-Res Static Images
Never build an entire video out of slow-zooming PNGs. High-res stills ARE studio-grade when used deliberately for:
1. **3-Up Vertical Architectural Strips** (3 contrasting macro shots with opposing subtle parallax drift).
2. **Rapid-Fire 4-to-8-Beat Match-Cut Montages** (`0.24s–0.25s` per cut on rising percussion).
3. **3D Perspective Bento / Vault Mosaic Walls** (where 12–18 product cards move in 3D space).

---

## 4. Typography & Anti-Slop Checklist
- **Font Pairing:** Editorial high-contrast Serif (`Instrument Serif`, `Playfair Display`, `Cormorant Garamond`) + clean Neo-Grotesk (`Space Grotesk`, `Inter`) + disciplined Monospace (`JetBrains Mono`) for micro telemetry only.
- **No Noise:** Keep at most **2 text zones** visible at once (e.g., lower-left title + top-right 2-line spec). Never clutter corners with fake radar widgets, neon progress bars, or generic rounded SaaS badges.
- **Match Video Clip Durations:** Never set `<video data-duration>` to more than `1.25x` the clip's native duration (prevents frozen end-frames and slow-motion stutter).

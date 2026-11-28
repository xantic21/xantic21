# xantform design system (public summary)

**Edition 2.0 · 25 November 2026.** xantform is the name of this personal product family. This page is the public reference for names, colors and icon rules; the generator, verifier and release-specific notes are kept with the private source.

<img src="../../assets/profile-icon.svg" width="76" alt="xantform icon: geometric interlaced X" align="left">

**Direction:** light, matte and calm; inspired by Samsung One UI and OnePro You, not affiliated with or endorsed by Samsung. Squircle tiles, precise two-tone glyphs, generous spacing, no gradients, gloss, 3D effects or generic icon sets.

<br clear="left">

## Names and palettes

Palette order: light, medium, ink, dark. Repository names, package and app IDs and release tags keep their original technical names.

| Product | Formerly | Icon motif | Light | Medium | Ink | Dark |
| --- | --- | --- | --- | --- | --- | --- |
| **xantform** | xantic21 | geometric interlaced X | `#D9E1F0` | `#9AAEC9` | `#455C7D` | `#202D42` |
| **Cremaflux** | Coffee Lab | espresso cup with extraction flow | `#DCE7DF` | `#A0BBAA` | `#4B6F5C` | `#243D31` |
| **Yardphase** | NFL Pulse | American football with laces and end bands | `#E5DFF0` | `#B5A5CD` | `#6B5989` | `#382F4E` |
| **Orbit** | Henning Hub | central core with an orbit and two satellites | `#DCE6F1` | `#9CB5D1` | `#496D98` | `#283E5D` |
| **Gatevector** | HACC | layered gate with a verification check | `#E0E3E9` | `#A8B0BF` | `#566274` | `#2C3545` |
| **Stride** | — | letter S inside a segmented performance ring | `#D9E8EA` | `#92B9C0` | `#3F7480` | `#20434A` |
| **Endurhythm** | Training Lab | periodized performance curve over its training load | `#EFE2D9` | `#C9A68F` | `#94664D` | `#583D2E` |
| **hevy2garmin** | — | dumbbell with a synchronization arrow | `#E6F3EE` | `#A4C7B7` | `#1F5A4D` | `#253F38` |

## Icon variants

| Variant | Tile | Primary glyph | Secondary glyph |
| --- | --- | --- | --- |
| Tonal light (canonical, used on GitHub) | light | ink if it reaches 7 : 1 on the tile, otherwise dark | medium (Orbit: `#637F9D`) |
| Tonal dark | dark | light | medium |
| Adaptive You (themed-icon preview) | common system tile | common system primary | common system secondary |
| Monochrome layer (Android 13+) | transparent | white | white at 50 % alpha |

Every variant uses the same glyph geometry on a 108 × 108 grid with an organic superellipse squircle. Primary glyphs reach at least 7 : 1 contrast against their tile. Orbit's tonal-light orbit ring uses `#637F9D` instead of its medium tone so that it reaches at least 3 : 1 on its tile (3.29 : 1); its tonal-dark ring keeps the medium tone (5.13 : 1). Icons are checked at 16, 24, 48 and 108 px on light and dark backgrounds.

## README and documentation rules

- Professional US English, short sentences, no filler or emojis; only verified facts — no invented badges, test results, stars, user numbers or features.
- Approved product names in current-facing text; a former name appears only next to the new one ("Cremaflux (formerly Coffee Lab)"). Historical, versioned and evidence documents stay as recorded.
- Landing READMEs follow one order: hero, promise, release line, experience, design, current release, privacy, documentation, license, footer.
- Native app names and launcher icons change only with each product's next regular, separately gated release.

## Profile assets

[`assets/`](../../assets/) holds the profile header, the xantform icon, the seven product icons, `avatar-460.png` (profile picture) and `social-preview.png`, all generated from the same masters.

# Tech Style Bytes

Liza Tinker's blog: Sydney cafes, bars, art, streets, fashion and tech. Live at https://techstylebytes.com

## How a post gets published (for Claude)
1. Liza sends photos + a voice note or a few lines.
2. Resize photos to max 1600px with EXIF/GPS stripped (PIL `ImageOps.exif_transpose`, save without exif) into `images/`.
3. Write `posts/YYYY-MM-DD-slug.md` in Liza's voice using only what she said: front matter keys are listed at the top of `build.py`.
4. `python3 build.py` (needs `pip install markdown`), then commit and push to `main`. GitHub Pages serves `docs/`.
5. Preview drafts with `python3 build.py --drafts`; set `draft: true` to keep a post offline.

Brand: navy #0d1b3e, pink #ff0876, teal #0a8086, yellow #f0c808; DM Serif Display, Oswald, Poppins (self-hosted in `static/fonts`).

"""Tech Style Bytes reel: Khanom House. 1080x1920, 30fps, ~18s, no music (add a sound in-app).
Usage: python3 make_reel.py  -> frames piped to ffmpeg -> khanom-house-reel.mp4
Scenes are data below; reuse for future reviews by swapping SCENES and photos."""
import subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageOps

W, H, FPS = 1080, 1920, 30
NAVY, PINK, TEAL, YELLOW, WHITE = (13, 27, 62), (255, 8, 118), (10, 128, 134), (240, 200, 8), (255, 255, 255)
F = "fonts/"
OSW = lambda s: ImageFont.truetype(F + "oswald-latin-700-normal.ttf", s)
DMS = lambda s: ImageFont.truetype(F + "dm-serif-display-latin-400-normal.ttf", s)
DMI = lambda s: ImageFont.truetype(F + "dm-serif-display-latin-400-italic.ttf", s)
POP = lambda s: ImageFont.truetype(F + "poppins-latin-500-normal.ttf", s)

UP = "/mnt/user-data/uploads/"
FOOD, SIGN, STORE = UP + "72ecf714-image.jpg", UP + "71b5adfa-image.jpg", UP + "a66cb5b4-image.jpg"
_img = {}
def src(p):
    if p not in _img:
        _img[p] = ImageOps.exif_transpose(Image.open(p)).convert("RGB")
    return _img[p]

# Each scene: photo, duration, focus start/end (0-1), zoom start/end, text lines, text y
# A line: (kicker|big|body, text, highlight-word-or-None)
SCENES = [
    dict(photo=STORE, dur=3.2, f0=(.5, .55), f1=(.5, .5), z0=1.0, z1=1.12, y=330,
         lines=[("kicker", "CHIPPENDALE, SYDNEY", None), ("big", "The hidden teal", None), ("big", "bakehouse", "bakehouse")]),
    dict(photo=FOOD, dur=3.2, f0=(.6, .3), f1=(.58, .26), z0=1.25, z1=1.4, y=1040,
         lines=[("kicker", "THE COFFEE", None), ("big", "Absolutely", None), ("big", "perfect.", "perfect.")]),
    dict(photo=FOOD, dur=3.2, f0=(.2, .45), f1=(.24, .48), z0=1.3, z1=1.42, y=1040,
         lines=[("kicker", "CRAVING SAVOURY?", None), ("big", "Ham & cheese", None), ("body", "Slim savoury pickings, but it hit the spot", None)]),
    dict(photo=FOOD, dur=3.4, f0=(.78, .7), f1=(.72, .66), z0=1.3, z1=1.15, y=330,
         lines=[("kicker", "MY PLANNING HOUR", None), ("big", "Spiral diary +", None), ("big", "outside table", "outside table")]),
    dict(photo=SIGN, dur=2.8, f0=(.5, .66), f1=(.5, .64), z0=1.0, z1=1.06, y=1150,
         lines=[("kicker", "FIND IT", None), ("big", "Khanom House", None), ("body", "15 Meagher St, Chippendale", None)]),
    dict(photo=None, dur=3.0),  # end card
]
XF = 0.3  # crossfade seconds


def frame_photo(path, f, z):
    im = src(path); sw, sh = im.size
    s0 = max(W / sw, H / sh)
    vw, vh = W / (s0 * z), H / (s0 * z)
    cx = min(max(f[0] * sw, vw / 2), sw - vw / 2); cy = min(max(f[1] * sh, vh / 2), sh - vh / 2)
    box = (cx - vw / 2, cy - vh / 2, cx + vw / 2, cy + vh / 2)
    return im.resize((W, H), Image.BICUBIC, box=box)


def text_layer(lines, y):
    """Navy blocks, white text; highlight phrase gets a yellow marker block with navy text + pink underline."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    x0 = 80
    for kind, txt, hl in lines:
        if kind == "kicker":
            fnt = OSW(44); pad = (22, 12)
            tw = d.textlength(txt, font=fnt); asc, desc = fnt.getmetrics()
            d.rounded_rectangle((x0, y, x0 + tw + 2 * pad[0], y + asc + desc + 2 * pad[1]), 30, fill=PINK)
            d.text((x0 + pad[0], y + pad[1]), txt, font=fnt, fill=WHITE)
            y += asc + desc + 2 * pad[1] + 14
        elif kind == "big":
            fnt = DMS(104); pad = (26, 10)
            tw = d.textlength(txt, font=fnt); asc, desc = fnt.getmetrics(); h = asc + desc + 2 * pad[1]
            bg, fg = (YELLOW, NAVY) if hl else (NAVY, WHITE)
            d.rectangle((x0, y, x0 + tw + 2 * pad[0], y + h), fill=bg)
            d.text((x0 + pad[0], y + pad[1] - 4), txt, font=fnt, fill=fg)
            if hl:
                d.rectangle((x0 + pad[0], y + h - 16, x0 + pad[0] + tw, y + h - 8), fill=PINK)
            y += h
        else:
            fnt = POP(40); pad = (24, 14)
            tw = d.textlength(txt, font=fnt); asc, desc = fnt.getmetrics(); h = asc + desc + 2 * pad[1]
            d.rectangle((x0, y + 8, x0 + tw + 2 * pad[0], y + 8 + h), fill=WHITE)
            d.text((x0 + pad[0], y + 8 + pad[1]), txt, font=fnt, fill=NAVY)
            y += h + 8
    print("text bottom", y, file=sys.stderr)
    assert y < 1520, "text runs into the bottom safe zone"
    return lay


def end_card():
    im = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(im)
    def centred(txt, fnt, y, fill):
        tw = d.textlength(txt, font=fnt); d.text(((W - tw) / 2, y), txt, font=fnt, fill=fill); return tw
    f = OSW(120); parts = [("TECH ", WHITE), ("STYLE", PINK), (" BYTES", WHITE)]
    total = sum(d.textlength(t, font=f) for t, _ in parts); x = (W - total) / 2; y = 640
    for t, c in parts:
        d.text((x, y), t, font=f, fill=c)
        if t == "STYLE":
            d.rectangle((x, y + 170, x + d.textlength(t, font=f), y + 180), fill=PINK)
        x += d.textlength(t, font=f)
    centred("Full review", DMI(78), 930, YELLOW)
    centred("techstylebytes.com", POP(58), 1050, WHITE)
    centred("@tech.style.bytes", OSW(52), 1160, PINK)
    return im


def ease(t):
    return 1 - (1 - min(max(t, 0), 1)) ** 3


def render_scene(sc, i):
    n = int(round(sc["dur"] * FPS))
    if sc.get("photo") is None:
        card = end_card()
        return [card] * n
    lay = text_layer(sc["lines"], sc["y"])
    out = []
    for k in range(n):
        t = k / max(n - 1, 1)
        f = tuple(a + (b - a) * t for a, b in zip(sc["f0"], sc["f1"]))
        z = sc["z0"] + (sc["z1"] - sc["z0"]) * t
        fr = frame_photo(sc["photo"], f, z).convert("RGBA")
        a = ease((k / FPS - 0.15) / 0.35)  # text pops in after 0.15s
        if a > 0:
            L = lay.copy(); L.putalpha(L.getchannel("A").point(lambda v: int(v * a)))
            fr.alpha_composite(L, (0, int(40 * (1 - a))))
        out.append(fr.convert("RGB"))
    return out


def main(outfile="khanom-house-reel.mp4"):
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                           "-shortest", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", outfile], stdin=subprocess.PIPE)
    xf = int(XF * FPS); prev_tail = None
    for i, sc in enumerate(SCENES):
        frames = render_scene(sc, i)
        if prev_tail:
            for j in range(xf):
                frames[j] = Image.blend(prev_tail[j], frames[j], (j + 1) / (xf + 1))
        body = frames if i == len(SCENES) - 1 else frames[:-xf]
        prev_tail = frames[-xf:] if i < len(SCENES) - 1 else None
        for fr in body:
            ff.stdin.write(fr.tobytes())
        print("scene", i + 1, "done", file=sys.stderr)
    ff.stdin.close(); ff.wait()


if __name__ == "__main__":
    main()

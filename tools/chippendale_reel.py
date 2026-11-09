"""Streets of Chippendale reel: photo scenes on the Tech Style Bytes reel template.
Run from a folder containing fonts/*.ttf (converted from static/fonts)."""
import os, subprocess, sys
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_reel as R
from anita_reel import photo_scene

I = "/home/claude/techstylebytes/images/"
SIGN, LANE, GREEN, RABBIT, KST = (I + "spice-alley-chippendale-neon-sign.jpg", I + "spice-alley-lantern-laneway.jpg",
    I + "chippendale-green-towers-ring-sculpture.jpg", I + "white-rabbit-gallery-jacaranda-balfour-street.jpg",
    I + "kensington-street-chippendale-laneway.jpg")


def end_card():
    im = R.end_card(); d = ImageDraw.Draw(im)
    d.rectangle((0, 830, R.W, 930), fill=R.NAVY)
    f = R.OSW(64); txt = "Streets: Chippendale"; tw = d.textlength(txt, font=f)
    d.text(((R.W - tw) / 2, 840), txt, font=f, fill=R.WHITE)
    return im


def main(out="chippendale-streets-reel.mp4"):
    scenes = [
        photo_scene(dict(photo=SIGN, dur=3.2, f0=(.5, .6), f1=(.5, .62), z0=1.0, z1=1.1, y=330,
                         lines=[("kicker", "CHIPPENDALE, SYDNEY", None), ("big", "A local's", None), ("big", "weekend walk", "weekend walk")])),
        photo_scene(dict(photo=LANE, dur=3.0, f0=(.5, .35), f1=(.5, .45), z0=1.0, z1=1.12, y=1040,
                         lines=[("kicker", "SPICE ALLEY", None), ("big", "Singapore", None), ("big", "at night", "at night")])),
        photo_scene(dict(photo=GREEN, dur=3.0, f0=(.5, .55), f1=(.5, .5), z0=1.0, z1=1.1, y=330,
                         lines=[("kicker", "CHIPPENDALE GREEN", None), ("big", "The hidden park", None), ("big", "off Broadway", "off Broadway")])),
        photo_scene(dict(photo=RABBIT, dur=3.0, f0=(.45, .45), f1=(.55, .42), z0=1.05, z1=1.15, y=1040,
                         lines=[("kicker", "WHITE RABBIT GALLERY", None), ("big", "Art +", None), ("big", "jacarandas", "jacarandas")])),
        photo_scene(dict(photo=KST, dur=2.8, f0=(.5, .55), f1=(.5, .5), z0=1.0, z1=1.08, y=330,
                         lines=[("kicker", "CAFES, PUBS, HIDDEN BARS", None), ("big", "Explore it", None), ("big", "any weekend", "any weekend")])),
        [end_card()] * int(3.0 * R.FPS),
    ]
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{R.W}x{R.H}",
                           "-r", str(R.FPS), "-i", "-", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
                           "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    xf = int(R.XF * R.FPS); tail = None
    for i, frames in enumerate(scenes):
        if tail:
            for j in range(xf):
                frames[j] = Image.blend(tail[j], frames[j], (j + 1) / (xf + 1))
        last = i == len(scenes) - 1
        for fr in (frames if last else frames[:-xf]):
            ff.stdin.write(fr.tobytes())
        tail = None if last else frames[-xf:]
    ff.stdin.close(); ff.wait()


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "chippendale-streets-reel.mp4")

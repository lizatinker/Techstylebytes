"""Keydom reel: photo scenes on the Tech Style Bytes reel template."""
import subprocess, sys
from PIL import Image, ImageDraw
import make_reel as R
from anita_reel import photo_scene

U = "/mnt/user-data/uploads/"
WALL, LIT, PEG, MATS = U + "eae7b8a1-image.jpg", "/home/claude/techstylebytes/images/keydom-lit-keyboard-display.jpg", U + "0e6fd668-image.jpg", U + "201e8075-image.jpg"


def end_card():
    im = R.end_card(); d = ImageDraw.Draw(im)
    d.rectangle((0, 830, R.W, 930), fill=R.NAVY)
    f = R.OSW(64); txt = "Tech find: Keydom"; tw = d.textlength(txt, font=f)
    d.text(((R.W - tw) / 2, 840), txt, font=f, fill=R.WHITE)
    return im


def main(out="keydom-reel.mp4"):
    scenes = [
        photo_scene(dict(photo=WALL, dur=3.2, f0=(.5, .5), f1=(.5, .46), z0=1.0, z1=1.1, y=330,
                         lines=[("kicker", "CHIPPENDALE, SYDNEY", None), ("big", "Keyboard", None), ("big", "heaven", "heaven")])),
        photo_scene(dict(photo=LIT, dur=3.0, f0=(.5, .3), f1=(.5, .36), z0=1.1, z1=1.2, y=1080,
                         lines=[("kicker", "WALLS OF KEYBOARDS", None), ("big", "Try them all", "Try them all")])),
        photo_scene(dict(photo=PEG, dur=3.2, f0=(.55, .45), f1=(.5, .5), z0=1.05, z1=1.15, y=330,
                         lines=[("kicker", "MAKE IT YOURS", None), ("big", "Custom builds", None), ("big", "+ keycaps", "+ keycaps")])),
        photo_scene(dict(photo=MATS, dur=2.8, f0=(.5, .35), f1=(.5, .3), z0=1.0, z1=1.08, y=1040,
                         lines=[("kicker", "THE WHOLE DESK", None), ("big", "Mats, mice +", None), ("big", "headphones", "headphones")])),
        photo_scene(dict(photo=PEG, dur=3.0, f0=(.75, .55), f1=(.72, .5), z0=1.35, z1=1.5, y=330,
                         lines=[("kicker", "COMING SOON", None), ("big", "My first one:", None), ("big", "Black Friday", "Black Friday"), ("body", "Unboxing next week", None)])),
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
    main()

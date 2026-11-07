"""Frankie Cadillac reel (photos only). Reuses anita_reel helpers."""
import subprocess, sys
from PIL import Image
import make_reel as R, anita_reel as A

UP = "/mnt/user-data/uploads/"
OLIVES, MENU, NEG = UP + "05048605-image.jpg", UP + "f935fc1c-image.jpg", UP + "c061977d-image.jpg"


def encode(scenes, out):
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


scenes = [
    A.photo_scene(dict(photo=MENU, dur=3.2, f0=(.4, .55), f1=(.42, .5), z0=1.0, z1=1.12, y=300,
                       lines=[("kicker", "SURRY HILLS", None), ("big", "The Home of", None), ("big", "the Negroni", "the Negroni")])),
    A.photo_scene(dict(photo=OLIVES, dur=3.2, f0=(.35, .7), f1=(.32, .74), z0=1.15, z1=1.3, y=300,
                       lines=[("kicker", "PRE-DINNER SNACK", None), ("big", "Fried olives", None), ("big", "to die for", "to die for")])),
    A.photo_scene(dict(photo=NEG, dur=3.2, f0=(.6, .62), f1=(.58, .6), z0=1.05, z1=1.18, y=300,
                       lines=[("kicker", "THE NEGRONI", None), ("big", "Absolutely", None), ("big", "perfect.", "perfect.")])),
    A.photo_scene(dict(photo=NEG, dur=3.4, f0=(.3, .45), f1=(.27, .42), z0=1.3, z1=1.45, y=1080,
                       lines=[("kicker", "THE CATCH", None), ("big", "A frosty welcome", None), ("body", "They warmed up. First impressions stick.", None)])),
    [A.end_card("8/10")] * int(3.0 * R.FPS),
]
encode(scenes, "frankie-cadillac-reel.mp4")

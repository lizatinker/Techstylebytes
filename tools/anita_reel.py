"""Anita Gelato reel: video + photo scenes, reusing the Tech Style Bytes reel template (make_reel.py)."""
import subprocess, sys
import numpy as np
from PIL import Image, ImageDraw
import make_reel as R

MOV = "/mnt/user-data/uploads/IMG_8911.mov"
CUP = "/mnt/user-data/uploads/ada8e621-image.jpg"


def video_frames(start, dur):
    cmd = ["ffmpeg", "-loglevel", "error", "-ss", str(start), "-t", str(dur), "-i", MOV,
           "-vf", f"scale={R.W}:{R.H}:force_original_aspect_ratio=increase,crop={R.W}:{R.H},fps={R.FPS}",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    n = len(raw) // (R.W * R.H * 3)
    return [Image.frombuffer("RGB", (R.W, R.H), raw[i * R.W * R.H * 3:(i + 1) * R.W * R.H * 3]) for i in range(n)]


def overlay(frames, lines, y):
    lay = R.text_layer(lines, y); out = []
    for k, fr in enumerate(frames):
        fr = fr.convert("RGBA"); a = R.ease((k / R.FPS - 0.15) / 0.35)
        if a > 0:
            L = lay.copy(); L.putalpha(L.getchannel("A").point(lambda v: int(v * a)))
            fr.alpha_composite(L, (0, int(40 * (1 - a))))
        out.append(fr.convert("RGB"))
    return out


def photo_scene(sc):
    n = int(round(sc["dur"] * R.FPS)); frs = []
    for k in range(n):
        t = k / max(n - 1, 1)
        f = tuple(a + (b - a) * t for a, b in zip(sc["f0"], sc["f1"]))
        frs.append(R.frame_photo(sc["photo"], f, sc["z0"] + (sc["z1"] - sc["z0"]) * t))
    return overlay(frs, sc["lines"], sc["y"])


def end_card(score="9/10"):
    im = R.end_card(); d = ImageDraw.Draw(im)
    # the template end card says 7/10 for Khanom House; repaint that line
    d.rectangle((0, 830, R.W, 930), fill=R.NAVY)
    f = R.OSW(64); txt = f"My score: {score}"; tw = d.textlength(txt, font=f)
    d.text(((R.W - tw) / 2, 840), txt, font=f, fill=R.WHITE)
    return im


def main(out="anita-gelato-reel.mp4"):
    scenes = [
        overlay(video_frames(0.0, 3.6), [("kicker", "CENTRAL PARK, CHIPPENDALE", None), ("big", "Dangerously close", None), ("big", "to my house", "to my house")], 330),
        overlay(video_frames(4.2, 3.0), [("kicker", "ANITA GELATO", None), ("big", "The best gelato", None), ("big", "in Sydney", "in Sydney")], 330),
        overlay(video_frames(8.8, 3.4), [("kicker", "MY ORDER", None), ("big", "Cookieman +", None), ("big", "Pavlova", "Pavlova")], 330),
        photo_scene(dict(photo=CUP, dur=3.0, f0=(.5, .5), f1=(.5, .46), z0=1.0, z1=1.1, y=1080,
                         lines=[("kicker", "$8.40 SMALL CUP", None), ("big", "Two flavours", None), ("body", "Take-home tub about $28. Christmas: sorted", None)])),
        photo_scene(dict(photo=CUP, dur=2.8, f0=(.45, .55), f1=(.48, .58), z0=1.35, z1=1.5, y=330,
                         lines=[("kicker", "THE ONE CATCH", None), ("big", "The sampling", None), ("big", "queue", "queue")])),
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
        print("scene", i + 1, len(frames), file=sys.stderr)
    ff.stdin.close(); ff.wait()


if __name__ == "__main__":
    main()

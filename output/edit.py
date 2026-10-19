#!/usr/bin/env python3
"""Xiaohongshu vertical edit: reproducible build script.

Usage: python3 edit.py <source_dir> [build_dir]
Renders (into the folder this script lives in):
  final_zh_subtitled.mp4, final_no_subtitles.mp4
from the original .mov files in <source_dir> (read only) plus subtitles_zh.ass.
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else "."
BUILD = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "_build")
FPS = 30

# (cut id, source file, start s, end s, framing, loudness target LUFS[, tail fade s])
CUTS = [
    ("01_hook_yoga",   "ac5c92ef-7d1d9b79d3f64dfb985c35c09797e6ca.mov", 5.60, 8.00, "lowres", -19),
    ("02_headphones",  "00c872dc-IMG_7904.mov",                         0.00, 2.9333, "fill",   -26),
    ("03_gym",         "391b8b73-5A1C6A72-EB66-4E0B-9328-922D1974543D.mov", 0.60, 2.4667, "fill", -26),
    ("04_pool",        "1e62a816-IMG_7392.mov",                         1.30, 3.9333, "fill",   -26),
    ("05_rose",        "77d5eb17-IMG_7108.mov",                         0.00, 4.3333, "fill",   -24),
    ("06_sunset",      "183110ce-IMG_7319.mov",                         0.00, 1.80, "fill",   -26, 0.35),
    ("07_night_selfie1", "606c6c26-98795DE9-E4A8-4123-9387-C9D84E895067.mov", 0.00, 3.5333, "fill", -25),
    ("08_night_selfie2", "6f7d1327-A65CE1D7-6EC3-4141-A869-26D8CBF5BA44.mov", 0.00, 1.60, "sideways", -25),
    ("09_night_selfie3", "79936ef1-8C7C835F-D8D7-4838-80A6-9780F872D27B.mov", 0.00, 1.9333, "fill", -25),
    ("10_yoga_full",   "ac5c92ef-7d1d9b79d3f64dfb985c35c09797e6ca.mov", 0.00, 10.20, "lowres", -19),
]
MAX_GAIN_DB = 10.0  # don't pump wind/room noise of very quiet clips

FILL = ("scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,"
        "crop=1080:1920,setsar=1")
VIDEO = {
    "fill": FILL,
    # 360x640 source: upscale + very light sharpening only
    "lowres": FILL + ",unsharp=5:5:0.5:5:5:0.0",
    # clip was recorded with the phone on its side and has no rotation flag:
    # rotate upright, keep a 1200x1080 window around the face and fill the
    # rest of the 9:16 frame with a blurred copy instead of cropping the face
    "sideways": ("transpose=2,crop=1200:1080:250:0,split[a][b];"
                 "[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
                 "boxblur=40:2,eq=brightness=-0.06[bg];"
                 "[b]scale=1080:-2:flags=lanczos[fg];[bg][fg]overlay=0:(H-h)/2,setsar=1"),
}


def run(cmd, **kw):
    print("+", " ".join(cmd), flush=True)
    return subprocess.run(cmd, check=True, **kw)


def loudness(path, ss, dur):
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-ss", str(ss), "-t", str(dur),
                        "-i", path, "-map", "0:a:0", "-af", "ebur128", "-f", "null", "-"],
                       capture_output=True, text=True)
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", p.stderr)
    return float(m[-1])


def main():
    os.makedirs(BUILD, exist_ok=True)
    segs, log = [], []
    for cid, name, a, b, mode, target, *rest in CUTS:
        fade = rest[0] if rest else 0.05
        src = os.path.join(SRC, name)
        dur = round(b - a, 3)
        lufs = loudness(src, a, dur)
        gain = max(-20.0, min(MAX_GAIN_DB, target - lufs))
        log.append(dict(cut=cid, source=name, start=a, end=b, dur=dur, lufs=lufs, gain_db=round(gain, 1)))
        out = os.path.join(BUILD, cid + ".mov")
        # tpad: some sources end a frame early; hold the last frame so A/V stay equal
        vf = VIDEO[mode] + f",fps={FPS},tpad=stop_mode=clone:stop_duration=0.2,format=yuv420p"
        af = (f"aresample=48000,aformat=channel_layouts=stereo,volume={gain:.2f}dB,"
              f"apad,atrim=0:{dur},afade=t=in:d=0.03,afade=t=out:st={dur-fade:.3f}:d={fade}")
        run(["ffmpeg", "-v", "error", "-y", "-ss", str(a), "-t", str(dur), "-i", src,
             "-filter_complex", f"[0:v:0]{vf}[v];[0:a:0]{af}[a]", "-map", "[v]", "-map", "[a]",
             "-t", str(dur), "-c:v", "libx264", "-crf", "12", "-preset", "fast",
             "-c:a", "pcm_s16le", out])
        segs.append(out)
    with open(os.path.join(BUILD, "cuts_log.json"), "w") as f:
        json.dump(log, f, indent=1)

    n = len(segs)
    inputs = sum((["-i", s] for s in segs), [])
    ass = os.path.join(HERE, "subtitles_zh.ass").replace("\\", "/").replace(":", r"\:")
    graph = "".join(f"[{i}:v][{i}:a]" for i in range(n)) + f"concat=n={n}:v=1:a=1[v][a0];"
    graph += "[v]split[vn][vs0];"
    graph += f"[vs0]ass='{ass}':fontsdir=/usr/share/fonts/truetype/wqy[vs];"
    # lift to phone-friendly loudness (~-17 LUFS), limiter keeps peaks under -1.5 dBFS
    graph += "[a0]volume=5dB,alimiter=limit=0.84:attack=5:release=80:level=false,asplit[an][as]"
    enc = ["-c:v", "libx264", "-preset", "slow", "-crf", "20", "-profile:v", "high",
           "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
           "-movflags", "+faststart"]
    run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", graph,
         "-map", "[vn]", "-map", "[an]", *enc, os.path.join(HERE, "final_no_subtitles.mp4"),
         "-map", "[vs]", "-map", "[as]", *enc, os.path.join(HERE, "final_zh_subtitled.mp4")])


if __name__ == "__main__":
    main()

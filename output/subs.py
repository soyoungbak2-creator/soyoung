#!/usr/bin/env python3
"""Writes subtitles_zh.ass (burned in) and subtitles_zh.srt from one list.
All lines are editor captions describing what is visible on screen;
no dialogue was transcribed (speech recognition was not available)."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
# start, end, position (top/bottom), text ("\n" = line break)
SUBS = [
    (0.10, 2.35, "top", "做个瑜伽\n背上怎么多了只小狗？"),
    (2.45, 5.28, "bot", "这几天的日常\n戴上耳机，出发！"),
    (5.38, 7.15, "top", "半露天健身房\n吊环、杠铃都有"),
    (7.25, 9.78, "top", "泳池边走一走\n池水是淡淡的绿色"),
    (9.88, 11.90, "top", "刚走出门……"),
    (11.95, 14.12, "top", "突然收到一朵玫瑰！"),
    (14.22, 15.92, "top", "傍晚的海边"),
    (16.02, 19.45, "bot", "晚上在露台餐厅\n自拍停不下来"),
    (19.55, 22.98, "bot", "换个角度\n再拍一段"),
    (23.10, 26.60, "top", "说回那节瑜伽课\n趴下拉伸，小狗直接站上来"),
    (26.68, 30.00, "top", "抬头看镜头\n笑了出来"),
    (30.05, 31.20, "top", "笑到捂脸"),
    (31.25, 33.20, "top", "你会想试试小狗瑜伽吗？"),
]

def ts(t, sep):
    h, r = divmod(t, 3600); m, s = divmod(r, 60)
    if sep == ",":
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{round((s % 1) * 1000):03d}"
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"

HEAD = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: top,WenQuanYi Zen Hei,70,&H00FFFFFF,&H00FFFFFF,&H00202020,&H80000000,-1,0,0,0,100,100,2,0,1,5,2,8,90,90,330,1
Style: bot,WenQuanYi Zen Hei,70,&H00FFFFFF,&H00FFFFFF,&H00202020,&H80000000,-1,0,0,0,100,100,2,0,1,5,2,2,90,90,470,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
with open(os.path.join(HERE, "subtitles_zh.ass"), "w", encoding="utf-8") as f:
    f.write(HEAD)
    for a, b, pos, txt in SUBS:
        f.write(f"Dialogue: 0,{ts(a,'.')},{ts(b,'.')},{pos},,0,0,0,,{{\\fad(80,80)}}{txt.replace(chr(10), r'\N')}\n")
with open(os.path.join(HERE, "subtitles_zh.srt"), "w", encoding="utf-8") as f:
    for i, (a, b, pos, txt) in enumerate(SUBS, 1):
        f.write(f"{i}\n{ts(a, ',')} --> {ts(b, ',')}\n{txt}\n\n")

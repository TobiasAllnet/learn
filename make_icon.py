"""App icon: one smooth white light bulb with grey detail lines and a small name watermark.
Needs Pillow (pip install pillow). Usage: python make_icon.py [output_folder] [watermark_text]
"""
import sys, os, math
from PIL import Image, ImageDraw, ImageFont

FONT = r'C:\Windows\Fonts\segoeuib.ttf'
SS = 4  # draw 4x bigger then shrink, for smooth edges

def bezier(p0, p1, p2, p3, n=24):
    pts = []
    for i in range(n + 1):
        t = i / n; u = 1 - t
        pts.append((u**3*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t**3*p3[0],
                    u**3*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t**3*p3[1]))
    return pts

def bulb_outline():
    cx, cy, r = .5, .385, .215
    a0 = math.radians(48)                       # where the globe starts to taper
    p0 = (cx + r*math.cos(a0), cy + r*math.sin(a0))
    d = (-math.sin(a0), math.cos(a0))           # direction of the circle there
    p3 = (.575, .685)                           # bottom of the neck
    right = bezier(p0, (p0[0] + .09*d[0], p0[1] + .09*d[1]), (.575, .625), p3)
    # globe arc from the left tangent point over the top to the right tangent point
    arc = []
    start, end = math.pi - a0, 2*math.pi + a0   # left side, over the top, right side
    for i in range(61):
        a = start + (end - start) * i / 60
        arc.append((cx + r*math.cos(a), cy + r*math.sin(a)))
    left = [(1 - x, y) for x, y in reversed(right)]
    return left + arc + right

ORANGE = (255, 112, 50); TEAL = (0, 190, 185); PEACH = (255, 190, 130)
def mix(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
def smooth(t, a, b):
    t = max(0, min(1, (t - a) / (b - a))); return t * t * (3 - 2 * t)
def field(u, v):
    t = (u + v) / 2 + .07 * math.sin(v * 9 + 1) + .05 * math.sin(u * 7)   # wavy diagonal
    k = smooth(t, .30, .80)                                                # wide soft fade, centre at 0.55 = 60/40
    return mix(mix(ORANGE, TEAL, k), PEACH, .22 * math.sin(math.pi * k))   # light touch keeps the fade clean

def make(size, text):
    s = size * SS
    g = Image.new('RGB', (size, size)); gp = g.load()   # orange and teal, wavy fade, about 60% orange
    for y in range(size):
        for x in range(size):
            gp[x, y] = field((x + .5) / size, (y + .5) / size)
    img = g.resize((s, s), Image.BICUBIC)
    d = ImageDraw.Draw(img, 'RGBA')
    P = lambda pts: [(x*s, y*s) for x, y in pts]
    white = (255, 255, 255, 255)
    d.polygon(P(bulb_outline()), fill=white)
    d.rounded_rectangle(P([(.405, .66), (.595, .83)]), radius=.05*s, fill=white)   # base, one piece
    # small round tip at the bottom of the base
    grey = (70, 72, 82, 255)
    lw = max(2, int(.011*s))
    for yy in (.715, .755):                     # thread lines on the base
        d.line(P([(.415, yy), (.585, yy)]), fill=grey, width=lw)
    # curved glass highlight inside the globe (upper left)
    box = [(.5 - .155)*s, (.385 - .155)*s, (.5 + .155)*s, (.385 + .155)*s]
    d.arc(box, start=195, end=255, fill=(150, 152, 165, 255), width=int(.014*s))
    # watermark, bottom right
    if text:
        font = ImageFont.truetype(FONT, int(.085*s))
        layer = Image.new('RGBA', (s, s), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        tw = ld.textlength(text, font=font)
        ld.text((.93*s - tw, .965*s), text, font=font, fill=(255, 255, 255, 170), anchor='ls')
        img = Image.alpha_composite(img.convert('RGBA'), layer).convert('RGB')
    return img.resize((size, size), Image.LANCZOS)

out = sys.argv[1] if len(sys.argv) > 1 else '.'
text = sys.argv[2] if len(sys.argv) > 2 else ''  # optional watermark, none by default
os.makedirs(out, exist_ok=True)
for n in (180, 192, 512):
    make(n, text).save(os.path.join(out, 'icon-%d.png' % n))

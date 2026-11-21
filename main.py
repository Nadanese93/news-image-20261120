#!/usr/bin/env python3
"""Sum up 20 November's world news in one image.

Draws a newspaper front page for Friday 20 November 2026: a masthead,
a hero story (Russia's barrage on Kyiv, missiles landing in Poland) and
four panels (ICJ genocide verdict on Myanmar, Hormuz tanker fires,
AI stock rout, Trump-Xi-Putin summit in Shenzhen), plus a footer ticker
(Peru quake, COP31).

Python 3.13 standard library only, no network, fully deterministic:
the same bytes on every run. Writes entry.png to $MAKEFUN_OUTPUT_DIR
(default '/output').
"""

import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- font: 5x7
# Each glyph is 7 rows of 5 bits, top to bottom, '1' = ink.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
}


def text_width(text, scale):
    """Width in pixels of text at the given scale (6 units per char)."""
    return len(text) * 6 * scale


def wrap_text(text, max_width, scale):
    """Greedy word wrap; returns a list of lines fitting max_width."""
    words = text.split(' ')
    lines = []
    cur = ''
    for word in words:
        trial = word if not cur else cur + ' ' + word
        if text_width(trial, scale) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(bg * (w * h))

    def put(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i:i + 3] = color

    def rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.buf[i:(yy * self.w + x1) * 3] = color * (x1 - x0)

    def vgrad(self, x, y, w, h, top, bottom):
        for yy in range(h):
            t = yy / max(1, h - 1)
            c = bytes(
                round(top[k] + (bottom[k] - top[k]) * t) for k in range(3)
            )
            self.rect(x, y + yy, w, 1, c)

    def hline(self, x, y, w, color, thick=1):
        self.rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.rect(x, y, thick, h, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        r = thick // 2
        while True:
            self.rect(x - r, y - r, thick, thick, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) ** 2) ** 0.5) if abs(yy - cy) <= r else 0
            self.rect(cx - dx, yy, dx * 2 + 1, 1, color)

    def poly(self, pts, color):
        """Scanline fill of a simple polygon given as [(x, y), ...]."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for yy in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= yy < y1) or (y1 <= yy < y0):
                    t = (yy - y0) / (y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.rect(int(xs[i]), yy, int(xs[i + 1]) - int(xs[i]) + 1, 1, color)

    def burst(self, cx, cy, r, color, spikes=12):
        """Starburst: alternating outer/inner radius polygon."""
        import math
        pts = []
        for i in range(spikes * 2):
            ang = math.pi * i / spikes - math.pi / 2
            rr = r if i % 2 == 0 else int(r * 0.45)
            pts.append((cx + int(rr * math.cos(ang)),
                        cy + int(rr * math.sin(ang))))
        self.poly(pts, color)

    def glyph(self, x, y, ch, scale, color):
        g = FONT.get(ch)
        if g is None:
            return
        for row in range(7):
            bits = g[row]
            for col in range(5):
                if bits[col] == '1':
                    self.rect(x + col * scale, y + row * scale,
                              scale, scale, color)

    def text(self, x, y, s, scale, color, align='left'):
        # The bitmap font holds capitals only: normalise every string
        # so mixed-case copy (panel subheads) renders instead of
        # dropping its lowercase letters.
        s = s.upper()
        w = text_width(s, scale)
        if align == 'center':
            x -= w // 2
        elif align == 'right':
            x -= w
        cx = x
        for ch in s:
            self.glyph(cx, y, ch, scale, color)
            cx += 6 * scale

    def text_lines(self, x, y, lines, scale, color, leading=None,
                   align='left'):
        if leading is None:
            leading = 9 * scale
        for ln in lines:
            self.text(x, y, ln, scale, color, align=align)
            y += leading
        return y


def write_png(path, canvas):
    """Deterministic PNG: filter 0, zlib level 9, no ancillary chunks."""
    raw = bytearray()
    stride = canvas.w * 3
    for yy in range(canvas.h):
        raw.append(0)
        raw += canvas.buf[yy * stride:(yy + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(typ, data):
        c = struct.pack('>I', len(data)) + typ + data
        c += struct.pack('>I', zlib.crc32(typ + data) & 0xFFFFFFFF)
        return c

    ihdr = struct.pack('>IIBBBBB', canvas.w, canvas.h, 8, 2, 0, 0, 0)
    png = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr)
           + chunk(b'IDAT', comp) + chunk(b'IEND', b''))
    with open(path, 'wb') as f:
        f.write(png)
    return len(png)

# ---------------------------------------------------------------- palette
PAPER = bytes((246, 239, 224))
NAVY = bytes((22, 35, 63))
NAVY2 = bytes((30, 48, 84))
GOLD = bytes((212, 175, 55))
CREAM = bytes((247, 241, 227))
WHITE = bytes((255, 255, 255))
INK = bytes((24, 24, 24))
RED = bytes((185, 28, 28))
TEAL = bytes((15, 118, 110))
DARKTEAL = bytes((19, 78, 74))
DUSK_TOP = bytes((38, 32, 86))
DUSK_MID = bytes((124, 45, 18))
DUSK_LOW = bytes((234, 130, 48))
RIVER = bytes((29, 53, 87))
SKYLINE = bytes((30, 27, 38))
FLAME = bytes((249, 115, 22))
EMBER = bytes((251, 191, 36))
SMOKE = bytes((87, 83, 78))


def draw_masthead(cv):
    cv.rect(0, 0, W, 124, NAVY)
    cv.text(24, 34, "THE WORLD", 8, CREAM)
    cv.text(W - 24, 52, "FRIDAY, 20 NOVEMBER 2026", 3, GOLD, align='right')
    cv.hline(0, 124, W, GOLD, 4)


def draw_hero(cv):
    x0, y0, w, h = 8, 132, W - 16, 380
    # Dusk sky: indigo -> burnt orange, horizon low.
    cv.vgrad(x0, y0, w, h, DUSK_TOP, DUSK_LOW)
    # (No sun: an earlier sun sat half-hidden behind the headline
    # band and read as a stray gold blob at the hero's bottom edge.)
    # Missile trails: bright diagonal streaks with glowing heads.
    for (tx, ty, lx, ly) in ((180, 180, 260, 300), (420, 150, 470, 290),
                             (820, 170, 760, 300), (940, 210, 900, 320)):
        cv.line(tx, ty, lx, ly, bytes((254, 249, 195)), 3)
        cv.circle(lx, ly, 7, bytes((254, 249, 195)))
    # Explosion bursts in the sky.
    cv.burst(300, 330, 34, FLAME)
    cv.burst(300, 330, 20, EMBER)
    cv.burst(880, 350, 26, FLAME)
    cv.burst(880, 350, 15, EMBER)
    # Kyiv skyline silhouette with domes.
    base = y0 + h - 64
    for (bx, bw, bh) in ((0, 130, 90), (120, 90, 130), (205, 150, 70),
                         (350, 80, 150), (425, 170, 95), (590, 110, 140),
                         (695, 150, 80), (840, 90, 120), (925, 100, 85)):
        cv.rect(x0 + bx, base - bh, bw, bh + 64, SKYLINE)
    # Domes: St Sophia / Lavra silhouettes.
    for (dx, dy, dr) in ((165, base - 130, 26), (390, base - 150, 22),
                         (645, base - 140, 24)):
        cv.circle(x0 + dx, dy, dr, SKYLINE)
        cv.rect(x0 + dx - 2, dy - dr - 22, 4, 22, SKYLINE)
    # Lit windows.
    for wy in range(base - 120, base + 50, 22):
        for wx in range(x0 + 14, x0 + w - 14, 34):
            if (wx * 7 + wy * 13) % 5 == 0:
                cv.rect(wx, wy, 5, 7, EMBER)
    # Dnipro river strip with a reflection column under the sun.
    cv.rect(x0, base, w, 64, RIVER)
    cv.rect(688, base, 24, 64, bytes((96, 130, 180)))
    cv.rect(676, base + 8, 48, 6, bytes((147, 178, 222)))
    cv.rect(684, base + 30, 32, 6, bytes((147, 178, 222)))
    # Kicker chip.
    cv.rect(x0 + 16, y0 + 16, 208, 34, RED)
    cv.text(x0 + 28, y0 + 25, "WAR - UKRAINE", 2, WHITE)
    # Headline band.
    cv.rect(x0, y0 + h - 108, w, 108, bytes((16, 20, 36)))
    cv.text(x0 + 20, y0 + h - 96, "KYIV UNDER FIRE", 6, WHITE)
    cv.text(x0 + 20, y0 + h - 44,
            "400 DRONES, 110 MISSILES - TWO LAND IN POLAND", 2, CREAM)


def panel_frame(cv, x, y, w, h):
    cv.rect(x, y, w, h, WHITE)
    cv.rect(x, y, w, 3, NAVY)
    cv.rect(x, y, 3, h, NAVY)
    cv.rect(x + w - 3, y, 3, h, NAVY)
    cv.rect(x, y + h - 3, w, 3, NAVY)


def panel_text(cv, x, y, w, kicker, kcolor, headline, sub):
    cv.text(x + 14, y + 108, kicker, 2, kcolor)
    yy = y + 132
    for ln in wrap_text(headline, w - 28, 3):
        cv.text(x + 14, yy, ln, 3, INK)
        yy += 27
    yy += 2
    for ln in wrap_text(sub, w - 28, 2):
        cv.text(x + 14, yy, ln, 2, bytes((64, 64, 64)))
        yy += 18


def draw_panel_icj(cv, x, y, w, h):
    panel_frame(cv, x, y, w, h)
    # Teal sky, courthouse pediment + columns.
    cv.rect(x + 3, y + 3, w - 6, 96, TEAL)
    cv.poly([(x + 90, y + 14), (x + w - 90, y + 14), (x + w // 2, y + 44)],
            CREAM)
    for cx in (x + 130, x + 205, x + 280, x + 355):
        cv.rect(cx, y + 48, 18, 48, CREAM)
    cv.rect(x + 100, y + 92, w - 200, 7, CREAM)
    panel_text(cv, x, y, w, "JUSTICE - THE HAGUE", TEAL,
               "GENOCIDE VERDICT",
               "UN court: Myanmar guilty over the Rohingya - a first.")


def draw_panel_hormuz(cv, x, y, w, h):
    panel_frame(cv, x, y, w, h)
    # Dusk sky over a dark sea; tanker hull, flames, smoke.
    cv.vgrad(x + 3, y + 3, w - 6, 96, bytes((124, 45, 18)), DARKTEAL)
    cv.rect(x + 3, y + 62, w - 6, 37, bytes((13, 60, 58)))
    cv.rect(x + 90, y + 66, 300, 20, bytes((12, 12, 12)))
    cv.rect(x + 330, y + 48, 60, 18, bytes((12, 12, 12)))
    cv.burst(x + 150, y + 52, 22, FLAME)
    cv.burst(x + 150, y + 52, 12, EMBER)
    cv.burst(x + 340, y + 46, 16, FLAME)
    for (sx, sy, sr) in ((x + 120, y + 22, 12), (x + 135, y + 12, 9),
                         (x + 310, y + 20, 11)):
        cv.circle(sx, sy, sr, SMOKE)
    panel_text(cv, x, y, w, "ENERGY - HORMUZ", RED,
               "HORMUZ BURNS",
               "US blockade, tanker fires - biggest oil shock on record.")


def draw_panel_markets(cv, x, y, w, h):
    panel_frame(cv, x, y, w, h)
    # White chart field, grey grid, red line falling steeply.
    cv.rect(x + 3, y + 3, w - 6, 96, bytes((250, 250, 249)))
    for gy in (y + 24, y + 48, y + 72):
        cv.hline(x + 3, gy, w - 6, bytes((220, 220, 220)), 1)
    pts = [(x + 20, y + 18), (x + 90, y + 26), (x + 150, y + 22),
           (x + 210, y + 44), (x + 270, y + 40), (x + 330, y + 66),
           (x + 390, y + 62), (x + 450, y + 88)]
    for i in range(len(pts) - 1):
        cv.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], RED, 4)
    cv.poly([(x + 450, y + 88), (x + 428, y + 76), (x + 440, y + 92)],
            RED)
    # Label in the clear top-right corner, away from the falling line.
    cv.text(x + w - 130, y + 10, "-3.7%", 3, RED)
    panel_text(cv, x, y, w, "MARKETS - NEW YORK", RED,
               "AI ROUT",
               "S&P 500 slides into correction on chip sell-off.")


def draw_panel_summit(cv, x, y, w, h):
    panel_frame(cv, x, y, w, h)
    # Deep red hall, gold trim, three flags over a table.
    cv.rect(x + 3, y + 3, w - 6, 96, bytes((127, 29, 29)))
    cv.rect(x + 3, y + 88, w - 6, 11, GOLD)
    for (fx, cols) in ((x + 110, None), (x + 240, None), (x + 370, None)):
        cv.vline(fx, y + 18, 70, GOLD, 3)
    # US flag: stripes + blue canton.
    for i in range(5):
        cv.rect(x + 113, y + 18 + i * 9, 62, 5,
                WHITE if i % 2 == 0 else RED)
    cv.rect(x + 113, y + 18, 26, 22, bytes((30, 58, 138)))
    # China flag: red field, gold stars.
    cv.rect(x + 243, y + 18, 62, 45, bytes((220, 38, 38)))
    cv.burst(x + 258, y + 30, 8, GOLD, spikes=5)
    # Russia flag: white / blue / red bands.
    cv.rect(x + 373, y + 18, 62, 15, WHITE)
    cv.rect(x + 373, y + 33, 62, 15, bytes((0, 57, 166)))
    cv.rect(x + 373, y + 48, 62, 15, bytes((213, 0, 50)))
    panel_text(cv, x, y, w, "DIPLOMACY - SHENZHEN", bytes((146, 64, 14)),
               "THREE LEADERS, ONE TABLE",
               "Trump, Xi and Putin meet - first trilateral summit.")


def draw_footer(cv):
    cv.rect(0, 964, W, 52, NAVY)
    cv.text(24, 982, "ALSO: 6.7 QUAKE SHAKES PERU - COP31 TALKS RUN PAST DEADLINE",
            2, CREAM)
    cv.text(W - 24, 982, "20 NOV 2026", 2, GOLD, align='right')


def build():
    cv = Canvas(W, H, PAPER)
    cv.rect(0, 0, W, 8, NAVY)
    cv.rect(0, 0, 8, H, NAVY)
    cv.rect(W - 8, 0, 8, H, NAVY)
    cv.rect(0, H - 8, W, 8, NAVY)
    draw_masthead(cv)
    draw_hero(cv)
    gx, gy = 8, 528
    pw, ph, gut = 496, 204, 16
    draw_panel_icj(cv, gx, gy, pw, ph)
    draw_panel_hormuz(cv, gx + pw + gut, gy, pw, ph)
    draw_panel_markets(cv, gx, gy + ph + gut, pw, ph)
    draw_panel_summit(cv, gx + pw + gut, gy + ph + gut, pw, ph)
    draw_footer(cv)
    return cv


def main():
    out_dir = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
    os.makedirs(out_dir, exist_ok=True)
    cv = build()
    path = os.path.join(out_dir, 'entry.png')
    size = write_png(path, cv)
    print(f"wrote {path} ({size} bytes, {W}x{H})")


if __name__ == '__main__':
    main()

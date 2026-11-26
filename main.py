#!/usr/bin/env python3
"""The World in One Day -- 26 November 2026.

Draws a one-page newspaper front page (1024x1024 PNG) summing up the
world news of Thursday 26 November 2026, from real stories reported
that day (Reuters, Observer Voice, SimpleLife.news, OilPrice).

Pure Python 3 standard library only: no third-party packages, no
network, no clock, no randomness. Two runs write byte-identical PNGs.

Output: $MAKEFUN_OUTPUT_DIR/entry.png (default: ./out/entry.png).
"""

import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (253, 248, 238)   # warm newsprint
INK = (20, 20, 20)        # near-black
RED = (178, 24, 24)       # headline red
BLUE = (31, 58, 95)       # dark blue accent
ORANGE = (214, 96, 0)     # flame orange
GREY = (120, 116, 108)    # muted grey

# ---------------------------------------------------------------- font ----
# 5x7 bitmap font, uppercase + digits + punctuation. "1" = ink pixel.
FONT = {
    'A': ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    'B': ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    'C': ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    'D': ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    'E': ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    'F': ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    'G': ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    'H': ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    'I': ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    'J': ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    'K': ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    'L': ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    'M': ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    'N': ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    'O': ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    'P': ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    'Q': ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    'R': ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    'S': ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    'T': ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    'U': ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    'V': ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    'W': ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    'X': ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    'Y': ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    'Z': ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    '0': ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    '1': ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    '2': ["01110", "10001", "00001", "00110", "01000", "10000", "11111"],
    '3': ["11111", "00010", "00100", "00010", "00001", "10001", "01110"],
    '4': ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    '5': ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    '6': ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    '7': ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    '8': ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    '9': ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    ' ': ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
    '.': ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    ',': ["00000", "00000", "00000", "00000", "01100", "00100", "01000"],
    ':': ["00000", "01100", "01100", "00000", "01100", "01100", "00000"],
    ';': ["00000", "01100", "01100", "00000", "01100", "00100", "01000"],
    "'": ["00100", "00100", "01000", "00000", "00000", "00000", "00000"],
    '-': ["00000", "00000", "00000", "01110", "00000", "00000", "00000"],
    '/': ["00001", "00010", "00010", "00100", "01000", "01000", "10000"],
    '(': ["00010", "00100", "01000", "01000", "01000", "00100", "00010"],
    ')': ["01000", "00100", "00010", "00010", "00010", "00100", "01000"],
    '%': ["11001", "11010", "00010", "00100", "01000", "01011", "10011"],
    '$': ["00100", "01111", "10100", "01110", "00101", "11110", "00100"],
    '&': ["01100", "10010", "10100", "01000", "10101", "10010", "01101"],
    '+': ["00000", "00100", "00100", "01110", "00100", "00100", "00000"],
    '=': ["00000", "00000", "11111", "00000", "11111", "00000", "00000"],
    '?': ["01110", "10001", "00001", "00110", "00100", "00000", "00100"],
    '!': ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    '*': ["00000", "10101", "01110", "10101", "00000", "00000", "00000"],
    '"': ["01010", "01010", "00000", "00000", "00000", "00000", "00000"],
    'X2': ["00000", "10001", "01010", "00100", "01010", "10001", "00000"],
}

# Map characters the font lacks onto close equivalents.
ALIASES = {'\u2019': "'", '\u2018': "'", '\u2014': '-', '\u2013': '-',
           '\u00b7': '.', '\u00d7': 'X2', '\u00b0': 'O', '\u201c': '"',
           '\u201d': '"', '\u2026': '.', '\u2011': '-'}


def glyph(ch):
    ch = ALIASES.get(ch, ch)
    return FONT.get(ch, FONT['?'])


def text_width(text, scale):
    return len(text) * 6 * scale - scale


# -------------------------------------------------------------- canvas ----
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg) * (w * h)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            self.px[base:(base + (x1 - x0) * 3)] = bytes(color) * (x1 - x0)

    def hline(self, x, y, w, color, thick=1):
        self.fill_rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.fill_rect(x, y, thick, h, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.fill_rect(x0, y0, thick, thick, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def fill_triangle(self, ax, ay, bx, by, cx, cy, color):
        minx = max(0, min(ax, bx, cx))
        maxx = min(self.w - 1, max(ax, bx, cx))
        miny = max(0, min(ay, by, cy))
        maxy = min(self.h - 1, max(ay, by, cy))
        d = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if d == 0:
            return
        for yy in range(miny, maxy + 1):
            for xx in range(minx, maxx + 1):
                w0 = ((by - cy) * (xx - cx) + (cx - bx) * (yy - cy)) / d
                w1 = ((cy - ay) * (xx - cx) + (ax - cx) * (yy - cy)) / d
                w2 = 1 - w0 - w1
                if w0 >= 0 and w1 >= 0 and w2 >= 0:
                    self.set(xx, yy, color)

    def fill_circle(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            dy = yy - cy
            dx = int((r * r - dy * dy) ** 0.5)
            self.fill_rect(cx - dx, yy, 2 * dx + 1, 1, color)

    def draw_text(self, x, y, text, scale, color, align='left'):
        text = text.upper()
        if align == 'center':
            x -= text_width(text, scale) // 2
        elif align == 'right':
            x -= text_width(text, scale)
        cx = x
        for ch in text:
            g = glyph(ch)
            for row in range(7):
                bits = g[row]
                for col in range(5):
                    if bits[col] == '1':
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       scale, scale, color)
            cx += 6 * scale
        return cx

    def wrap(self, text, scale, max_w):
        """Greedy word wrap; returns list of lines fitting max_w pixels."""
        words = text.upper().split(' ')
        lines = []
        cur = ''
        for word in words:
            trial = word if not cur else cur + ' ' + word
            if text_width(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    def draw_para(self, x, y, text, scale, max_w, color, leading=None):
        if leading is None:
            leading = 7 * scale + 4
        for line in self.wrap(text, scale, max_w):
            self.draw_text(x, y, line, scale, color)
            y += leading
        return y


# ----------------------------------------------------------- pictograms ----
def draw_flame(cv, x, y, w, h, color=ORANGE):
    """Simple flame: outer triangle-ish flame + inner red core."""
    cv.fill_triangle(x + w // 2, y, x, y + h, x + w, y + h, color)
    cv.fill_triangle(x + w // 2, y + h // 3, x + w // 4, y + h,
                     x + 3 * w // 4, y + h, RED)


def pict_lead_oil(cv, x0, y0, x1, y1):
    """Oil barrel with flame + Brent price tag."""
    cv.fill_rect(x0, y0, x1 - x0, y1 - y0, (255, 255, 255))
    cv.draw_text((x0 + x1) // 2, y0 + 8, "RAS TANURA", 2, GREY, align='center')
    # barrel
    bx, bw = x0 + 30, 96
    by, bh = y0 + 100, 90
    cv.fill_rect(bx, by, bw, bh, BLUE)
    cv.fill_rect(bx, by, bw, 6, INK)
    cv.fill_rect(bx, by + bh // 2 - 3, bw, 6, INK)
    cv.fill_rect(bx, by + bh - 6, bw, 6, INK)
    # flame above the barrel
    draw_flame(cv, bx + 18, by - 52, 60, 46)
    # price, centred under the barrel
    cv.draw_text((x0 + x1) // 2, by + bh + 12, "$94.61", 4, RED, align='center')
    cv.draw_text((x0 + x1) // 2, by + bh + 44, "BRENT +3.5%", 2, INK,
                 align='center')
    cv.hline(x0 + 8, y1 - 8, x1 - x0 - 16, INK, 2)


def pict_tariffs(cv, x0, y0, w, h):
    cv.fill_rect(x0, y0, w, h, (255, 255, 255))
    # ascending bars, then a red down arrow
    base = y0 + h - 12
    bars = [26, 40, 54]
    bx = x0 + 10
    for bh in bars:
        cv.fill_rect(bx, base - bh, 20, bh, BLUE)
        bx += 26
    cv.line(x0 + 8, y0 + 14, x0 + w - 10, y0 + h - 30, RED, 4)
    cv.fill_triangle(x0 + w - 10, y0 + h - 30, x0 + w - 26, y0 + h - 34,
                     x0 + w - 16, y0 + h - 14, RED)


def pict_gaza(cv, x0, y0, w, h):
    cv.fill_rect(x0, y0, w, h, (255, 255, 255))
    # building with a crack
    bx, by, bw, bh = x0 + 24, y0 + 10, 56, 66
    cv.fill_rect(bx, by, bw, bh, BLUE)
    for wy in (by + 10, by + 28, by + 46):
        for wx in (bx + 8, bx + 30):
            cv.fill_rect(wx, wy, 12, 12, PAPER)
    cv.line(bx + 28, by, bx + 18, by + 30, RED, 3)
    cv.line(bx + 18, by + 30, bx + 34, by + 52, RED, 3)
    cv.line(bx + 34, by + 52, bx + 26, by + bh, RED, 3)
    # rubble
    cv.fill_triangle(x0 + 12, y0 + h - 12, x0 + 30, y0 + h - 26,
                     x0 + 48, y0 + h - 12, GREY)
    cv.fill_triangle(x0 + 60, y0 + h - 12, x0 + 76, y0 + h - 24,
                     x0 + 94, y0 + h - 12, GREY)


def pict_ukraine(cv, x0, y0, w, h):
    cv.fill_rect(x0, y0, w, h, (255, 255, 255))
    # refinery towers + flame
    cv.fill_rect(x0 + 14, y0 + 28, 16, 40, BLUE)
    cv.fill_rect(x0 + 40, y0 + 18, 16, 50, BLUE)
    cv.fill_rect(x0 + 66, y0 + 38, 16, 30, BLUE)
    cv.fill_rect(x0 + 10, y0 + 68, 76, 5, INK)
    draw_flame(cv, x0 + 40, y0 + 2, 16, 16)


def pict_space(cv, x0, y0, w, h):
    cv.fill_rect(x0, y0, w, h, (255, 255, 255))
    # stars
    for sx, sy in ((x0 + 8, y0 + 8), (x0 + 88, y0 + 6), (x0 + 96, y0 + 36),
                   (x0 + 6, y0 + 44)):
        cv.fill_rect(sx - 1, sy - 4, 2, 9, INK)
        cv.fill_rect(sx - 4, sy - 1, 9, 2, INK)
    # rocket
    rx = x0 + 44
    cv.fill_triangle(rx + 11, y0 + 8, rx, y0 + 26, rx + 22, y0 + 26, RED)
    cv.fill_rect(rx, y0 + 26, 22, 30, BLUE)
    cv.fill_circle(rx + 11, y0 + 38, 5, PAPER)
    cv.fill_triangle(rx, y0 + 56, rx - 10, y0 + 68, rx, y0 + 62, RED)
    cv.fill_triangle(rx + 22, y0 + 56, rx + 32, y0 + 68, rx + 22, y0 + 62, RED)
    draw_flame(cv, rx + 5, y0 + 60, 12, 12)


# -------------------------------------------------------------- layout ----
def draw_page(cv):
    # outer double border
    cv.fill_rect(14, 14, W - 28, 2, INK)
    cv.fill_rect(14, H - 16, W - 28, 2, INK)
    cv.vline(14, 14, H - 28, INK, 2)
    cv.vline(W - 16, 14, H - 28, INK, 2)

    # masthead
    cv.draw_text(W // 2, 44, "THE WORLD IN ONE DAY", 7, INK, align='center')
    cv.draw_text(W // 2, 102, "ONE DAY. EVERY STORY THAT MATTERED.", 2, GREY,
                 align='center')

    # date band
    cv.fill_rect(40, 126, W - 80, 42, RED)
    cv.draw_text(W // 2, 137, "THURSDAY \u00b7 26 NOVEMBER 2026", 4, (255, 255, 255),
                 align='center')
    cv.hline(40, 176, W - 80, INK, 2)

    # ---- lead story: Gulf oil shock ----
    cv.draw_text(40, 194, "MIDDLE EAST \u00b7 ENERGY", 2, RED)
    cv.draw_text(40, 220, "GULF OIL SHOCK", 6, INK)
    cv.draw_para(40, 288,
                 "Houthis claim a strike on Saudi Arabia's Ras Tanura "
                 "refinery. Riyadh says it shot down four drones. Brent "
                 "crude jumps 3.5% to $94.61 as tankers are hit by mines "
                 "in the Strait of Hormuz.",
                 3, 660, INK)
    pict_lead_oil(cv, 720, 194, 984, 452)
    cv.hline(40, 470, W - 80, INK, 3)

    # ---- 2x2 grid ----
    cells = [
        # (col, row, kicker, headline, sub, pictogram)
        (0, 0, "TRADE \u00b7 WASHINGTON",
         "NEW US TARIFFS HIT 14 PARTNERS",
         "Washington proposes levies on 14 partners to fight factory "
         "overcapacity; Taiwan faces up to 15%. Stock futures slide.",
         pict_tariffs),
        (1, 0, "GAZA \u00b7 CEASEFIRE",
         "CEASEFIRE UNDER STRAIN IN GAZA",
         "Israel kills Hamas security chief Abuelouf in a Gaza strike. "
         "Mediators urge calm as the aid crisis deepens.",
         pict_gaza),
        (0, 1, "UKRAINE \u00b7 RUSSIA",
         "UKRAINE HITS REFINERIES; PUTIN VOWS REPLY",
         "Ukraine strikes two Russian oil refineries overnight. At least "
         "14 refineries have been hit since November began.",
         pict_ukraine),
        (1, 1, "SPACE \u00b7 ASIA",
         "PAKISTAN'S FIRST ASTRONAUT TO TIANGONG",
         "China picks Muhammad Zeeshan Ali for Shenzhou-24 \u2014 the "
         "first foreign astronaut bound for its space station.",
         pict_space),
    ]
    col_x = [40, 528]
    col_w = 456
    row_y = [492, 708]
    row_h = 196
    for col, row, kicker, headline, sub, pict in cells:
        x = col_x[col]
        y = row_y[row]
        cv.draw_text(x, y, kicker, 2, RED)
        y_head = y + 24
        # headline wraps within the text column (pictogram on the right)
        lines = cv.wrap(headline, 3, col_w - 132)
        hy = y_head
        for ln in lines:
            cv.draw_text(x, hy, ln, 3, INK)
            hy += 25
        pict(cv, x + col_w - 118, y_head - 2, 118, 76)
        cv.draw_para(x, y + 100, sub, 2, col_w, INK, leading=18)
    # grid dividers
    cv.vline(512, 492, 2 * row_h + 20, INK, 1)
    cv.hline(40, 698, W - 80, INK, 1)

    # ---- footer ----
    cv.hline(40, 916, W - 80, INK, 2)
    cv.draw_para(40, 930,
                 "ALSO TODAY: INDIA MARKS 18 YEARS SINCE THE 26/11 "
                 "ATTACKS \u00b7 US THANKSGIVING AS TURKEY HITS A RECORD "
                 "$2 A POUND \u00b7 SOLOMON ISLANDS-AUSTRALIA TREATY",
                 2, W - 80, INK, leading=18)
    cv.draw_text(40, 972,
                 "SOURCES: REUTERS \u00b7 OBSERVER VOICE \u00b7 SIMPLELIFE.NEWS "
                 "\u00b7 OILPRICE", 2, GREY)


# ----------------------------------------------------------------- png ----
def png_bytes(cv):
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)  # filter: none
        raw += cv.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    cv = Canvas(W, H, PAPER)
    draw_page(cv)
    data = png_bytes(cv)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes, %dx%d)" % (path, len(data), W, H))


if __name__ == "__main__":
    main()

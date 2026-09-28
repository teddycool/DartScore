"""Render the three current-implementation diagrams with Pillow."""

from math import atan2, cos, sin
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


OUT = Path(__file__).resolve().parents[1] / "images"
OUT.mkdir(parents=True, exist_ok=True)
FONT_DIR = Path(os.environ.get("DARTSCORE_DIAGRAM_FONT_DIR", "/usr/share/fonts/truetype/dejavu"))
INK = "#173044"
MUTED = "#476476"
BG = "#f7fafc"
BLUE = "#2563a6"
BLUE_BG = "#e8f2fc"
TEAL = "#007e85"
TEAL_BG = "#e3f7f3"
AMBER = "#a65b08"
AMBER_BG = "#fff2d8"
GREEN = "#287b49"
GREEN_BG = "#e8f6ea"
LINE = "#89a2b2"


def font(size, bold=False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    path = FONT_DIR / name
    if not path.is_file():
        raise FileNotFoundError(
            f"Missing {path}. Install the DejaVu Sans fonts, or set "
            "DARTSCORE_DIAGRAM_FONT_DIR to a directory containing "
            "DejaVuSans.ttf and DejaVuSans-Bold.ttf."
        )
    return ImageFont.truetype(str(path), size)


def canvas(size, title, subtitle):
    image = Image.new("RGB", size, BG)
    draw = ImageDraw.Draw(image)
    draw.text((64, 42), title, fill=INK, font=font(42, True))
    draw.text((65, 106), subtitle, fill=MUTED, font=font(23))
    draw.line([(64, 153), (size[0] - 64, 153)], fill="#cbdce4", width=2)
    return image, draw


def centered(draw, xy, value, size, color=INK, bold=False):
    x, y = xy
    f = font(size, bold)
    bounds = draw.textbbox((0, 0), value, font=f)
    draw.text((x - (bounds[2] - bounds[0]) / 2,
               y - (bounds[3] - bounds[1]) / 2 - bounds[1]),
              value, fill=color, font=f)


def box(draw, rect, title, detail, stroke, fill, *, title_size=25, detail_size=19):
    draw.rounded_rectangle(rect, radius=19, fill=fill, outline=stroke, width=3)
    x1, y1, x2, y2 = rect
    centered(draw, ((x1 + x2) / 2, y1 + 34), title, title_size, stroke, True)
    for index, line in enumerate(detail.split("\n")):
        centered(draw, ((x1 + x2) / 2, y1 + 71 + 29 * index), line, detail_size, INK)


def arrow(draw, points, color=INK, width=4, head=14):
    draw.line(points, fill=color, width=width, joint="curve")
    a, b = points[-2:]
    angle = atan2(b[1] - a[1], b[0] - a[0])
    sides = [(b[0] - head * cos(angle + delta),
              b[1] - head * sin(angle + delta)) for delta in (-0.6, 0.6)]
    draw.polygon([b, *sides], fill=color)


def pill(draw, rect, value, color, fill, size=20):
    draw.rounded_rectangle(rect, radius=14, fill=fill, outline=color, width=2)
    x1, y1, x2, y2 = rect
    centered(draw, ((x1 + x2) / 2, (y1 + y2) / 2), value, size, color, True)


def render_interaction():
    image, draw = canvas((1800, 1390), "Engine ↔ presentation", "Current HTTP request and event path · Pi 5 is authoritative")
    xs = [175, 535, 895, 1255, 1615]
    actors = [("Browser", "Pi 4B", TEAL, TEAL_BG),
              ("Presentation", "same-origin proxy", TEAL, TEAL_BG),
              ("Engine API", "Pi 5", BLUE, BLUE_BG),
              ("DurableSession", "SQLite journal", BLUE, BLUE_BG),
              ("Game core", "input + rules", BLUE, BLUE_BG)]
    for x, (name, detail, stroke, fill) in zip(xs, actors):
        box(draw, (x - 150, 185, x + 150, 299), name, detail, stroke, fill, title_size=23)
        draw.line((x, 305, x, 1280), fill=LINE, width=2)
    messages = [
        (0, 1, "1 · GET /state", TEAL),
        (1, 2, "2 · forward GET", TEAL),
        (2, 3, "3 · read snapshot", BLUE),
        (3, 2, "4 · snapshot", BLUE),
        (2, 1, "5 · JSON state", TEAL),
        (1, 0, "6 · display state", TEAL),
        (0, 1, "7 · open /events", TEAL),
        (1, 2, "8 · stream SSE", TEAL),
        (0, 1, "9 · POST game command", TEAL),
        (1, 2, "10 · forward command", TEAL),
        (2, 3, "11 · check revision and request ID", BLUE),
        (3, 4, "12 · apply review or round action", BLUE),
        (4, 3, "13 · score or pending result", GREEN),
        (3, 2, "14 · commit then respond", GREEN),
        (2, 1, "15 · response + SSE", TEAL),
        (1, 0, "16 · notify browser", TEAL),
        (0, 1, "17 · refresh /state", TEAL),
    ]
    for index, (src, dst, label, color) in enumerate(messages):
        y = 338 + index * 57
        start = xs[src] + (19 if dst > src else -19)
        end = xs[dst] + (-19 if dst > src else 19)
        arrow(draw, [(start, y), (end, y)], color, 3, 12)
        left = min(start, end) + 16
        draw.rounded_rectangle((left, y - 34, left + draw.textlength(label, font=font(18)) + 18, y - 5),
                               radius=6, fill=BG)
        draw.text((left + 8, y - 32), label, font=font(18), fill=color)
    pill(draw, (75, 1310, 1725, 1366),
         "The Pi 4B never applies scores · the Pi 5 journals accepted actions before publishing state", BLUE, BLUE_BG, 21)
    image.save(OUT / "current-interaction.png", optimize=True)


def render_round():
    image, draw = canvas((1800, 1120), "One three-dart round", "Accepted darts and pending candidates share three slots")
    box(draw, (85, 370, 485, 560), "Collecting", "0–2 accepted darts\nremaining slots available", BLUE, BLUE_BG, title_size=32, detail_size=22)
    box(draw, (700, 370, 1100, 560), "Reviewing", "uncertain candidates\nordered by captured_at", AMBER, AMBER_BG, title_size=32, detail_size=22)
    box(draw, (1315, 370, 1715, 560), "Round complete", "3 accepted darts\nno pending review", GREEN, GREEN_BG, title_size=32, detail_size=22)
    arrow(draw, [(485, 435), (700, 435)], AMBER, 5)
    centered(draw, (590, 402), "Uncertain hit", 21, AMBER, True)
    arrow(draw, [(700, 507), (485, 507)], BLUE, 5)
    centered(draw, (590, 539), "Resolved, <3 scored", 18, BLUE)
    arrow(draw, [(1100, 435), (1315, 435)], GREEN, 5)
    centered(draw, (1207, 402), "Third scored", 21, GREEN, True)
    arrow(draw, [(485, 329), (1315, 329)], GREEN, 4)
    centered(draw, (900, 296), "Third confirmed dart, no review", 21, GREEN, True)
    arrow(draw, [(1515, 560), (1515, 698), (285, 698), (285, 560)], BLUE, 5)
    pill(draw, (625, 656, 1190, 701), "Remove darts / Next round · total retained", BLUE, BLUE_BG, 20)
    pill(draw, (94, 774, 545, 857), "Confirmed hit: score now", BLUE, BLUE_BG, 20)
    pill(draw, (672, 774, 1128, 857), "Reject false detection: free slot", AMBER, AMBER_BG, 19)
    pill(draw, (1250, 774, 1704, 857), "Accepted zero: counts as a dart", GREEN, GREEN_BG, 18)
    centered(draw, (900, 950), "Confirmed hits behind a pending review wait, then score automatically in order.", 23, INK)
    centered(draw, (900, 996), "Pause preserves the round; throws during pause are ignored.", 22, MUTED)
    image.save(OUT / "current-round.png", optimize=True)


def render_concerns():
    image, draw = canvas((1800, 1320), "Two Pis, separate responsibilities", "Implemented components and the current camera-free input boundary")
    draw.rounded_rectangle((65, 185, 890, 976), radius=30, fill="#f1f7fd", outline=BLUE, width=4)
    draw.rounded_rectangle((975, 185, 1735, 976), radius=30, fill="#effaf7", outline=TEAL, width=4)
    centered(draw, (478, 229), "PI 5 · ENGINE", 30, BLUE, True)
    centered(draw, (1355, 229), "PI 4B · PRESENTATION", 30, TEAL, True)
    box(draw, (283, 285, 678, 395), "HTTP API + SSE", "commands · state · health", BLUE, "#ffffff")
    box(draw, (283, 470, 678, 580), "DurableSession", "request IDs · revisions", BLUE, "#ffffff")
    box(draw, (112, 660, 485, 770), "InputCoordinator", "candidates · review order", BLUE, "#ffffff", title_size=23)
    box(draw, (530, 660, 836, 770), "GameService", "score · round rules", BLUE, "#ffffff", title_size=23)
    box(draw, (292, 839, 670, 949), "SQLite", "durable action journal", BLUE, "#ffffff")
    arrow(draw, [(480, 395), (480, 470)], BLUE)
    arrow(draw, [(421, 580), (300, 660)], BLUE)
    arrow(draw, [(485, 714), (530, 714)], BLUE)
    arrow(draw, [(540, 580), (510, 610), (510, 813), (480, 839)], BLUE)
    box(draw, (1140, 285, 1565, 395), "Browser scoreboard", "view · review controls · reconnect", TEAL, "#ffffff", title_size=23)
    box(draw, (1140, 580, 1565, 690), "Presentation server", "static page · limited API proxy", TEAL, "#ffffff", title_size=23)
    arrow(draw, [(1352, 395), (1352, 580)], TEAL)
    arrow(draw, [(1140, 628), (954, 628), (954, 339), (678, 339)], TEAL, 5)
    pill(draw, (1010, 758, 1700, 820), "HTTP JSON commands/state · SSE events", TEAL, TEAL_BG, 20)
    box(draw, (335, 1040, 960, 1158), "Developer simulator · local test host", "Loopback dev input only · no live camera capture", AMBER, AMBER_BG,
        title_size=24, detail_size=18)
    arrow(draw, [(335, 1098), (32, 1098), (32, 339), (283, 339)], AMBER, 4)
    centered(draw, (900, 1250), "Planned: two cameras · image evidence · 301/501 · status LEDs · kiosk startup", 22, MUTED)
    image.save(OUT / "current-concerns.png", optimize=True)


if __name__ == "__main__":
    render_interaction()
    render_round()
    render_concerns()
    for image_path in sorted(OUT.glob("current-*.png")):
        print(image_path.relative_to(OUT.parent))

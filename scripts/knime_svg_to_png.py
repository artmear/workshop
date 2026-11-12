"""Turn the workflow.svg that KNIME saves in each workflow folder into a PNG.

KNIME writes node names as HTML inside <foreignObject>, which librsvg does not draw.
This replaces each one with plain SVG <text> (wrapped to the label box) and renders
the result with librsvg + cairo at 2x scale.

    python3 scripts/knime_svg_to_png.py ~/knime-workspace/wine/workflow.svg docs/images/knime-wine.png
"""
import html
import re
import sys
import warnings

import cairo
import gi

gi.require_version("Rsvg", "2.0")
from gi.repository import Rsvg  # noqa: E402

# get_dimensions/render_cairo are deprecated, but their replacements need librsvg >= 2.52
warnings.filterwarnings("ignore", category=DeprecationWarning)

FONT_PX = 13
CHARS_PER_LINE = 17  # fits the 120 px label box at 13 px bold condensed
LINE_H = 15


def wrap(text):
    lines, cur = [], ""
    for word in text.split():
        if cur and len(cur) + 1 + len(word) > CHARS_PER_LINE:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    return lines + [cur] if cur else lines


def to_text(match):
    x, y, w, h = (float(match.group(i)) for i in range(1, 5))
    inner = re.sub(r"<[^>]+>", " ", match.group(5))
    label = html.unescape(" ".join(inner.split()))
    if not label:
        return ""
    lines = wrap(label)
    cx = x + w / 2
    bottom = y + h - 3  # labels sit right above the node
    first = bottom - (len(lines) - 1) * LINE_H
    spans = "".join(
        f'<tspan x="{cx}" y="{first + i * LINE_H}">{html.escape(t)}</tspan>' for i, t in enumerate(lines)
    )
    return (f'<text text-anchor="middle" font-family="Roboto Condensed, Arial Narrow, sans-serif" '
            f'font-size="{FONT_PX}" font-weight="bold" fill="#3e3a39">{spans}</text>')


src, dst = sys.argv[1], sys.argv[2]
svg = open(src, encoding="utf-8").read()
svg = re.sub(
    r'<foreignObject x="([-\d.]+)" y="([-\d.]+)" width="([-\d.]+)" height="([-\d.]+)"[^>]*>(.*?)</foreignObject>',
    to_text, svg, flags=re.S,
)
handle = Rsvg.Handle.new_from_data(svg.encode("utf-8"))
dim = handle.get_dimensions()
scale = 2
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, dim.width * scale, dim.height * scale)
ctx = cairo.Context(surface)
ctx.set_source_rgb(1, 1, 1)
ctx.paint()
ctx.scale(scale, scale)
handle.render_cairo(ctx)
surface.write_to_png(dst)
print(f"wrote {dst} ({dim.width * scale}x{dim.height * scale})")

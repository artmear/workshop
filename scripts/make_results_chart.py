"""Draw docs/images/results.svg: test accuracy (and kappa) per dataset x algorithm.

    python3 scripts/make_results_chart.py
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "docs" / "images" / "results.svg"

# (label, accuracy, kappa, kind)
GROUPS = {
    "Wine": {"baseline": 43.6, "bars": [("KNN", 56.3, 0.32, "knn"),
                                        ("Random Forest (KNIME)", 65.3, 0.44, "rf"),
                                        ("Random Forest (Python ref.)", 68.1, 0.50, "ref")]},
    "Adult": {"baseline": 75.1, "bars": [("KNN", 81.1, 0.48, "knn"),
                                         ("Random Forest (KNIME)", 75.3, 0.01, "rf"),
                                         ("Random Forest (Python ref.)", 85.3, 0.59, "ref")]},
}
COLORS = {"knn": ("#4A9A3F", "#4A9A3F"), "rf": ("#3A78C2", "#3A78C2"), "ref": ("#ffffff", "#3A78C2")}

W, H = 920, 470
top, bottom, left = 60, 390, 70
bar_w, gap, group_gap = 90, 18, 110
scale = (bottom - top) / 100

out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
       'font-family="Helvetica, Arial, sans-serif">',
       f'<rect width="{W}" height="{H}" rx="12" fill="#ffffff"/>',
       '<text x="30" y="34" font-size="16" font-weight="bold" fill="#1f2328">Test accuracy by dataset and algorithm</text>']
for v in range(0, 101, 20):
    y = bottom - v * scale
    out.append(f'<line x1="{left}" y1="{y}" x2="{W - 30}" y2="{y}" stroke="#eaeef2"/>')
    out.append(f'<text x="{left - 10}" y="{y + 4}" font-size="11" text-anchor="end" fill="#57606a">{v}%</text>')

x = left + 40
for gname, g in GROUPS.items():
    gx0 = x
    for label, acc, kap, kind in g["bars"]:
        fill, stroke = COLORS[kind]
        y = bottom - acc * scale
        dash = ' stroke-dasharray="5 3"' if kind == "ref" else ""
        out.append(f'<rect x="{x}" y="{y}" width="{bar_w}" height="{acc * scale}" fill="{fill}" '
                   f'stroke="{stroke}" stroke-width="2"{dash} rx="3"/>')
        out.append(f'<text x="{x + bar_w / 2}" y="{y - 20}" font-size="13" font-weight="bold" '
                   f'text-anchor="middle" fill="#1f2328">{acc:.1f}%</text>')
        out.append(f'<text x="{x + bar_w / 2}" y="{y - 6}" font-size="11" text-anchor="middle" '
                   f'fill="#57606a">kappa {kap:.2f}</text>')
        x += bar_w + gap
    gx1 = x - gap
    by = bottom - g["baseline"] * scale
    out.append(f'<line x1="{gx0 - 8}" y1="{by}" x2="{gx1 + 8}" y2="{by}" stroke="#cf222e" '
               'stroke-width="1.6" stroke-dasharray="6 4"/>')
    out.append(f'<text x="{gx1 + 10}" y="{by + 4}" font-size="11" fill="#cf222e">{g["baseline"]:.1f}%</text>')
    out.append(f'<text x="{(gx0 + gx1) / 2}" y="{bottom + 24}" font-size="14" font-weight="bold" '
               f'text-anchor="middle" fill="#1f2328">{gname}</text>')
    x += group_gap - gap

ly = H - 34
items = [("knn", "KNN (KNIME)"), ("rf", "Random Forest (KNIME 5.12 node)"),
         ("ref", "Random Forest, Python reference")]
lx = 30
for kind, text in items:
    fill, stroke = COLORS[kind]
    dash = ' stroke-dasharray="4 2"' if kind == "ref" else ""
    out.append(f'<rect x="{lx}" y="{ly - 11}" width="16" height="14" rx="2" fill="{fill}" stroke="{stroke}" stroke-width="2"{dash}/>')
    out.append(f'<text x="{lx + 22}" y="{ly}" font-size="12" fill="#424a53">{text}</text>')
    lx += 22 + len(text) * 6.6 + 24
out.append(f'<line x1="{lx}" y1="{ly - 4}" x2="{lx + 22}" y2="{ly - 4}" stroke="#cf222e" stroke-width="1.6" stroke-dasharray="6 4"/>')
out.append(f'<text x="{lx + 28}" y="{ly}" font-size="12" fill="#424a53">majority-class baseline</text>')
out.append("</svg>")
OUT.write_text("\n".join(out) + "\n")
print(f"wrote {OUT}")

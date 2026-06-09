from pathlib import Path

import ezdxf
import matplotlib.pyplot as plt
from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs/cad"
DXF = OUT / "office_cabling_system_diagram.dxf"
PNG = OUT / "office_cabling_system_diagram.png"

FLOORS = [
    ("4F", "4FD", 72, 72, 3, 4),
    ("3F", "3FD", 48, 48, 2, 3),
    ("2F NORTH", "2-1FD", 26, 26, 2, 2),
    ("2F SOUTH", "2-2FD", 31, 31, 2, 2),
    ("1F NORTH", "1-1FD", 23, 22, 1, 1),
    ("1F SOUTH", "1-2FD", 29, 28, 2, 2),
]


def box(msp, x, y, w, h, text, layer="EQUIP", height=2.6):
    msp.add_lwpolyline(
        [(x, y), (x + w, y), (x + w, y + h), (x, y + h)],
        close=True,
        dxfattribs={"layer": layer},
    )
    entity = msp.add_mtext(
        text.replace("\n", r"\P"),
        dxfattribs={
            "char_height": height,
            "layer": "TEXT",
            "attachment_point": 5,
            "width": w - 0.8,
        },
    )
    entity.set_location((x + w / 2, y + h / 2))


def line(msp, points, layer):
    msp.add_lwpolyline(points, dxfattribs={"layer": layer, "lineweight": 35})


def text(msp, value, point, height=2.5, layer="TEXT"):
    entity = msp.add_text(value, dxfattribs={"height": height, "layer": layer})
    entity.set_placement(point)


def build():
    doc = ezdxf.new("R2010", setup=True)
    doc.layers.add("EQUIP", color=250)
    doc.layers.add("DATA", color=5)
    doc.layers.add("VOICE", color=1)
    doc.layers.add("TEXT", color=250)
    doc.layers.add("FRAME", color=250)
    msp = doc.modelspace()

    x_info, x_fd, x_patch, x_sw, x_liu = 8, 40, 65, 91, 116
    data_bus, voice_bus = 140, 146
    ys = [116, 96, 76, 56, 36, 16]

    for y, (floor, fd, td, tp, sw, voice_cables) in zip(ys, FLOORS):
        text(msp, floor, (0, y + 5), 3.2)
        text(msp, f"TD {td} / TP {tp}", (0, y), 2.8)
        box(msp, x_fd, y - 2, 15, 12, fd, height=3.0)
        box(msp, x_patch, y + 3, 19, 7, "RJ45 PATCH", height=2.2)
        box(msp, x_sw, y + 3, 17, 7, f"SW x {sw}")
        box(msp, x_liu, y + 3, 14, 7, "LIU")
        box(msp, 79, y - 6, 20, 7, "IDC PATCH")

        line(msp, [(x_info + 21, y + 4), (x_fd, y + 4)], "DATA")
        line(msp, [(x_fd + 15, y + 7), (x_patch, y + 7)], "DATA")
        line(msp, [(x_patch + 19, y + 7), (x_sw, y + 7)], "DATA")
        line(msp, [(x_sw + 17, y + 7), (x_liu, y + 7)], "DATA")
        line(msp, [(x_liu + 14, y + 7), (data_bus, y + 7)], "DATA")

        line(msp, [(x_fd + 15, y + 1), (72, y + 1), (72, y - 2), (79, y - 2)], "VOICE")
        line(msp, [(99, y - 2), (voice_bus, y - 2)], "VOICE")
        text(msp, f"25P x {voice_cables}", (108, y - 5), 2.2, "VOICE")

    line(msp, [(data_bus, 13), (data_bus, 126)], "DATA")
    line(msp, [(voice_bus, 13), (voice_bus, 126)], "VOICE")

    box(msp, 158, 58, 25, 18, "BD\nMAIN DISTRIBUTOR", height=2.5)
    box(msp, 194, 82, 27, 9, "CORE SWITCH")
    box(msp, 194, 43, 27, 9, "PBX")
    box(msp, 231, 82, 30, 9, "FIREWALL / SERVER")
    box(msp, 231, 43, 30, 9, "ODF / DDF")
    box(msp, 272, 58, 30, 18, "CARRIER\nNETWORK", height=2.7)

    line(msp, [(data_bus, 69), (158, 69)], "DATA")
    line(msp, [(voice_bus, 63), (158, 63)], "VOICE")
    line(msp, [(183, 70), (188, 70), (188, 86), (194, 86)], "DATA")
    line(msp, [(183, 63), (188, 63), (188, 47), (194, 47)], "VOICE")
    line(msp, [(221, 86), (231, 86)], "DATA")
    line(msp, [(221, 47), (231, 47)], "VOICE")
    line(msp, [(261, 86), (267, 86), (267, 71), (272, 71)], "DATA")
    line(msp, [(261, 47), (267, 47), (267, 63), (272, 63)], "VOICE")

    text(msp, "B1 MAIN EQUIPMENT ROOM", (158, 96), 3.5)
    line(msp, [(44, 2), (58, 2)], "DATA")
    text(msp, "DATA: CAT6 UTP + 12-CORE SM FIBER", (61, 0.5), 2.5)
    line(msp, [(170, 2), (184, 2)], "VOICE")
    text(msp, "VOICE: CAT6 UTP + CAT3 25-PAIR CABLE", (187, 0.5), 2.5)

    msp.add_lwpolyline(
        [(-5, -4), (307, -4), (307, 132), (-5, 132)],
        close=True,
        dxfattribs={"layer": "FRAME", "lineweight": 50},
    )
    text(msp, "OFFICE BUILDING STRUCTURED CABLING SYSTEM DIAGRAM", (70, 127), 4.5)
    text(msp, "PROJECT DATA: 229 DATA POINTS / 227 VOICE POINTS / 6 FD / 12 ACCESS SWITCHES", (63, -3), 2.2)
    return doc


def render(doc):
    fig, ax = plt.subplots(figsize=(16, 7.4), dpi=180)
    Frontend(RenderContext(doc), MatplotlibBackend(ax)).draw_layout(doc.modelspace())
    ax.set_xlim(-8, 310)
    ax.set_ylim(-7, 135)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    fig.savefig(PNG, bbox_inches="tight", pad_inches=0.08, facecolor="white")
    plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    doc = build()
    doc.saveas(DXF)
    render(doc)
    print(DXF)
    print(PNG)


if __name__ == "__main__":
    main()

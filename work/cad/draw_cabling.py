from __future__ import annotations

from pathlib import Path

import ezdxf
from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.disassemble import recursive_decompose
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "work/cad/base.dxf"
OUTPUT = ROOT / "outputs/cad/office_cabling_plans.dxf"
PREVIEW_DIR = ROOT / "outputs/cad"

LAYERS = {
    "point": ("综合布线-信息点", 1),
    "wire": ("综合布线-线路", 4),
    "equip": ("综合布线-设备", 6),
    "text": ("综合布线-标注", 1),
}

FLOORS = {
    "floor1": {
        "title": "一层综合布线平面图",
        "region": (1280000, 1350000, -408000, -345000),
        "fds": [(1318885, -362429, "1-1FD"), (1313192, -393104, "1-2FD")],
        "groups": [
            (1318885, -362429, [
                (1336016, -359046, 8),
                (1308500, -359072, 7),
                (1291851, -372717, 7),
            ]),
            (1313192, -393104, [
                (1301785, -390044, 11),
                (1297591, -384236, 9),
                (1322239, -386103, 4),
                (1317855, -388931, 2),
                (1329422, -360526, 2),
            ]),
        ],
        "data_only": [(1329422, -360526), (1317855, -388931)],
    },
    "floor2": {
        "title": "二层综合布线平面图",
        "region": (1280000, 1350000, -482000, -419000),
        "fds": [(1318889, -436679, "2-1FD"), (1313196, -467354, "2-2FD")],
        "groups": [
            (1318889, -436679, [
                (1337955, -430704, 5),
                (1334090, -430653, 5),
                (1317581, -431532, 4),
                (1310386, -432160, 4),
                (1303970, -432163, 4),
                (1291776, -446275, 4),
            ]),
            (1313196, -467354, [
                (1324976, -464490, 6),
                (1302738, -468663, 5),
                (1300326, -464927, 5),
                (1298126, -461679, 5),
                (1296024, -458241, 5),
                (1294184, -455255, 5),
            ]),
        ],
        "data_only": [],
    },
    "floor3": {
        "title": "三层综合布线平面图",
        "region": (1280000, 1350000, -555000, -495000),
        "fds": [(1313196, -541604, "3FD")],
        "groups": [
            (1313196, -541604, [
                (1338294, -510265, 4),
                (1333462, -509084, 4),
                (1317967, -510332, 4),
                (1312710, -510034, 4),
                (1308406, -510086, 4),
                (1302836, -542819, 4),
                (1300711, -539836, 4),
                (1298070, -535376, 4),
                (1296338, -532643, 4),
                (1301629, -507331, 4),
                (1321698, -540692, 4),
                (1321653, -533475, 4),
            ]),
        ],
        "data_only": [],
    },
    "floor4": {
        "title": "四层综合布线平面图",
        "region": (1280000, 1350000, -630000, -570000),
        "fds": [(1313196, -615854, "4FD")],
        "groups": [
            (1313196, -615854, [
                (1338128, -583970, 5),
                (1333677, -583970, 5),
                (1317835, -584347, 5),
                (1312994, -584347, 5),
                (1309462, -584402, 4),
                (1304840, -620584, 4),
                (1302763, -616700, 4),
                (1300667, -613827, 4),
                (1298429, -610232, 4),
                (1296234, -607022, 4),
                (1305402, -584418, 4),
                (1321574, -615115, 4),
                (1325031, -612834, 4),
                (1293976, -603088, 4),
                (1290552, -598002, 4),
                (1295276, -588657, 4),
                (1298992, -581170, 4),
            ]),
        ],
        "data_only": [],
    },
}


def add_layers(doc: ezdxf.document.Drawing) -> None:
    for name, color in LAYERS.values():
        if name not in doc.layers:
            doc.layers.add(name, color=color)
        else:
            doc.layers.get(name).color = color


def add_text(msp, text: str, point, height=420, layer=None) -> None:
    entity = msp.add_text(
        text,
        dxfattribs={"height": height, "layer": layer or LAYERS["text"][0]},
    )
    entity.set_placement(point)


def add_info_point(msp, x: float, y: float, count: int, fd) -> None:
    point_layer = LAYERS["point"][0]
    wire_layer = LAYERS["wire"][0]
    msp.add_circle((x, y), 260, dxfattribs={"layer": point_layer})
    msp.add_line((x - 180, y), (x + 180, y), dxfattribs={"layer": point_layer})
    msp.add_line((x, y - 180), (x, y + 180), dxfattribs={"layer": point_layer})
    add_text(msp, f"TD/TPx{count}", (x + 380, y + 180), 360)

    fx, fy = fd
    bend_x = fx - 1300 if x < fx else fx + 1300
    msp.add_lwpolyline(
        [(x, y), (bend_x, y), (bend_x, fy), (fx, fy)],
        dxfattribs={"layer": wire_layer},
    )


def add_data_only(msp, x: float, y: float, fd) -> None:
    point_layer = LAYERS["point"][0]
    wire_layer = LAYERS["wire"][0]
    x += 1000
    y -= 900
    msp.add_circle((x, y), 220, dxfattribs={"layer": point_layer})
    add_text(msp, "TDx1", (x + 330, y + 150), 340)
    fx, fy = fd
    bend_x = fx - 1000 if x < fx else fx + 1000
    msp.add_lwpolyline(
        [(x, y), (bend_x, y), (bend_x, fy), (fx, fy)],
        dxfattribs={"layer": wire_layer},
    )


def add_fd(msp, x: float, y: float, label: str) -> None:
    layer = LAYERS["equip"][0]
    size = 620
    msp.add_lwpolyline(
        [
            (x - size, y - size),
            (x + size, y - size),
            (x + size, y + size),
            (x - size, y + size),
        ],
        close=True,
        dxfattribs={"layer": layer},
    )
    add_text(msp, label, (x - 500, y + 850), 420, layer)


def draw_design(doc: ezdxf.document.Drawing) -> None:
    add_layers(doc)
    msp = doc.modelspace()
    for floor in FLOORS.values():
        for fx, fy, label in floor["fds"]:
            add_fd(msp, fx, fy, label)
        for fx, fy, rooms in floor["groups"]:
            for x, y, count in rooms:
                add_info_point(msp, x, y, count, (fx, fy))
        for index, (x, y) in enumerate(floor["data_only"]):
            fx, fy, _ = floor["fds"][min(index, len(floor["fds"]) - 1)]
            add_data_only(msp, x, y, (fx, fy))
        xmin, xmax, ymin, ymax = floor["region"]
        add_text(msp, floor["title"], (xmin + 2000, ymax - 2000), 700)

    msp.add_lwpolyline(
        [
            (1314600, -286500),
            (1316800, -286500),
            (1316800, -283800),
            (1314600, -283800),
        ],
        close=True,
        dxfattribs={"layer": LAYERS["equip"][0]},
    )
    add_text(msp, "BD主设备间", (1314500, -283300), 430)


def prepare_for_render(doc: ezdxf.document.Drawing) -> None:
    overlay = {value[0] for value in LAYERS.values()}
    for layer in doc.layers:
        if layer.dxf.name not in overlay:
            layer.color = 250
    msp = doc.modelspace()
    for entity in list(msp.query("INSERT")):
        try:
            list(recursive_decompose([entity]))
        except Exception:
            msp.delete_entity(entity)
    for entity in list(msp.query("ACAD_PROXY_ENTITY")):
        msp.delete_entity(entity)


def render_floors(doc: ezdxf.document.Drawing) -> None:
    prepare_for_render(doc)
    msp = doc.modelspace()
    for name, floor in FLOORS.items():
        xmin, xmax, ymin, ymax = floor["region"]
        fig, ax = plt.subplots(figsize=(15, 10), dpi=160)
        Frontend(RenderContext(doc), MatplotlibBackend(ax)).draw_layout(
            msp, finalize=False
        )
        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)
        ax.set_aspect("equal", adjustable="box")
        ax.axis("off")
        fig.patch.set_facecolor("white")
        ax.set_facecolor("white")
        fig.savefig(
            PREVIEW_DIR / f"{name}_cabling.png",
            dpi=180,
            bbox_inches="tight",
            pad_inches=0.05,
            facecolor="white",
        )
        plt.close(fig)


def main() -> None:
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    doc = ezdxf.readfile(SOURCE)
    draw_design(doc)
    doc.saveas(OUTPUT)
    render_doc = ezdxf.readfile(OUTPUT)
    render_floors(render_doc)
    print(OUTPUT)


if __name__ == "__main__":
    main()

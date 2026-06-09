from pathlib import Path

import ezdxf
import matplotlib.pyplot as plt
from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.enums import TextEntityAlignment


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs/cad"
DXF = OUT / "office_cabling_system_diagram.dxf"
PNG = OUT / "office_cabling_system_diagram.png"


def add_text(msp, value, point, height=2.5, align=TextEntityAlignment.LEFT):
    entity = msp.add_text(
        value,
        dxfattribs={"height": height, "layer": "文字", "style": "Standard"},
    )
    entity.set_placement(point, align=align)


def add_box(msp, x, y, w, h, value, height=2.3):
    msp.add_lwpolyline(
        [(x, y), (x + w, y), (x + w, y + h), (x, y + h)],
        close=True,
        dxfattribs={"layer": "设备"},
    )
    add_text(
        msp,
        value,
        (x + w / 2, y + h / 2),
        height,
        TextEntityAlignment.MIDDLE_CENTER,
    )


def add_line(msp, points, layer="线路", dashed=False):
    attrs = {"layer": layer, "lineweight": 35}
    if dashed:
        attrs["linetype"] = "DASHED"
    msp.add_lwpolyline(points, dxfattribs=attrs)


def add_junction(msp, x, y):
    msp.add_circle(
        (x, y),
        0.8,
        dxfattribs={"layer": "线路", "color": 1},
    )


def add_terminal(msp, x, y, label, count):
    msp.add_circle((x, y), 3.1, dxfattribs={"layer": "设备"})
    add_text(msp, label, (x, y), 2.1, TextEntityAlignment.MIDDLE_CENTER)
    add_text(msp, str(count), (x + 4.2, y), 2.2, TextEntityAlignment.MIDDLE_LEFT)


def add_fd_symbol(msp, x, y, label):
    add_box(msp, x, y, 12, 15, label, 2.5)
    add_line(msp, [(x + 2, y + 1), (x + 10, y + 14)], "设备")
    add_line(msp, [(x + 10, y + 1), (x + 2, y + 14)], "设备")


def add_floor_branch(msp, x, y, floor, fd, td, tp, switches, side="left"):
    direction = 1 if side == "left" else -1
    fd_x = x
    add_fd_symbol(msp, fd_x, y - 7.5, fd)

    terminal_x = fd_x - 18 * direction
    add_terminal(msp, terminal_x, y + 4, "TD", td)
    add_terminal(msp, terminal_x, y - 4, "TP", tp)
    add_line(msp, [(terminal_x + 3.1 * direction, y + 4), (fd_x, y + 4)])
    add_line(msp, [(terminal_x + 3.1 * direction, y - 4), (fd_x, y - 4)])

    device_x = fd_x + 16 * direction
    left = min(device_x, device_x + 14 * direction)
    add_box(msp, left, y + 1, 14, 7, f"交换机×{switches}", 1.9)
    add_box(msp, left, y - 8, 14, 7, "LIU", 2.3)
    add_line(msp, [(fd_x + (12 if direction > 0 else 0), y + 4), (left if direction > 0 else left + 14, y + 4)])
    add_line(msp, [(fd_x + (12 if direction > 0 else 0), y - 4), (left if direction > 0 else left + 14, y - 4)])

    trunk_x = fd_x + 38 * direction
    add_line(msp, [(left + (14 if direction > 0 else 0), y + 4), (trunk_x, y + 4)])
    add_line(msp, [(left + (14 if direction > 0 else 0), y - 4), (trunk_x, y - 4)])
    add_text(
        msp,
        "12芯",
        (fd_x + 54 * direction, y + 6),
        1.8,
        TextEntityAlignment.MIDDLE_CENTER,
    )
    add_text(msp, floor, (terminal_x - 9 * direction, y), 3.0, TextEntityAlignment.MIDDLE_CENTER)
    return trunk_x


def build():
    doc = ezdxf.new("R2010", setup=True)
    doc.layers.add("设备", color=250)
    doc.layers.add("线路", color=1)
    doc.layers.add("文字", color=250)
    doc.layers.add("图框", color=250)
    msp = doc.modelspace()

    # 图框及主标题
    msp.add_lwpolyline(
        [(0, 0), (320, 0), (320, 205), (0, 205)],
        close=True,
        dxfattribs={"layer": "图框", "lineweight": 50},
    )

    # 左侧楼层
    left_data = [
        (181, "四层", "4FD", 72, 72, 3),
        (146, "三层", "3FD", 48, 48, 2),
        (111, "二层北区", "2-1FD", 26, 26, 2),
        (76, "一层北区", "1-1FD", 23, 22, 1),
    ]
    left_trunks = []
    for y, floor, fd, td, tp, sw in left_data:
        left_trunks.append((y, add_floor_branch(msp, 58, y, floor, fd, td, tp, sw)))

    # 右侧楼层
    right_data = [
        (111, "二层南区", "2-2FD", 31, 31, 2),
        (76, "一层南区", "1-2FD", 29, 28, 2),
    ]
    right_trunks = []
    for y, floor, fd, td, tp, sw in right_data:
        right_trunks.append((y, add_floor_branch(msp, 258, y, floor, fd, td, tp, sw, "right")))

    # 数据、语音垂直主干分别汇聚至BD
    left_data_bus, left_voice_bus = 130, 136
    right_data_bus, right_voice_bus = 190, 184
    add_line(msp, [(left_data_bus, 64), (left_data_bus, 192)])
    add_line(msp, [(left_voice_bus, 64), (left_voice_bus, 192)])
    add_line(msp, [(right_data_bus, 64), (right_data_bus, 123)])
    add_line(msp, [(right_voice_bus, 64), (right_voice_bus, 123)])
    for y, trunk in left_trunks:
        add_line(msp, [(trunk, y + 4), (left_data_bus, y + 4)])
        add_line(msp, [(trunk, y - 4), (left_voice_bus, y - 4)])
        add_junction(msp, left_data_bus, y + 4)
        add_junction(msp, left_voice_bus, y - 4)
    for y, trunk in right_trunks:
        add_line(msp, [(trunk, y + 4), (right_data_bus, y + 4)])
        add_line(msp, [(trunk, y - 4), (right_voice_bus, y - 4)])
        add_junction(msp, right_data_bus, y + 4)
        add_junction(msp, right_voice_bus, y - 4)

    add_fd_symbol(msp, 154, 118, "BD")
    add_line(msp, [(left_data_bus, 128), (154, 128)])
    add_line(msp, [(left_voice_bus, 123), (154, 123)])
    add_line(msp, [(166, 128), (right_data_bus, 128), (right_data_bus, 123)])
    add_line(msp, [(166, 123), (right_voice_bus, 123)])
    for point in [
        (left_data_bus, 128),
        (left_voice_bus, 123),
        (154, 128),
        (154, 123),
        (166, 128),
        (166, 123),
        (right_data_bus, 123),
        (right_voice_bus, 123),
    ]:
        add_junction(msp, *point)

    # 电话及网络机房
    add_line(msp, [(145, 113), (145, 194), (267, 194), (267, 113), (145, 113)], "图框", True)
    add_text(msp, "电话及网络机房（地下一层）", (150, 190), 2.8)
    add_box(msp, 178, 160, 25, 10, "核心交换机", 2.3)
    add_box(msp, 214, 160, 27, 10, "路由器/防火墙", 2.2)
    add_box(msp, 178, 142, 25, 9, "PBX", 2.4)
    add_box(msp, 216, 178, 20, 9, "服务器", 2.4)
    add_box(msp, 246, 178, 16, 9, "工作站", 2.4)
    add_line(msp, [(160, 133), (160, 165), (178, 165)])
    add_line(msp, [(166, 121), (172, 121), (172, 146.5), (178, 146.5)])
    add_line(msp, [(203, 165), (214, 165)])
    add_line(msp, [(226, 178), (226, 170)])
    add_line(msp, [(254, 178), (254, 165), (241, 165)])
    add_junction(msp, 160, 133)
    add_junction(msp, 166, 121)

    # 进线间
    add_line(msp, [(185, 22), (185, 58), (289, 58), (289, 22), (185, 22)], "图框", True)
    add_text(msp, "进线间（地下一层）", (210, 53), 2.8)
    add_fd_symbol(msp, 251, 30, "ODF")
    add_fd_symbol(msp, 201, 30, "DDF")
    add_box(msp, 222, 34, 20, 8, "传输设备", 2.0)
    # 数据经核心交换机、路由器/防火墙、ODF进入运营商网络；
    # 语音经PBX、DDF进入运营商网络。
    add_line(msp, [(241, 165), (276, 165), (276, 37), (263, 37)])
    add_line(msp, [(203, 146.5), (207, 146.5), (207, 37)])
    add_line(msp, [(207, 37), (222, 37)])
    add_line(msp, [(242, 37), (251, 37)])
    add_line(msp, [(263, 37), (305, 37)])
    for point in [(207, 37), (263, 37), (276, 37)]:
        add_junction(msp, *point)
    add_text(msp, "至物业总配线间", (277, 41), 2.4)

    # 图纸说明
    add_text(msp, "注：", (8, 28), 2.2)
    add_text(msp, "1. 各FD至BD的数据主干采用12芯单模光缆。", (16, 28), 2.0)
    add_text(msp, "2. 语音主干采用3类25对大对数电缆。", (16, 22), 2.0)
    add_text(msp, "3. 交换机、配线架及跳线数量见设备材料表。", (16, 16), 2.0)
    add_text(msp, "4. 图中线路均为星型连接，不采用FD级联。", (16, 10), 2.0)

    # 底部图签
    msp.add_lwpolyline(
        [(176, 0), (320, 0), (320, 18), (176, 18)],
        close=True,
        dxfattribs={"layer": "图框"},
    )
    add_line(msp, [(176, 7), (320, 7)], "图框")
    add_line(msp, [(274, 0), (274, 18)], "图框")
    add_text(msp, "某办公楼综合布线系统图", (225, 12.5), 4.2, TextEntityAlignment.MIDDLE_CENTER)
    add_text(msp, "设计：张涔熙", (180, 3.5), 2.1, TextEntityAlignment.MIDDLE_LEFT)
    add_text(msp, "图号：01", (280, 12.5), 2.2, TextEntityAlignment.MIDDLE_LEFT)
    add_text(msp, "日期：2026.06", (280, 3.5), 2.2, TextEntityAlignment.MIDDLE_LEFT)
    return doc


def render(doc):
    fig, ax = plt.subplots(figsize=(16, 10.25), dpi=190)
    Frontend(RenderContext(doc), MatplotlibBackend(ax)).draw_layout(doc.modelspace())
    ax.set_xlim(-2, 322)
    ax.set_ylim(-2, 207)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    fig.savefig(PNG, bbox_inches="tight", pad_inches=0.03, facecolor="white")
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

# Office Building Structured Cabling Report

基于 LaTeX 和 Python/ezdxf 的办公楼综合布线课程设计示例，包含：

- 本科课程设计报告 LaTeX 源文件
- 信息点、FD 和水平路由的 CAD 绘制脚本
- 六类水平线缆、交换机、光缆和语音主干容量计算
- XeLaTeX 编译流程

## 环境

- TeX Live 2024 或更高版本
- Python 3.10+
- `ezdxf`
- `matplotlib`
- 可选：LibreDWG，用于 DXF/DWG 转换

```bash
python3 -m pip install -r requirements.txt
```

## 生成 CAD 图

将有权使用的建筑底图转换为 `work/cad/base.dxf`，然后执行：

```bash
python3 work/cad/draw_cabling.py
```

脚本将在 `outputs/cad/` 生成完整 DXF 和四张楼层预览图。示例坐标与信息点数量需要按实际建筑平面调整。

## 编译报告

报告源文件位于 `outputs/office_cabling_report.tex`。本地放入：

- `outputs/cover_template.pdf`
- `outputs/cad/floor1_cabling.png`
- `outputs/cad/floor2_cabling.png`
- `outputs/cad/floor3_cabling.png`
- `outputs/cad/floor4_cabling.png`

然后执行：

```bash
cd outputs
xelatex office_cabling_report.tex
xelatex office_cabling_report.tex
```

## 说明

仓库不包含原始建筑 DWG、课程模板、个人封面、最终提交 PDF 或由原图派生的 CAD 文件。使用者应确保对输入图纸拥有合法使用权，并按项目要求复核点位、路由、长度和设备容量。


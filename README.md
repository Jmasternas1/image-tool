# 图片信息读取与简单编辑工具

## 5.1 项目介绍

这是一个用 Python 编写的**命令行图片处理工具**，基于 OpenCV 实现。

- **程序做什么**：读取图片的基础信息，并对图片做几种常见的简单编辑。
- **支持哪些功能**：
  - 读取信息：文件名、格式、宽高（像素）、颜色模式（RGB / RGBA / 灰度）、文件大小（KB / MB，保留 2 位小数）
  - 缩放（可只给宽或只给高，按比例缩放）
  - 裁剪（按像素坐标 左 / 上 / 右 / 下）
  - 旋转（90° / 180° / 270°）
  - 翻转（水平 / 垂直）
  - 灰度化
  - 格式转换（如 PNG 与 JPG 互转）
- **程序是什么形式**：命令行程序（Command Line Interface，CLI）。

## 5.2 环境配置

1. **Python 版本**：需要 **Python 3.10 或以上**。
2. **依赖安装**（二选一）：
   - 使用 `uv`（推荐）：
     ```bash
     uv sync          # 按 pyproject.toml 安装依赖并生成 uv.lock
     ```
   - 使用 `pip`：
     ```bash
     python -m venv .venv
     source .venv/bin/activate        # Windows: .venv\Scripts\activate
     pip install opencv-python
     ```
3. **uv 管理**：仓库已包含 `pyproject.toml`，并在根目录提交 `uv.lock`，保证依赖版本可复现。运行 `uv run python main.py ...` 即可在隔离环境中执行。

## 5.3 运行方式

1. **启动方式**：本程序通过子命令调用，基本格式为
   ```bash
   python main.py <子命令> <图片路径> [参数]
   ```
   使用 `uv` 时把 `python` 换成 `uv run python`。

2. **每个功能的使用方法与示例**：

   - 读取信息
     ```bash
     python main.py info demo.jpg
     ```
     预期输出：
     ```
     文件名: demo.jpg
     图片格式: JPG
     宽度: 1920 像素
     高度: 1080 像素
     颜色模式: RGB
     文件大小: 352.18 KB
     ```

   - 缩放（只给宽，高度按比例）
     ```bash
     python main.py resize demo.jpg --width 800
     ```
     预期输出：`已保存到: demo_800x450.jpg`

   - 裁剪（左=10, 上=10, 右=200, 下=200）
     ```bash
     python main.py crop demo.jpg --left 10 --top 10 --right 200 --bottom 200
     ```
     预期输出：`已保存到: demo_crop.jpg`

   - 旋转 90°
     ```bash
     python main.py rotate demo.jpg --angle 90
     ```
     预期输出：`已保存到: demo_rotate90.jpg`

   - 水平翻转
     ```bash
     python main.py flip demo.jpg --mode horizontal
     ```
     预期输出：`已保存到: demo_flip_horizontal.jpg`

   - 灰度化
     ```bash
     python main.py gray demo.jpg
     ```
     预期输出：`已保存到: demo_gray.jpg`

   - 格式转换（PNG 转 JPG，透明通道会自动转 RGB）
     ```bash
     python main.py convert demo.png --format jpg
     ```
     预期输出：`已保存到: demo.jpg`

**通用说明**：
- 所有编辑结果都保存为**新文件**，不会覆盖原图，并在终端打印保存位置。
- 当文件不存在、不是有效图片、或参数非法（如宽高 ≤ 0）时，程序会打印明确的中文错误提示并以非零状态退出，不会崩溃。

"""图片信息读取与简单编辑命令行工具（课程作业）。

用法示例：
    python main.py info demo.jpg

当前状态：已实现图片基础信息读取，编辑功能待补充。
"""

import argparse
import os
import sys

import cv2


# ---------------------------------------------------------------------------
# 基础工具函数
# ---------------------------------------------------------------------------

def _load(path):
    """读取图片；统一处理 文件不存在 和 不是有效图片 两种错误。"""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"文件不存在: {path}")
    # IMREAD_UNCHANGED 会保留透明通道(Alpha)，方便后续处理 PNG
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError(f"无法读取图片，可能不是有效的图片文件: {path}")
    return img


# ---------------------------------------------------------------------------
# 3.1 读取图片信息
# ---------------------------------------------------------------------------

def read_info(path):
    """返回图片的基础信息字典：文件名、格式、宽、高、颜色模式、文件大小。"""
    img = _load(path)

    h, w = img.shape[:2]
    channels = 1 if img.ndim == 2 else img.shape[2]
    mode_map = {1: "灰度 (Grayscale)", 3: "RGB", 4: "RGBA"}
    color_mode = mode_map.get(channels, f"未知 ({channels} 通道)")

    size_bytes = os.path.getsize(path)
    if size_bytes < 1024 * 1024:
        size_str = f"{size_bytes / 1024:.2f} KB"
    else:
        size_str = f"{size_bytes / (1024 * 1024):.2f} MB"

    ext = os.path.splitext(path)[1].lstrip(".").upper() or "未知"

    return {
        "文件名": os.path.basename(path),
        "图片格式": ext,
        "宽度": f"{w} 像素",
        "高度": f"{h} 像素",
        "颜色模式": color_mode,
        "文件大小": size_str,
    }


# ---------------------------------------------------------------------------
# 命令行入口
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="图片信息读取与简单编辑工具")
    sub = parser.add_subparsers(dest="command", required=True)

    p_info = sub.add_parser("info", help="读取图片基础信息")
    p_info.add_argument("path")

    args = parser.parse_args()

    if args.command == "info":
        try:
            info = read_info(args.path)
        except (FileNotFoundError, ValueError) as e:
            print(f"[错误] {e}", file=sys.stderr)
            sys.exit(1)
        for k, v in info.items():
            print(f"{k}: {v}")


if __name__ == "__main__":
    main()

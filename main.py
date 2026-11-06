"""图片信息读取与简单编辑命令行工具（课程作业）。

计划实现的子命令：
    info     读取图片基础信息
    resize   缩放
    crop     裁剪
    rotate   旋转
    flip     翻转
    gray     灰度化
    convert  格式转换

当前状态：项目骨架，功能待实现。
"""

import argparse
import sys


def main():
    """命令行入口（骨架版：只负责解析子命令，功能尚未实现）。"""
    parser = argparse.ArgumentParser(description="图片信息读取与简单编辑工具")
    sub = parser.add_subparsers(dest="command", required=True)

    p_info = sub.add_parser("info", help="读取图片基础信息")
    p_info.add_argument("path")

    parser.parse_args()
    print("TODO: 功能尚在开发中", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()

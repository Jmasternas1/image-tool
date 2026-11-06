"""图片信息读取与简单编辑命令行工具（课程作业）。

用法示例：
    python main.py info    demo.jpg
    python main.py resize  demo.jpg --width 800
    python main.py crop    demo.jpg --left 10 --top 10 --right 200 --bottom 200
    python main.py rotate  demo.jpg --angle 90
    python main.py flip    demo.jpg --mode horizontal
    python main.py gray    demo.jpg
    python main.py convert demo.png --format jpg

所有编辑结果都保存为“新文件”，不覆盖原图，并打印保存路径。
"""

import argparse
import os
import sys

import cv2


# ---------------------------------------------------------------------------
# 基础工具函数：加载、保存、命名
# ---------------------------------------------------------------------------

def _load(path):
    """读取图片；统一处理“文件不存在”和“不是有效图片”两种错误。"""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"文件不存在: {path}")
    # IMREAD_UNCHANGED 会保留透明通道(Alpha)，方便后续处理 PNG
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError(f"无法读取图片，可能不是有效的图片文件: {path}")
    return img


def _save(img, path):
    """保存图片，并处理“带透明通道的 PNG 存成 JPG 前先转 RGB”的要求。"""
    ext = os.path.splitext(path)[1].lower()
    out = img
    if ext in (".jpg", ".jpeg") and img.ndim == 3 and img.shape[2] == 4:
        out = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    ok = cv2.imwrite(path, out)
    if not ok:
        raise IOError(f"保存失败（可能是路径无写权限）: {path}")
    return path


def _new_path(path, suffix):
    """按原文件名生成结果文件名，例如 demo.jpg -> demo_resize.jpg"""
    base, ext = os.path.splitext(path)
    return f"{base}_{suffix}{ext}"


# ---------------------------------------------------------------------------
# 3.1 读取图片信息
# ---------------------------------------------------------------------------

def read_info(path):
    """返回图片的基础信息字典：文件名、格式、宽、高、颜色模式、文件大小。"""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"文件不存在: {path}")
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError(f"无法读取图片，可能不是有效的图片文件: {path}")

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
# 3.2 简单编辑
# ---------------------------------------------------------------------------

def resize(path, width=None, height=None, output=None):
    """缩放：只给宽或只给高时按比例计算另一维。"""
    if width is None and height is None:
        raise ValueError("缩放必须指定 --width 或 --height 至少一个")
    if (width is not None and width <= 0) or (height is not None and height <= 0):
        raise ValueError("宽和高必须大于 0")

    img = _load(path)
    h, w = img.shape[:2]
    if width is None:
        width = int(round(w * height / h))
    elif height is None:
        height = int(round(h * width / w))

    result = cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)
    out = output or _new_path(path, f"{width}x{height}")
    return result, _save(result, out)


def crop(path, left, top, right, bottom, output=None):
    """裁剪：按像素坐标 (左, 上, 右, 下) 截取矩形区域。"""
    if any(v is None for v in (left, top, right, bottom)):
        raise ValueError("裁剪必须提供 --left --top --right --bottom 四个参数")
    if left < 0 or top < 0:
        raise ValueError("left / top 不能为负数")
    if right <= left or bottom <= top:
        raise ValueError("right 必须大于 left，bottom 必须大于 top")

    img = _load(path)
    h, w = img.shape[:2]
    if right > w or bottom > h:
        raise ValueError(f"裁剪区域超出图片边界（图片尺寸 {w}x{h}）")

    result = img[top:bottom, left:right]
    out = output or _new_path(path, "crop")
    return result, _save(result, out)


def rotate(path, angle, output=None):
    """旋转：仅支持 90 / 180 / 270 度。"""
    if angle not in (90, 180, 270):
        raise ValueError("旋转角度仅支持 90、180、270")
    img = _load(path)
    if angle == 90:
        result = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    elif angle == 180:
        result = cv2.rotate(img, cv2.ROTATE_180)
    else:  # 270
        result = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    out = output or _new_path(path, f"rotate{angle}")
    return result, _save(result, out)


def flip(path, mode, output=None):
    """翻转：horizontal 水平翻转，vertical 垂直翻转。"""
    if mode == "horizontal":
        code = 1          # cv2.flip 的 code：1 = 水平翻转
    elif mode == "vertical":
        code = 0          # 0 = 垂直翻转
    else:
        raise ValueError("翻转模式仅支持 horizontal 或 vertical")
    img = _load(path)
    result = cv2.flip(img, code)
    out = output or _new_path(path, f"flip_{mode}")
    return result, _save(result, out)


def grayscale(path, output=None):
    """灰度化：彩色/带透明通道图转单通道灰度图。"""
    img = _load(path)
    if img.ndim == 2:
        result = img  # 本来就是灰度
    elif img.shape[2] == 4:
        result = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
    else:
        result = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    out = output or _new_path(path, "gray")
    return result, _save(result, out)


def convert(path, fmt, output=None):
    """格式转换：根据目标扩展名重新保存（透明通道在存 JPG 时自动转 RGB）。"""
    fmt = fmt.lower().lstrip(".")
    if fmt not in ("jpg", "jpeg", "png", "bmp", "tiff"):
        raise ValueError(f"不支持的目标格式: {fmt}")
    img = _load(path)
    base = os.path.splitext(path)[0]
    ext = ".jpg" if fmt == "jpeg" else f".{fmt}"
    out = output or f"{base}.{fmt}"
    return img, _save(img, out)


# ---------------------------------------------------------------------------
# 命令行入口
# ---------------------------------------------------------------------------

def _run(func, path, **kwargs):
    """统一调用编辑函数，捕获异常并给出友好提示（不直接崩溃）。"""
    try:
        _, saved = func(path, **kwargs)
    except (FileNotFoundError, ValueError, IOError) as e:
        print(f"[错误] {e}", file=sys.stderr)
        sys.exit(1)
    print(f"已保存到: {saved}")


def main():
    parser = argparse.ArgumentParser(description="图片信息读取与简单编辑工具")
    sub = parser.add_subparsers(dest="command", required=True)

    p_info = sub.add_parser("info", help="读取图片基础信息")
    p_info.add_argument("path")

    p_resize = sub.add_parser("resize", help="缩放")
    p_resize.add_argument("path")
    p_resize.add_argument("--width", type=int)
    p_resize.add_argument("--height", type=int)
    p_resize.add_argument("--output")

    p_crop = sub.add_parser("crop", help="裁剪")
    p_crop.add_argument("path")
    p_crop.add_argument("--left", type=int, required=True)
    p_crop.add_argument("--top", type=int, required=True)
    p_crop.add_argument("--right", type=int, required=True)
    p_crop.add_argument("--bottom", type=int, required=True)
    p_crop.add_argument("--output")

    p_rotate = sub.add_parser("rotate", help="旋转 90/180/270")
    p_rotate.add_argument("path")
    p_rotate.add_argument("--angle", type=int, required=True)
    p_rotate.add_argument("--output")

    p_flip = sub.add_parser("flip", help="翻转")
    p_flip.add_argument("path")
    p_flip.add_argument("--mode", required=True, choices=["horizontal", "vertical"])
    p_flip.add_argument("--output")

    p_gray = sub.add_parser("gray", help="灰度化")
    p_gray.add_argument("path")
    p_gray.add_argument("--output")

    p_convert = sub.add_parser("convert", help="格式转换")
    p_convert.add_argument("path")
    p_convert.add_argument("--format", required=True)
    p_convert.add_argument("--output")

    args = parser.parse_args()

    if args.command == "info":
        try:
            info = read_info(args.path)
        except (FileNotFoundError, ValueError) as e:
            print(f"[错误] {e}", file=sys.stderr)
            sys.exit(1)
        for k, v in info.items():
            print(f"{k}: {v}")
        return

    if args.command == "resize":
        _run(resize, args.path, width=args.width, height=args.height, output=args.output)
    elif args.command == "crop":
        _run(crop, args.path, left=args.left, top=args.top,
             right=args.right, bottom=args.bottom, output=args.output)
    elif args.command == "rotate":
        _run(rotate, args.path, angle=args.angle, output=args.output)
    elif args.command == "flip":
        _run(flip, args.path, mode=args.mode, output=args.output)
    elif args.command == "gray":
        _run(grayscale, args.path, output=args.output)
    elif args.command == "convert":
        _run(convert, args.path, fmt=args.format, output=args.output)


if __name__ == "__main__":
    main()

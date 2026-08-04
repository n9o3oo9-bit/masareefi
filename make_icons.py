#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
يولّد أيقونات «مصاريفي» بصيغة PNG للمتاجر وللتثبيت على الأجهزة.

المخرجات في مجلد icons/:
  • icon-192.png / icon-512.png        — أيقونات عادية (شفافة الزوايا)
  • icon-maskable-512.png              — بهامش أمان ٢٠٪ لأندرويد
  • icon-1024.png                      — مطلوبة لمتجر آبل
  • apple-touch-icon.png (180)         — لسفاري على iOS

التشغيل:  python3 make_icons.py
"""

import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    sys.exit("يحتاج Pillow:  python3 -m pip install pillow")

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "icons"

GREEN = (47, 206, 101, 255)
DARK = (16, 18, 22, 255)
SS = 8  # معامل التنعيم — نرسم مكبَّرًا ثم نصغّر


def wallet(d: ImageDraw.ImageDraw, x: float, y: float, w: float, h: float, col) -> None:
    """محفظة بخطوط سميكة — نفس رسم أيقونة الواجهة."""
    lw = max(2, int(w * 0.085))
    r = w * 0.07
    body_top = y + h * 0.30
    d.rounded_rectangle([x, body_top, x + w, y + h], radius=r, outline=col, width=lw)
    # الطية العلوية
    flap = w * 0.19
    d.line([(x, body_top), (x + flap, y), (x + w - flap, y), (x + w, body_top)],
           fill=col, width=lw, joint="curve")
    # الزر
    cr = w * 0.075
    cx, cy = x + w * 0.76, body_top + (y + h - body_top) * 0.46
    d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=col)


def build(size: int, maskable: bool = False, transparent_corners: bool = True) -> Image.Image:
    S = size * SS
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    if maskable:
        # أندرويد يقصّ دائرة — نملأ الإطار كاملًا ونُبقي الرسم داخل ٦٠٪ الوسط
        d.rectangle([0, 0, S, S], fill=GREEN)
        inset, gw = S * 0.28, S * 0.44
    else:
        radius = S * 0.22 if transparent_corners else 0
        d.rounded_rectangle([0, 0, S - 1, S - 1], radius=radius, fill=GREEN)
        inset, gw = S * 0.24, S * 0.52

    wallet(d, inset, S * 0.30, gw, gw * 0.72, DARK)
    return img.resize((size, size), Image.LANCZOS)


def main() -> int:
    OUT.mkdir(exist_ok=True)
    jobs = [
        ("icon-192.png", 192, False),
        ("icon-512.png", 512, False),
        ("icon-maskable-512.png", 512, True),
        ("icon-1024.png", 1024, False),
        ("apple-touch-icon.png", 180, False),
    ]
    for name, size, mask in jobs:
        img = build(size, maskable=mask)
        if name == "apple-touch-icon.png" or name == "icon-1024.png":
            # آبل ترفض الشفافية — نسطّحها على خلفية خضراء
            bg = Image.new("RGBA", img.size, GREEN)
            bg.alpha_composite(img)
            img = bg.convert("RGB")
        img.save(OUT / name)
        print(f"  {name:26} {size}×{size}")

    print(f"\nتم توليد {len(jobs)} أيقونات في icons/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

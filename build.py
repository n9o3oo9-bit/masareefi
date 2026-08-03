#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
يبني تطبيق «مصاريفي» من القالب app.template.html إلى index.html.

ما يفعله:
  • يضمّن خط ثمانية داخل الملف (base64) — يعمل بلا إنترنت وبلا إعداد.
  • يحذف تحذير «هذا ملف المصدر».
  • يحقن إعداد Firebase من firebase.config.json إن وُجد.

التشغيل:  python3 build.py
"""

import base64
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "app.template.html"
OUT = ROOT / "index.html"
FBCFG = ROOT / "firebase.config.json"
FONTS = ROOT / "fonts" / "thmanyah typeface"

# (عائلة CSS، مجلد الخط، الوزن، اسم الملف)
FACES = [
    ("Thmanyah Sans",    "thmanyahsans",         300, "Light"),
    ("Thmanyah Sans",    "thmanyahsans",         400, "Regular"),
    ("Thmanyah Sans",    "thmanyahsans",         500, "Medium"),
    ("Thmanyah Sans",    "thmanyahsans",         700, "Bold"),
    ("Thmanyah Sans",    "thmanyahsans",         900, "Black"),
    ("Thmanyah Display", "thmanyahserifdisplay", 400, "Regular"),
    ("Thmanyah Display", "thmanyahserifdisplay", 500, "Medium"),
    ("Thmanyah Display", "thmanyahserifdisplay", 700, "Bold"),
    ("Thmanyah Display", "thmanyahserifdisplay", 900, "Black"),
]


def font_css() -> str:
    blocks = ["/* خط ثمانية — Thmanyah Typeface (مضمَّن داخل الملف) */"]
    missing = []
    for family, folder, weight, style in FACES:
        path = FONTS / folder / "woff2" / f"{folder}-{style}.woff2"
        if not path.exists():
            missing.append(str(path.relative_to(ROOT)))
            continue
        b64 = base64.b64encode(path.read_bytes()).decode("ascii")
        blocks.append(
            "@font-face{font-family:'%s';font-style:normal;font-weight:%d;font-display:block;"
            "src:url(data:font/woff2;base64,%s) format('woff2')}" % (family, weight, b64)
        )
    if missing:
        print("تحذير — ملفات خط مفقودة:", *missing, sep="\n  ", file=sys.stderr)
    if len(blocks) == 1:
        print("خطأ: لم يُضمَّن أي خط. تأكد من مجلد fonts/", file=sys.stderr)
    return "\n".join(blocks)


def firebase_snippet() -> str:
    if not FBCFG.exists():
        return "null"
    try:
        cfg = json.loads(FBCFG.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"تحذير — firebase.config.json غير صالح ({e})؛ سيُبنى بلا إعداد.", file=sys.stderr)
        return "null"
    if not cfg.get("apiKey") or not cfg.get("projectId"):
        print("تحذير — firebase.config.json ناقص apiKey أو projectId.", file=sys.stderr)
        return "null"
    print(f"أُدرج إعداد Firebase للمشروع: {cfg['projectId']}")
    return json.dumps(cfg, ensure_ascii=False)


def main() -> int:
    if not SRC.exists():
        print(f"لم يُعثر على القالب: {SRC}", file=sys.stderr)
        return 1

    html = SRC.read_text(encoding="utf-8")

    for marker in ("/*FONT_CSS*/", 'id="tplWarn"', "/*FIREBASE_CONFIG*/"):
        if marker not in html:
            print(f"القالب لا يحتوي على العلامة: {marker}", file=sys.stderr)
            return 1

    html = html.replace("/*FONT_CSS*/", font_css(), 1)

    # حذف تحذير «هذا ملف المصدر»
    html, n = re.subn(r'<div id="tplWarn">.*?</div>\s*', "", html, count=1, flags=re.S)
    if n != 1:
        print("تعذّر حذف تحذير القالب.", file=sys.stderr)
        return 1

    # حقن إعداد Firebase
    html = re.sub(r"/\*FIREBASE_CONFIG\*/.*?/\*END\*/", firebase_snippet(), html, count=1, flags=re.S)

    OUT.write_text(html, encoding="utf-8")
    print(f"تم البناء: {OUT.name}  ({OUT.stat().st_size / 1024:,.0f} كيلوبايت)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

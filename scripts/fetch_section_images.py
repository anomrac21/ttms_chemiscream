#!/usr/bin/env python3
"""Download section images (client PNG + Pexels) and update content/*/_index.md."""
from __future__ import annotations

import re
import urllib.error
import urllib.request
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
IMAGES_DIR = ROOT / "static" / "images"

PEX = "https://images.pexels.com/photos/{id}/pexels-photo-{id}.jpeg?auto=compress&cs=tinysrgb&w=900"

CLIENT_PNG: dict[str, str] = {
    "hero.webp": "ChemiscreamLunch.png",
    "lunch-menu.webp": "ChemiscreamLunch.png",
}

PEXELS: dict[str, tuple[str, str]] = {
    "promotions.webp": (PEX.format(id="2233348"), "Pexels #2233348"),
    "espresso-equations.webp": (PEX.format(id="302899"), "Pexels #302899"),
    "whole-latte-love.webp": (PEX.format(id="654642"), "Pexels #654642"),
    "signature.webp": (PEX.format(id="1640777"), "Pexels #1640777"),
    "hot-chocolate.webp": (PEX.format(id="848612"), "Pexels #848612"),
    "floral-teas.webp": (PEX.format(id="1132558"), "Pexels #1132558"),
    "smoothie-bar.webp": (PEX.format(id="376464"), "Pexels #376464"),
    "appetizers.webp": (PEX.format(id="2338407"), "Pexels #2338407"),
    "rise-and-shine.webp": (PEX.format(id="1028737"), "Pexels #1028737"),
    "engineer-your-own-formula.webp": (PEX.format(id="1109198"), "Pexels #1109198"),
    "early-bird.webp": (PEX.format(id="1640777"), "Pexels #1640777"),
    "omelettes.webp": (PEX.format(id="1095550"), "Pexels #1095550"),
    "paninis.webp": (PEX.format(id="1630757"), "Pexels #1630757"),
    "sandwiches-and-burgers.webp": (PEX.format(id="769289"), "Pexels #769289"),
    "skillets.webp": (PEX.format(id="691114"), "Pexels #691114"),
    "entrees.webp": (PEX.format(id="958545"), "Pexels #958545"),
    "pasta.webp": (PEX.format(id="2097090"), "Pexels #2097090"),
    "salads.webp": (PEX.format(id="1279330"), "Pexels #1279330"),
    "desserts.webp": (PEX.format(id="2089718"), "Pexels #2089718"),
    "kids.webp": (PEX.format(id="699953"), "Pexels #699953"),
    "mocktails-and-drinks.webp": (PEX.format(id="1267325"), "Pexels #1267325"),
    "slideshow-coffee.webp": (PEX.format(id="654642"), "Pexels #654642"),
    "slideshow-dessert.webp": (PEX.format(id="2089718"), "Pexels #2089718"),
}

SECTIONS: dict[str, str] = {
    "promotions": "promotions.webp",
    "espresso-equations": "espresso-equations.webp",
    "whole-latte-love": "whole-latte-love.webp",
    "signature": "signature.webp",
    "hot-chocolate": "hot-chocolate.webp",
    "floral-teas": "floral-teas.webp",
    "smoothie-bar": "smoothie-bar.webp",
    "appetizers": "appetizers.webp",
    "lunch-menu": "lunch-menu.webp",
    "rise-and-shine": "rise-and-shine.webp",
    "engineer-your-own-formula": "engineer-your-own-formula.webp",
    "early-bird": "early-bird.webp",
    "omelettes": "omelettes.webp",
    "paninis": "paninis.webp",
    "sandwiches-and-burgers": "sandwiches-and-burgers.webp",
    "skillets": "skillets.webp",
    "entrees": "entrees.webp",
    "pasta": "pasta.webp",
    "salads": "salads.webp",
    "desserts": "desserts.webp",
    "kids": "kids.webp",
    "mocktails-and-drinks": "mocktails-and-drinks.webp",
}


def img(name: str) -> str:
    return f"images/{name}"


def convert_png_to_webp(src: Path, dest: Path) -> bool:
    from PIL import Image

    if not src.exists():
        return dest.exists()
    Image.open(src).save(dest, "WEBP", quality=85)
    print(f"OK {dest.name} (from {src.name})")
    return True


def download_pexels(filename: str, url: str) -> bool:
    from PIL import Image

    webp = IMAGES_DIR / filename
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
    except urllib.error.HTTPError as e:
        print(f"SKIP {filename}: HTTP {e.code}")
        return webp.exists()
    Image.open(BytesIO(data)).save(webp, "WEBP", quality=85)
    print(f"OK {filename}")
    return True


def body_after_frontmatter(raw: str) -> str:
    if raw.count("---") < 2:
        return raw.strip()
    return raw.split("---", 2)[2].strip()


def update_section_index(section: str, image_file: str) -> None:
    path = CONTENT / section / "_index.md"
    if not path.exists():
        return
    raw = path.read_text(encoding="utf-8")
    title_m = re.search(r"^title:\s*(.+)$", raw, re.M)
    weight_m = re.search(r"^weight:\s*(.+)$", raw, re.M)
    title = title_m.group(1).strip().strip('"') if title_m else section.replace("-", " ").title()
    weight = weight_m.group(1).strip().strip('"') if weight_m else "1"
    body = body_after_frontmatter(raw)

    lines = [
        "---",
        f"title: {title}",
        f"weight: {weight}",
        f"icon: {img(image_file)}",
        "images:",
        f"    primary: {img(image_file)}",
        "---",
    ]
    if body:
        lines.extend(["", body])
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def update_home_index() -> None:
    path = CONTENT / "_index.md"
    body = body_after_frontmatter(path.read_text(encoding="utf-8"))
    if not body.strip():
        body = (
            "<p>Digital menu for Chemis Cream Café Ltd. "
            "Call/WhatsApp: 766-8067 · @chemiscreamcafeltd</p>"
        )
    text = (
        "---\n"
        'title: "Chemis Cream Café Ltd"\n'
        f"image: {img('hero.webp')}\n"
        "images:\n"
        f"    - image: {img('hero.webp')}\n"
        f"    - image: {img('whole-latte-love.webp')}\n"
        f"    - image: {img('desserts.webp')}\n"
        f"    - image: {img('rise-and-shine.webp')}\n"
        "slideshow:\n"
        f"    - image: {img('hero.webp')}\n"
        f"    - image: {img('slideshow-coffee.webp')}\n"
        f"    - image: {img('slideshow-dessert.webp')}\n"
        f"    - image: {img('engineer-your-own-formula.webp')}\n"
        f"    - image: {img('lunch-menu.webp')}\n"
        f"    - image: {img('promotions.webp')}\n"
        "---"
    )
    text += f"\n\n{body}\n"
    path.write_text(text, encoding="utf-8")


def main() -> None:
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    credits: list[str] = []

    for dest, src_name in CLIENT_PNG.items():
        src = IMAGES_DIR / src_name
        if convert_png_to_webp(src, IMAGES_DIR / dest):
            credits.append(f"- {dest} — Chemis Cream (client-owned, from {src_name})")

    for filename, (url, credit) in PEXELS.items():
        if download_pexels(filename, url):
            credits.append(f"- {filename} — {credit}")

    missing = [s for s, f in SECTIONS.items() if not (IMAGES_DIR / f).exists()]
    if missing:
        print("Missing:", ", ".join(missing))
        return

    for section, image_file in SECTIONS.items():
        update_section_index(section, image_file)

    if (IMAGES_DIR / "hero.webp").exists():
        update_home_index()

    (IMAGES_DIR / "IMAGE_CREDITS.txt").write_text(
        "Section photos:\n" + "\n".join(credits) + "\n",
        encoding="utf-8",
    )
    print("Section headers updated.")


if __name__ == "__main__":
    main()

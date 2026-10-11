#!/usr/bin/env python3
"""captures.py - mesure, en lecture seule, les deux critères de capture du contrôle M3 (tools/gate.py).

Pour chaque PNG donné : couleur dominante (une couleur exacte, en % des pixels) et part des pixels sous
luminance 0,05. Les seuils du contrôle sont 40 % et 35 %. Le contrôle reste la référence ; ce script ne fait
que montrer les chiffres avant et après un changement visuel.
Usage : python3 tools/mesure/captures.py <png> [<png> ...]
"""
import sys
from collections import Counter

from PIL import Image


def lin(c):
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(rgb):
    r, g, b = rgb
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def mesurer(chemin):
    img = Image.open(chemin).convert("RGB")
    pixels = list(img.getdata())
    n = len(pixels)
    compte = Counter(pixels)
    dom = max(compte.values()) / n
    sombre = sum(1 for p in pixels if luminance(p) < 0.05) / n
    return dom, sombre


if __name__ == "__main__":
    for chemin in sys.argv[1:]:
        dom, sombre = mesurer(chemin)
        print(f"{chemin} : dominante {dom * 100:.0f} % (<40) ; sous luminance 0,05 : {sombre * 100:.0f} % (<35)")

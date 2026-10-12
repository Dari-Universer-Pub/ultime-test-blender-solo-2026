#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
feuille.py - feuille d'animation (images d'un lot, côte à côte) avec tags et durées.

    python3 tools/planches/feuille.py FICHE.json SORTIE.png TAG

Lit la fiche (images, durées) et les PNG de sortie de l'assembleur (sortie/<NN_nom>.png). Assemble une
feuille horizontale (112 px par image, sans rotation ni échelle) et écrit feuille.json : tag, plage d'images,
durée de chaque image en unités de fiche (duree_images). Outil d'ASSEMBLAGE : ne dessine aucun asset.
"""
import argparse
import json
from pathlib import Path

from PIL import Image

CANEVAS = 112


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fiche")
    ap.add_argument("sortie_png")
    ap.add_argument("tag")
    a = ap.parse_args()
    fiche = json.loads(Path(a.fiche).read_text(encoding="utf-8"))
    sortie = Path(a.fiche).parent / "sortie"
    images = fiche["images"]
    feuille = Image.new("RGBA", (CANEVAS * len(images), CANEVAS), (0, 0, 0, 0))
    frames = []
    for i, f in enumerate(images):
        nom = "%02d_%s" % (f["n"], f["nom"])
        src = sortie / (nom + ".png")
        im = Image.open(src).convert("RGBA")
        if im.size != (CANEVAS, CANEVAS):
            raise SystemExit("taille inattendue : %s %s" % (src, im.size))
        feuille.paste(im, (i * CANEVAS, 0))
        frames.append({"index": i, "nom": nom, "duree_images": f["duree_images"]})
    Path(a.sortie_png).parent.mkdir(parents=True, exist_ok=True)
    feuille.save(a.sortie_png)
    tags = {a.tag: {"debut": 0, "fin": len(images) - 1, "boucle": True}}
    meta = {"tag": a.tag, "canevas": [CANEVAS, CANEVAS], "images": frames, "tags": tags,
            "total_duree_images": sum(f["duree_images"] for f in images)}
    Path(a.sortie_png).with_suffix(".json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(meta, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()

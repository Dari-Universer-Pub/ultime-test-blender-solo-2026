#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pieces.py - remontage de l'ancre à partir de ses pièces plates (creusage, étape 1 de la méthode 2D).

    python3 tools/planches/pieces.py DOSSIER_PIECES ANCRE_VALIDEE.png SORTIE_DOSSIER

DOSSIER_PIECES : écrit par plongeur_v6 (PLONGEUR_PIECES=...) : ancre_rendu.png, pieces/<nom>.png, pieces/manifeste.json.
Remontage : empilement dans l'ordre du manifeste (du fond vers l'avant), pixel par pixel, sans rotation ni
redimensionnement. Comparaison : (a) avec le rendu complet de la même chaîne ; (b) avec l'ancre validée,
après le même nettoyage des pixels isolés que l'ancre (tools/pixelisation/nettoyage.py).
Sorties : remontage.png, comparaison.png (diagramme des pixels qui diffèrent), planche_pieces.png, rapport.json.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "pixelisation"))
import nettoyage  # noqa: E402


def charger(p):
    return np.array(Image.open(p).convert("RGBA"))


def remonter(dossier, manifeste):
    """Assemble les pièces pixel par pixel : sur chaque pixel, la pièce la plus proche de la caméra
    (carte de profondeur) l'emporte ; à profondeur égale, l'ordre du manifeste. Sans rotation ni échelle."""
    base = np.zeros((112, 112, 4), dtype=np.uint8)
    prof_best = np.full((112, 112), 999.0)
    for nom in manifeste["ordre"]:
        pix = charger(dossier / "pieces" / (nom + ".png"))
        prof = charger(dossier / "profondeur" / (nom + ".png"))[..., 0].astype(float)
        m = (pix[..., 3] > 0) & (prof <= prof_best)
        base[m] = pix[m]
        prof_best[m] = prof[m]
    return base


def egalite(a, b):
    """Pourcentage de pixels identiques (RGBA), pixels transparents comparés sur l'alpha seul."""
    a_alpha = a[..., 3] > 0
    b_alpha = b[..., 3] > 0
    opaque = a_alpha & b_alpha
    ident = np.all(a[..., :3] == b[..., :3], axis=2) & opaque
    transp = ~a_alpha & ~b_alpha
    return round(100.0 * float(np.sum(ident | transp)) / a.shape[0] / a.shape[1], 3), int(np.sum(a_alpha != b_alpha))


def diagramme(a, b, chemin, echelle=4):
    """Pixels qui diffèrent : rouge = différence de couleur, jaune = présent d'un seul côté."""
    h, w = a.shape[:2]
    img = np.zeros((h, w, 3), dtype=np.uint8)
    img[...] = (40, 40, 40)
    a_alpha = a[..., 3] > 0
    b_alpha = b[..., 3] > 0
    img[a_alpha & b_alpha] = (90, 90, 90)
    img[a_alpha & b_alpha & np.any(a[..., :3] != b[..., :3], axis=2)] = (255, 40, 40)
    img[a_alpha != b_alpha] = (255, 220, 40)
    Image.fromarray(img).resize((w * echelle, h * echelle), Image.NEAREST).save(chemin)


def planche_pieces(dossier, sortie, echelle=3):
    """Toutes les pièces, rendues seules, à 112 px (ici ×3), fond sombre pour voir l'alpha."""
    noms = []
    man = json.loads((dossier / "pieces" / "manifeste.json").read_text(encoding="utf-8"))
    noms = list(man["ordre"])
    pioche = dossier / "pieces" / "pioche.json"
    if pioche.exists():
        noms += list(json.loads(pioche.read_text(encoding="utf-8"))["pieces"].keys())
    cote = 112 * echelle
    cols = 5
    rangees = (len(noms) + cols - 1) // cols
    img = Image.new("RGB", (cols * (cote + 12) + 12, rangees * (cote + 30) + 12), (28, 28, 28))
    d = ImageDraw.Draw(img)
    for i, nom in enumerate(noms):
        r, c = divmod(i, cols)
        x, y = 12 + c * (cote + 12), 12 + r * (cote + 30)
        piece = Image.open(dossier / "pieces" / (nom + ".png")).convert("RGBA").resize((cote, cote), Image.NEAREST)
        img.paste(piece, (x, y + 18), piece)
        d.text((x + 2, y + 2), nom, fill=(255, 220, 120))
    img.save(sortie)


def planche_remontage(sortie, remontage, ancre, nettoye, rapport, echelle=4):
    """Ancre validée, remontage (même chaîne : pièces, profondeur, nettoyage) et diagramme des différences."""
    cote = 112 * echelle
    img = Image.new("RGB", (3 * (cote + 12) + 12, cote + 60), (28, 28, 28))
    d = ImageDraw.Draw(img)
    colonnes = [("ancre validee", ancre), ("remontage des pieces", remontage)]
    for i, (titre, arr) in enumerate(colonnes):
        x = 12 + i * (cote + 12)
        im = Image.fromarray(arr).resize((cote, cote), Image.NEAREST)
        fond = Image.new("RGBA", (cote, cote), (30, 120, 150, 255))
        fond.alpha_composite(im)
        img.paste(fond.convert("RGB"), (x, 36))
        d.text((x + 2, 16), titre, fill=(255, 220, 120))
    diff = Image.open(sortie.parent / "comparaison_ancre.png").convert("RGB").resize((cote, cote), Image.NEAREST)
    img.paste(diff, (12 + 2 * (cote + 12), 36))
    d.text((12 + 2 * (cote + 12) + 2, 16), "pixels qui different (rouge = couleur, jaune = alpha)", fill=(255, 220, 120))
    d.text((12, cote + 44), "remontage vs ancre validee : %.3f %% identiques (alpha : %d px differents)" % (
        rapport["remontage_nettoye_vs_ancre_validee_pct"], rapport["pixels_alpha_differents_nettoye_vs_ancre"]),
        fill=(235, 235, 235))
    img.save(sortie)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pieces")
    ap.add_argument("ancre")
    ap.add_argument("sortie")
    args = ap.parse_args()
    dossier = Path(args.pieces)
    sortie = Path(args.sortie)
    sortie.mkdir(parents=True, exist_ok=True)
    manifeste = json.loads((dossier / "pieces" / "manifeste.json").read_text(encoding="utf-8"))

    remontage = remonter(dossier, manifeste)
    rendu = charger(dossier / "ancre_rendu.png")
    ancre = charger(args.ancre)
    # nettoyage : même traitement que l'ancre (pixels isolés), appliqué au remontage
    nettoye = nettoyage.nettoyer(remontage)

    pct_rendu, diff_rendu = egalite(remontage, rendu)
    pct_ancre_brut, diff_brut = egalite(remontage, ancre)
    pct_ancre, diff_ancre = egalite(nettoye, ancre)
    Image.fromarray(remontage).save(sortie / "remontage.png")
    diagramme(remontage, rendu, sortie / "comparaison_rendu.png")
    diagramme(nettoye, ancre, sortie / "comparaison_ancre.png")

    rapport = {
        "pixels_identiques_remontage_vs_rendu_complet_pct": pct_rendu,
        "pixels_alpha_differents_vs_rendu": diff_rendu,
        "pixels_identiques_remontage_vs_ancre_validee_pct": pct_ancre_brut,
        "pixels_alpha_differents_vs_ancre": diff_brut,
        "remontage_nettoye_vs_ancre_validee_pct": pct_ancre,
        "pixels_alpha_differents_nettoye_vs_ancre": diff_ancre,
        "ordre": manifeste["ordre"],
    }
    (sortie / "rapport.json").write_text(json.dumps(rapport, ensure_ascii=False, indent=1), encoding="utf-8")
    planche_pieces(dossier, sortie / "planche_pieces.png")
    planche_remontage(sortie / "planche_remontage.png", nettoye, ancre, nettoye, rapport)
    print(json.dumps(rapport, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()

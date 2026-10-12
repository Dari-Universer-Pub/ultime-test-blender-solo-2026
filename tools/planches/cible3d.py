#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cible3d.py - planche cible 3D du creusage, image par image, sous la planche d'intention (RÈGLE ANIMATION, B et E).

    python3 tools/planches/cible3d.py RENDU_448 DOSSIER_IDENT PLANCHE_INTENTION.png TEXTES.json SORTIE.png

RENDU_448     : dossier écrit par plongeur_v6 (PLONGEUR_CREUSAGE=fiche) : creusage_01..06.png et controles_3d.json.
DOSSIER_IDENT : dossier écrit par plongeur_v6 (PLONGEUR_CREUSAGE=identite) : image_01..06, mesuré par
                tools/mesure/membres_nage.py (bras proche = droit, seuil 45 % ; lointain = gauche, seuil 40 %).
TEXTES.json   : pour chaque image, « conforme » et « ecart » écrits d'après la planche.
Sortie : SORTIE.png (intention à gauche de chaque cible, six images), SORTIE.md (tableau des contrôles
et liste conforme / écart). Les mesures de hauteur viennent de la bbox alpha du rendu (448 px = 112 px x 4).
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
MEMBRES = HERE.parent / "mesure" / "membres_nage.py"
HAUTEUR_MAX = 72.0
TETE_MIN = 12.0
MANCHE_MIN = 3.0
ETIRE_MAX = 25.0
PROCHE_MIN, LOINTAIN_MIN = 45.0, 40.0
ECART_MIN = 40.0
PENETRATION_GANTS_MAX = 0.5    # mm : gants et pioche, zéro (0,5 mm = tolérance numérique)
PENETRATION_HAUT_BRAS_MAX = 5.0  # mm : haut du bras et épaule, quelques millimètres
PENETRATION_AVANT_BRAS_MAX = 0.5  # mm : avant-bras, zéro
TRANSLIT = str.maketrans({"é": "e", "è": "e", "ê": "e", "à": "a", "â": "a", "ç": "c", "ù": "u", "ô": "o",
                          "î": "i", "É": "E", "È": "E", "’": "'", "°": " deg", "→": "->", "≥": ">=", "≤": "<=",
                          "φ": "phi", "–": "-", "—": "-", "×": "x"})


def cter_2d_depuis_txt(chemin):
    """Distances 2D (px) de C ter (a), une ligne par image, lues dans planche_intention.txt."""
    motif = re.compile(r"main-casque (-?[\d.]+) px ; manche-casque (-?[\d.]+) px ; manche-torse (-?[\d.]+) px ; "
                       r"manche-jambes (-?[\d.]+) px")
    return [tuple(float(x) for x in m.groups()) for m in map(motif.search, Path(chemin).read_text(encoding="utf-8").splitlines())
            if m]


def mesure_bras(dossier_k):
    """Pourcentage visible des bras proche (d) et lointain (g), par tools/mesure/membres_nage.py."""
    sortie = subprocess.run([sys.executable, str(MEMBRES), str(dossier_k), "--proche", "d"],
                            capture_output=True, text=True).stdout
    p = re.search(r"bras_proche (\d+) px / (\d+) %", sortie)
    l = re.search(r"bras_lointain (\d+) px / (\d+) %", sortie)
    return (int(p.group(2)), int(l.group(2))) if p and l else (None, None)


def hauteur_px(chemin):
    """Hauteur du plongeur (tête, outil compris) en px du sprite 112 : bbox alpha du rendu 448 divisée par 4."""
    img = Image.open(chemin).convert("RGBA")
    haut, bas = img.getchannel("A").getbbox()[1], img.getchannel("A").getbbox()[3]
    return (bas - haut) / 4.0, haut / 4.0, bas / 4.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rendu")
    ap.add_argument("ident")
    ap.add_argument("intention")
    ap.add_argument("textes")
    ap.add_argument("sortie")
    args = ap.parse_args()
    rendu, ident = Path(args.rendu), Path(args.ident)
    controles = json.loads((rendu / "controles_3d.json").read_text(encoding="utf-8"))
    textes = json.loads(Path(args.textes).read_text(encoding="utf-8"))
    intention = Image.open(args.intention).convert("RGBA")
    cter = cter_2d_depuis_txt(Path(args.intention).with_suffix(".txt"))
    marge, case = 12, 448

    lignes_md = []
    rendus = []
    for k, c in enumerate(controles):
        n = c["image"]
        img = Image.open(rendu / ("creusage_%02d.png" % n)).convert("RGBA")
        rendus.append(img)
        h, haut, bas = hauteur_px(rendu / ("creusage_%02d.png" % n))
        proche, lointain = mesure_bras(ident / ("image_%02d" % n))
        etir = c["etirement_pct"]
        ecart = textes["frames"][k]["ecart_angle"]
        col = c.get("collisions", {})
        gants = max(v["max_mm"] for k, v in col.items() if k.startswith("main_"))
        pioche = max(v["max_mm"] for k, v in col.items() if k.startswith("pioche_"))
        haut = max(v["max_mm"] for k, v in col.items() if k.startswith("haut_bras_"))
        avant = max(v["max_mm"] for k, v in col.items() if k.startswith("avant_bras_"))
        verdicts = {
            "etirement": max(etir.values()) <= ETIRE_MAX + 0.05,
            "hauteur": h <= HAUTEUR_MAX + 0.05,
            "tete": c["tete_acier_px"] >= TETE_MIN,
            "manche": c["manche_epaisseur_px"] >= MANCHE_MIN,
            "bras": proche is not None and proche >= PROCHE_MIN and lointain >= LOINTAIN_MIN,
            "mains": max(c["main_sur_manche_m"].values()) < 1e-4,
            "angle": ecart is None or ecart >= ECART_MIN,
            "gants_pioche": max(gants, pioche) <= PENETRATION_GANTS_MAX,
            "haut_bras": haut <= PENETRATION_HAUT_BRAS_MAX,
            "avant_bras": avant <= PENETRATION_AVANT_BRAS_MAX,
        }
        echec = [nom for nom, ok in verdicts.items() if not ok]
        lignes_md.append({
            "n": n, "nom": c["nom"], "phi": c["phi_deg"],
            "etir": etir, "hauteur": round(h, 1), "tete": c["tete_acier_px"], "manche": c["manche_px"],
            "epaisseur": c["manche_epaisseur_px"], "proche": proche, "lointain": lointain,
            "ecart_angle": ecart, "echec": echec, "verdicts": verdicts,
            "conforme": textes["frames"][k]["conforme"], "ecart_txt": textes["frames"][k]["ecart"],
            "haut_px": round(haut, 1), "bas_px": round(bas, 1),
            "gants_mm": gants, "pioche_mm": pioche, "haut_bras_mm": haut, "avant_bras_mm": avant,
            "cter": cter[k] if k < len(cter) else None,
        })

    # ---- planche : intention au-dessus de la cible 3D, trois images par ligne
    colonnes = 3
    lignes_planche = []
    for k, L in enumerate(lignes_md):
        lignes_planche.append(textwrap.wrap("%d %s : %s" % (L["n"], L["nom"], "CONFORME" if not L["echec"] else
                                                           "ECART ( " + ", ".join(L["echec"]) + " )"), 210) or [""])
    textes_bloc = []
    for L in lignes_md:
        textes_bloc.append("%d. %s : conforme : %s" % (L["n"], L["nom"], L["conforme"]))
        textes_bloc.append("   ECART : %s" % L["ecart_txt"])
    textes_bloc.append("")
    textes_bloc.append("Controles (regle C, image par image) : etirement des bras <= 25 % ; hauteur <= 72 px ; "
                       "tete d'acier >= 12 px ; manche >= 3 px ; bras proche >= 45 %, lointain >= 40 % ; "
                       "mains sur le manche (0 m) ; ecart d'angle >= 40 deg. Pixels isoles, hash, contour : au pixel art.")
    for L in lignes_md:
        textes_bloc.append("%d %s : phi %+d ; etirement G %+.0f %% D %+.0f %% ; hauteur %.1f px ; tete %.1f px ; "
                           "manche %.0f px, %.1f px d'epaisseur ; bras proche %s %% lointain %s %% ; ecart %s ; %s" % (
                               L["n"], L["nom"], L["phi"], L["etir"]["g"], L["etir"]["d"], L["hauteur"], L["tete"],
                               L["manche"], L["epaisseur"], L["proche"], L["lointain"],
                               "-" if L["ecart_angle"] is None else "%.0f deg" % L["ecart_angle"],
                               "OK" if not L["echec"] else "ECART " + ", ".join(L["echec"])))
    lignes_wrap = []
    for t in textes_bloc:
        lignes_wrap.extend(textwrap.wrap(t.translate(TRANSLIT), 210) or [""])

    lignes_rangee = (len(lignes_md) + colonnes - 1) // colonnes
    lignes_b = [("intention", "cible 3D")]
    haut_bande = 14
    rangees = lignes_rangee * 2
    W = colonnes * case + (colonnes + 1) * marge
    H = rangees * (case + haut_bande + marge) + marge + 24 + 15 * len(lignes_wrap) + marge
    planche = Image.new("RGBA", (W, H), (28, 28, 28, 255))
    d = ImageDraw.Draw(planche)
    for k, L in enumerate(lignes_md):
        grp, c = divmod(k, colonnes)
        for ligne, (source, legende) in enumerate(((intention_panel(intention, k), "intention"),
                                                   (rendus[k], "cible 3D haute qualite"))):
            r = grp * 2 + ligne
            x = marge + c * (case + marge)
            y = marge + r * (case + haut_bande + marge)
            d.rectangle([x, y, x + case, y + haut_bande], fill=(60, 60, 60, 255))
            d.text((x + 4, y + 2), "%d %s - %s" % (L["n"], L["nom"], legende), fill=(255, 220, 120, 255))
            planche.alpha_composite(source, (x, y + haut_bande))
    y0 = marge + rangees * (case + haut_bande + marge)
    for i, t in enumerate(lignes_wrap):
        d.text((marge, y0 + 24 + 15 * i), t, fill=(235, 235, 235, 255))
    d.text((marge, y0), "Planche cible 3D (creusage, fiche Stardew) : sous chaque image d'intention, le rendu 3D "
           "(448 px, meme camera, meme lumiere)".translate(TRANSLIT), fill=(255, 220, 120, 255))
    sortie = Path(args.sortie)
    planche.convert("RGB").save(sortie)

    # ---- tableau et texte en markdown, à côté de la planche
    md = ["# Cible 3D haute qualité : creusage (fiche), contrôle C ter", "",
          "Pénétration 3D : maximum en mm, contre les enveloppes convexes du corps (majorant). Gants et pioche : 0 mm. "
          "Haut du bras : 5 mm au plus. Avant-bras : 0 mm. Distances 2D (px) : main-casque et manche-casque, "
          "négatif = dedans (manche derrière le casque, déclaré pour l'image 1).", "",
          "| image | nom | phi (deg) | étirement G / D (%) | hauteur (px, max 72) | tête (px, min 12) | manche (px) "
          "| bras proche / lointain (%) | gants+pioche (mm) | haut du bras (mm, max 5) | avant-bras (mm, max 0) "
          "| 2D main-casque / manche-casque (px) | écart d'angle précédent | verdict |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for L in lignes_md:
        cter_txt = "-" if L["cter"] is None else "%.1f / %.1f" % (L["cter"][0], L["cter"][1])
        md.append("| %d | %s | %+d | %+.1f / %+.1f | %.1f | %.1f | %.0f | %s / %s | %.2f | %.2f | %.2f | %s | %s | %s |" % (
            L["n"], L["nom"], L["phi"], L["etir"]["g"], L["etir"]["d"], L["hauteur"], L["tete"], L["manche"],
            L["proche"], L["lointain"], L["gants_mm"], L["haut_bras_mm"], L["avant_bras_mm"], cter_txt,
            "-" if L["ecart_angle"] is None else "%.0f" % L["ecart_angle"],
            "OK" if not L["echec"] else "ÉCART : " + ", ".join(L["echec"])))
    md += ["", "## Conforme / écart, image par image", ""]
    for L in lignes_md:
        md.append("- **%d. %s** — conforme : %s" % (L["n"], L["nom"], L["conforme"]))
        md.append("  - écart : %s" % L["ecart_txt"])
    md += ["", "Contrôles qui restent au pixel art : pixels isolés, images distinctes (hash), contour (aucun)."]
    sortie.with_suffix(".md").write_text("\n".join(md) + "\n", encoding="utf-8")
    sortie.with_suffix(".json").write_text(json.dumps(lignes_md, ensure_ascii=False, indent=1), encoding="utf-8")
    print("planche :", sortie)
    print("image_sha256 :", hashlib.sha256(sortie.read_bytes()).hexdigest())
    for L in lignes_md:
        print(L["n"], L["nom"], "hauteur", L["hauteur"], "tete", L["tete"], "bras", L["proche"], L["lointain"],
              "etir", L["etir"], "echec", L["echec"])


def intention_panel(intention, k, marge=12, case=448):
    """Panneau k de la planche d'intention (trois par ligne, 448 px chacun)."""
    r, c = divmod(k, 3)
    x = marge + c * (case + marge)
    y = marge + r * (case + marge)
    return intention.crop((x, y, x + case, y + case))


if __name__ == "__main__":
    main()

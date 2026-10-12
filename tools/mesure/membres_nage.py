#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
membres_nage.py - visibilité des quatre membres en NAGE, image par image (carte d'identité).

    python3 tools/mesure/membres_nage.py DOSSIER_IMAGE --proche g|d [--facteur 1]

DOSSIER_IMAGE est un dossier produit par plongeur_v6.rendre_identite (identite/idle_01.png, parties/<groupe>/).
Repères (demande de Julien, pas des règles du gate) : membres PROCHES >= 30 px visibles et >= 45 % non cachés ;
membres LOINTAINS >= 30 px visibles et >= 40 % non cachés. Sortie : une ligne, code 0 si tout passe.
Réutilise les fonctions de membres.py (étiquettes majoritaires, surface seule).
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import membres as m  # noqa: E402


def couleur_de(palette, groupe):
    hexa = palette[groupe][0].lstrip("#")
    return tuple(int(hexa[k:k + 2], 16) for k in (0, 2, 4))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dossier")
    ap.add_argument("--proche", choices=["g", "d"], required=True)
    ap.add_argument("--facteur", type=int, default=1)
    ap.add_argument("--seuil-proche", type=float, default=0.45, help="repère : membres proches (défaut 45 %)")
    ap.add_argument("--seuil-lointain", type=float, default=0.40, help="repère : membres lointains (défaut 40 %)")
    args = ap.parse_args()
    palette = json.load(open(os.path.join(args.dossier, "identite_palette.json"), encoding="utf-8"))["rampes"]
    groupes = m.membres_pour(args.proche)
    couleurs = {g: couleur_de(palette, g) for g in {x for v in groupes.values() for x in v}}
    etiq, noms = m.etiquettes(os.path.join(args.dossier, "identite", "idle_01.png"), couleurs, args.facteur)
    ligne = []
    ok = True
    for nom, parties in groupes.items():
        proche = nom.endswith("proche")
        visible = int(sum((etiq == noms.index(g)).sum() for g in parties))
        surface = 0
        for g in parties:
            surface += int(m.surface_seule(os.path.join(args.dossier, "parties", g, "idle_01.png"), args.facteur).sum())
        non_cache = visible / surface if surface else 0.0
        seuil = args.seuil_proche if proche else args.seuil_lointain
        bon = visible >= 30 and non_cache >= seuil
        ok = ok and bon
        ligne.append("%s %d px / %d %% (seuil %d %%)%s" % (nom, visible, round(100 * non_cache),
                                                          round(100 * seuil), "" if bon else " KO"))
    print(" ; ".join(ligne))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

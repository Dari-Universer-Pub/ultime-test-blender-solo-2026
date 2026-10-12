#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""essai.py - essai rapide d'une pose : assemble, puis imprime les mesures utiles au réglage à l'œil.

    python3 tools/mesure/animation/essai.py POSE.json [--png SORTIE.png]

Mesures : étendue verticale de l'outil (haut / bas), chevauchement visible pioche-casque, pixels du hublot touchés,
bras sur le casque, hauteur. Ne modifie rien ; sert à régler la pose par essais.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "planches" / "animation"))
import assembleur  # noqa: E402


def mesure(pose_path, png=None):
    pose = json.loads(Path(pose_path).read_text(encoding="utf-8"))
    out, qui, utilisees, couches = assembleur.composer_pose(pose, Path("/tmp/essai_asm"))
    ordre = pose["calques"]
    masques = {nom: (img[..., 3] > 0) for nom, img in couches}
    bloc = masques.get("bloc_main_d", np.zeros(out.shape[:2], bool))
    casque = masques.get("casque", np.zeros(out.shape[:2], bool))
    ys = np.nonzero(out[..., 3] > 0)[0]
    res = {"hauteur": int(ys.max() - ys.min() + 1) if len(ys) else 0,
           "haut_y": int(ys.min()) if len(ys) else None, "bas_y": int(ys.max()) if len(ys) else None,
           "bloc_bas_y": int(np.nonzero(bloc)[0].max()) if bloc.any() else None,
           "bloc_haut_y": int(np.nonzero(bloc)[0].min()) if bloc.any() else None,
           "pioche_sur_casque_px": int(np.sum(bloc & casque & (qui == "bloc_main_d")))}
    if png:
        Image.fromarray(out).resize((448, 448), Image.NEAREST).save(png)
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("pose")
    ap.add_argument("--png")
    a = ap.parse_args()
    print(json.dumps(mesure(a.pose, a.png)))

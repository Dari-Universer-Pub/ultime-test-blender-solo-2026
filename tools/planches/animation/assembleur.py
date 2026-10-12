#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
assembleur.py - assemble une image d'animation à partir d'un fichier de pose (creusage, étape 3).

    python3 tools/planches/animation/assembleur.py POSE.json SORTIE_DOSSIER

Le fichier de pose donne, pour une image :
  - les angles des articulations (bras droit et gauche : haut et avant-bras ; bloc main + pioche) dans le plan
    de l'écran, en degrés (voir bibliotheque.json : +90 = vers la droite pour les bras, horaire pour le bloc) ;
  - les décalages entiers du buste (torse, ceinture, jambes restent au repos) et de la tête (casque) ;
  - l'ORDRE D'AFFICHAGE EXPLICITE : la liste « calques » de bas en haut. Aucune profondeur par pixel.

Aucune rotation de pixels : chaque variante est une image rendue par Blender autour de son pivot ; l'assembleur
ne fait que des translations entières, calculées depuis les pivots (chaîne épaule -> coude -> poignet -> gant).

Sorties : image.png (112 x 112), controles.json (chevauchements, pixels isolés, hauteur, pièces utilisées).
"""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
RACINE = HERE.parent.parent.parent
sys.path.insert(0, str(RACINE / "tools" / "pixelisation"))
import nettoyage  # noqa: E402

CREUSAGE = RACINE / "art" / "pixel" / "plongeur_v6" / "creusage"
BIBLIO = CREUSAGE / "bibliotheque"
PIECES = CREUSAGE / "decoupe_ancre" / "pieces"
CANEVAS = 112


def charger(p):
    return np.array(Image.open(p).convert("RGBA"))


def angle_cle(a):
    """Nom de fichier d'une variante : +090, -060 (format %+04d)."""
    return "%+04d.png" % int(a)


def tourner_px(v, deg):
    """Rotation anti-horaire pour le spectateur, en coordonnées écran (y vers le bas), de deg degrés."""
    t = math.radians(deg)
    dx, dy = v
    return (dx * math.cos(t) + dy * math.sin(t), -dx * math.sin(t) + dy * math.cos(t))


def translater(img, dx, dy):
    """Translation entière (pixels décalés, aucune rotation ni échelle)."""
    dx, dy = int(dx), int(dy)
    out = np.zeros_like(img)
    h, w = img.shape[:2]
    xs0, xs1 = max(0, -dx), min(w, w - dx)
    ys0, ys1 = max(0, -dy), min(h, h - dy)
    if xs1 > xs0 and ys1 > ys0:
        out[ys0 + dy:ys1 + dy, xs0 + dx:xs1 + dx] = img[ys0:ys1, xs0:xs1]
    return out


def chaine_bras(cote, lib, theta_haut, theta_avant, decal=(0, 0)):
    """Pièces d'un bras et translations entières. Le haut du bras tourne autour de l'épaule (décalée de `decal`
    quand le torse se penche : option epaules_suivent_buste) ; l'avant-bras (sans gant) et le capuchon du coude
    sont tournés autour du coude de repos puis translatés au coude nouveau."""
    S0 = np.array(lib["pieces"]["bras_%s_haut" % cote]["pivot_px"])
    E = np.array(lib["capuchons"]["coude_%s" % cote]["centre_px"])
    S = S0 + np.array(decal, dtype=float)
    E_new = S + np.array(tourner_px(E - S0, theta_haut))
    t_e = (int(round(E_new[0] - E[0])), int(round(E_new[1] - E[1])))
    return S, E, E_new, t_e


def composer_pose(pose, sortie_dir):
    lib = json.loads((BIBLIO / "bibliotheque.json").read_text(encoding="utf-8"))
    blocs = json.loads((BIBLIO / "blocs_main.json").read_text(encoding="utf-8"))
    ch = pose["chaine"]
    couches = []        # (nom, image, masque de la pièce)
    utilisees = {}
    buste = ch.get("buste", [0, 0])
    tete = ch.get("casque", [0, 0])
    # épaules : suivent le torse si la pose le demande (attaque : le corps se penche, les bras suivent)
    decal = tuple(buste) if pose.get("epaules_suivent_buste") else (0, 0)
    jambes_dec = tuple(ch.get("jambes", [0, 0]))   # saut : décalage vertical du corps entier (jambes rigides)
    bloc_dir = BIBLIO / "variantes" / pose.get("bloc_dossier", "bloc_main_d")

    def ajouter(nom, img):
        couches.append((nom, img))
        utilisees[nom] = int(np.sum(img[..., 3] > 0))

    dessin = {
        "torse": lambda: translater(charger(PIECES / "torse.png"), buste[0], buste[1]),
        "jambes": lambda: translater(charger(PIECES / "jambes.png"), jambes_dec[0], jambes_dec[1]),
        "casque": lambda: translater(charger(PIECES / "casque.png"), tete[0], tete[1]),
    }
    # bras et bloc main : tournés puis translatés (chaîne)
    for cote in ("g", "d"):
        a = ch["bras_%s" % cote]
        S, E, E_new, t_e = chaine_bras(cote, lib, a["haut"], a["avant"], decal)
        wrist = np.array(blocs["pivots_px"]["poignet"]) if cote == "d" else None
        dessin["bras_%s_haut" % cote] = (lambda cote=cote, th=a["haut"]:
                                         translater(charger(BIBLIO / "variantes" / ("bras_%s_haut" % cote) / angle_cle(th)),
                                                    decal[0], decal[1]))
        if cote == "g":
            dessin["bras_g_avant"] = (lambda th=a["avant"], t_e=t_e, E=E:
                                      translater(charger(BIBLIO / "variantes" / "bras_g_avant" / angle_cle(th)),
                                                 t_e[0], t_e[1]))
            dessin["cap_coude_g"] = (lambda t_e=t_e: translater(charger(BIBLIO / "capuchons" / "coude_g.png"),
                                                                t_e[0], t_e[1]))
        else:
            dessin["bras_d_avant"] = (lambda th=a["avant"], t_e=t_e:
                                      translater(charger(BIBLIO / "variantes" / "bras_d_avant_nu" / angle_cle(th)),
                                                 t_e[0], t_e[1]))
            dessin["cap_coude_d"] = (lambda t_e=t_e: translater(charger(BIBLIO / "capuchons" / "coude_d.png"),
                                                                t_e[0], t_e[1]))
            # bloc main + pioche : la poignée (centre du gant) suit la chaîne du poignet
            Gp = np.array(blocs["pivots_px"]["poignee_gant"])
            Ep = np.array(blocs["pivots_px"]["coude"])
            G_new = E_new + np.array(tourner_px(Gp - Ep, a["avant"]))
            t_b = (int(round(G_new[0] - Gp[0])), int(round(G_new[1] - Gp[1])))
            dessin["bloc_main_d"] = (lambda th=ch.get("bloc_main_d", 0), t_b=t_b:
                                     translater(charger(bloc_dir / angle_cle(th)),
                                                t_b[0], t_b[1]))
        dessin["cap_epaule_%s" % cote] = (lambda cote=cote: translater(charger(BIBLIO / "capuchons" / ("epaule_%s.png" % cote)),
                                                                       decal[0], decal[1]))

    for nom in pose["calques"]:
        if nom not in dessin:
            raise SystemExit("pièce inconnue : %s" % nom)
        img = dessin[nom]()
        ajouter(nom, img)

    out = np.zeros((CANEVAS, CANEVAS, 4), dtype=np.uint8)
    qui = np.full((CANEVAS, CANEVAS), "", dtype=object)
    for nom, img in couches:
        m = img[..., 3] > 0
        out[m] = img[m]
        qui[m] = nom
    # nettoyage des pixels isolés : même étape que l'ancre (rendu -> nettoyage -> sprite)
    out = nettoyage.nettoyer(out)
    return out, qui, utilisees, couches


def controles(out, qui, couches, pose):
    """Contrôles sur les masques visibles à la taille finale (chevauchements, hublot, hauteur, isolés)."""
    res = {"chevauchements_visibles": {}, "hauteur_px": None, "pixels_isoles": None, "image_sha256": None}
    ys, xs = np.nonzero(out[..., 3] > 0)
    if len(ys):
        res["hauteur_px"] = int(ys.max() - ys.min() + 1)
    # pixels d'un calque couverts ensuite par un calque au-dessus : recouvrements visibles
    for i, (nom_b, img_b) in enumerate(couches):
        for nom_h, img_h in couches[i + 1:]:
            if nom_b == nom_h:
                continue
            dessous = img_b[..., 3] > 0
            dessus = img_h[..., 3] > 0
            n = int(np.sum(dessous & dessus))
            if n:
                res["chevauchements_visibles"]["%s<%s" % (nom_b, nom_h)] = n
    res["pixels_isoles"] = int(nettoyage.isoles(out))
    res["pieces"] = [c[0] for c in couches]
    res["image_sha256"] = hashlib.sha256(out.tobytes()).hexdigest()[:16]
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pose")
    ap.add_argument("sortie")
    args = ap.parse_args()
    pose = json.loads(Path(args.pose).read_text(encoding="utf-8"))
    out, qui, utilisees, couches = composer_pose(pose, Path(args.sortie))
    sortie = Path(args.sortie)
    sortie.mkdir(parents=True, exist_ok=True)
    Image.fromarray(out).save(sortie / (pose["nom"] + ".png"))
    masques = sortie / "masques" / pose["nom"]
    masques.mkdir(parents=True, exist_ok=True)
    for nom, img in couches:
        Image.fromarray(((img[..., 3] > 0) * 255).astype(np.uint8)).save(masques / (nom + ".png"))
    res = controles(out, qui, couches, pose)
    res["nom"] = pose["nom"]
    res["utilisees_px"] = utilisees
    (sortie / (pose["nom"] + ".json")).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()

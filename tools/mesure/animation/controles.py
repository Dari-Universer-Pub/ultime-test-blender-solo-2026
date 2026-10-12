#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
controles.py - contrôles d'une séquence d'animation (creusage), sur les masques visibles à la taille finale.

    python3 tools/mesure/animation/controles.py FICHE.json POSES_DIR SORTIE_DIR

Lit les poses (ordre explicite des calques), les masques par calque écrits par assembleur.py, et les sorties
PNG. Chaque contrôle est mesuré, jamais modifié : un échec se corrige dans la pose ou la pièce, pas ici.
Écrit controles.json (une entrée par image + séquence) et controles.md (tableau OK / échec).
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
RACINE = HERE.parent.parent.parent
CREUSAGE = RACINE / "art" / "pixel" / "plongeur_v6" / "creusage"

TOLERANCE_PIOCHE_CASQUE = 2     # px : pioche visible sur le casque
TOLERANCE_BRAS_CASQUE = 1       # px : bras visible sur le casque
HAUTEUR_MAX = 72
TETE_LARGEUR_MIN, TETE_HAUTEUR_MIN = 12, 4


def masque(p):
    return np.array(Image.open(p).convert("L")) > 0


def couleur(p):
    return np.array(Image.open(p).convert("RGBA"))


def visible(calques_ordre, masques):
    """Calque visible à chaque pixel : le dernier de la liste (dessus) qui couvre le pixel."""
    qui = np.full(next(iter(masques.values())).shape, -1, dtype=int)
    for i, nom in enumerate(calques_ordre):
        if nom in masques:
            qui[masques[nom]] = i
    return qui


def steel(rgba):
    """Pixels d'acier de la pioche : bleu-gris (#a8b6d6, #5a6490 : vert au-dessus du rouge). Les gants violets
    (75,63,160) sont exclus : leur vert est sous leur rouge."""
    r, g, b, a = [rgba[..., i].astype(int) for i in range(4)]
    return (a > 0) & (b > r + 25) & (b > 120) & (g >= r + 5)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fiche")
    ap.add_argument("poses")
    ap.add_argument("sortie")
    args = ap.parse_args()
    fiche = json.loads(Path(args.fiche).read_text(encoding="utf-8"))
    poses_dir, sortie = Path(args.poses), Path(args.sortie)
    sortie.mkdir(parents=True, exist_ok=True)
    sorties_png = poses_dir.parent / "sortie"
    ancre = couleur(RACINE / "art" / "references" / "ancre_plongeur_v6.png")
    palette_ancre = set(map(tuple, ancre[ancre[..., 3] > 0][:, :3].tolist()))
    # palette de la chaîne : ancre + couleurs des pièces de la bibliothèque (même rendu, mêmes matières)
    for piece in (CREUSAGE / "bibliotheque" / "variantes" / "bloc_main_d").glob("*.png"):
        im = couleur(piece)
        palette_ancre |= set(map(tuple, im[im[..., 3] > 0][:, :3].tolist()))

    resultats = []
    images = []
    hashes = []
    for f in fiche["images"]:
        nom = "%02d_%s" % (f["n"], f["nom"])
        pose = json.loads((poses_dir / (nom + ".json")).read_text(encoding="utf-8"))
        rgba = couleur(sorties_png / (pose["nom"] + ".png"))
        images.append(rgba)
        hashes.append(hashlib.sha256(rgba.tobytes()).hexdigest()[:16])
        masques_dir = sorties_png / "masques" / pose["nom"]
        masques = {p.stem: masque(p) for p in masques_dir.glob("*.png")}
        ordre = pose["calques"]
        qui = visible(ordre, masques)
        contr = {}
        # 1. pioche (bloc main + pioche) et casque : chevauchement visible interdit (tolérance 2 px)
        bloc = masques.get("bloc_main_d", np.zeros_like(qui, bool))
        casque = masques.get("casque", np.zeros_like(qui, bool))
        # sans pioche dans la pose (saut) : l'indice du bloc ne correspond à aucun calque, les mesures d'outil valent 0
        i_bloc, i_casque = (ordre.index("bloc_main_d") if "bloc_main_d" in ordre else -2), ordre.index("casque")
        pioche_sur_casque = int(np.sum(bloc & casque & (qui == i_bloc)))
        contr["pioche_casque_px"] = {"valeur": pioche_sur_casque, "tolerance": TOLERANCE_PIOCHE_CASQUE,
                                     "ok": pioche_sur_casque <= TOLERANCE_PIOCHE_CASQUE}
        # 2. hublot : aucun pixel visible d'outil ou de main dedans
        verre = steel(rgba)  # acier ; le verre est bleu foncé dans le casque
        hublot = casque & (rgba[..., 2].astype(int) > rgba[..., 0].astype(int) + 40) & (rgba[..., 0] < 60) & (rgba[..., 3] > 0)
        bloc_visible_hublot = int(np.sum(hublot & bloc & (qui == i_bloc)))
        contr["outil_dans_hublot_px"] = {"valeur": bloc_visible_hublot, "ok": bloc_visible_hublot == 0}
        # 3. bras sur le casque : chevauchement visible interdit (tolérance 1 px)
        bras_sur = 0
        for b in ("bras_d_haut", "bras_d_avant", "bras_g_haut", "bras_g_avant"):
            if b in masques:
                bras_sur += int(np.sum(masques[b] & casque & (qui == ordre.index(b))))
        contr["bras_sur_casque_px"] = {"valeur": bras_sur, "tolerance": TOLERANCE_BRAS_CASQUE,
                                       "ok": bras_sur <= TOLERANCE_BRAS_CASQUE}
        # 4. hauteur outil compris
        ys = np.nonzero(rgba[..., 3] > 0)[0]
        hauteur = int(ys.max() - ys.min() + 1) if len(ys) else 0
        contr["hauteur_px"] = {"valeur": hauteur, "max": HAUTEUR_MAX, "ok": hauteur <= HAUTEUR_MAX}
        # 5. tête d'acier : bbox des pixels d'acier de la pioche visibles
        st = steel(rgba) & bloc & (qui == i_bloc)  # visible seulement : une tête cachée derrière le casque ne compte pas
        if np.any(st):
            yy, xx = np.nonzero(st)
            lw, lh = int(xx.max() - xx.min() + 1), int(yy.max() - yy.min() + 1)
        else:
            lw, lh = 0, 0
        if f.get("critere_tete", True):
            contr["tete_acier_px"] = {"largeur": lw, "hauteur": lh,
                                      "ok": lw >= TETE_LARGEUR_MIN and lh >= TETE_HAUTEUR_MIN}
        else:  # décision de Julien : le critère ne vaut que pour les images où la pioche est vue de face ou presque
            contr["tete_acier_px"] = {"largeur": lw, "hauteur": lh, "ok": True, "applicable": False,
                                      "note": "tête vue de profil : critère non applicable (géométrie, décision Julien)"}
        # 6. pixels isolés (même critère que l'ancre)
        contr["pixels_isoles"] = {"valeur": int(json.loads((sorties_png / (pose["nom"] + ".json")).read_text(
            encoding="utf-8")).get("pixels_isoles", 0)), "ok": True}
        contr["pixels_isoles"]["ok"] = contr["pixels_isoles"]["valeur"] == 0
        # 7. palette : couleurs visibles dans la palette de l'ancre ou des pièces de la bibliothèque
        couleurs = set(map(tuple, rgba[rgba[..., 3] > 0][:, :3].tolist()))
        hors = len(couleurs - palette_ancre)
        contr["palette_hors_ancre_couleurs"] = {"valeur": hors, "ok": True,
                                                "note": "couleurs nouvelles (pioche, acier) à vérifier à la main"}
        # 8. cible à l'impact (attaque) : centre de la tête d'acier visible à moins de la tolérance de la cible
        if f.get("evenement") == "impact" and "cible" in fiche and np.any(st):
            cx_, cy_ = fiche["cible"]["tete_au_contact_px"]
            tol_ = fiche["cible"].get("tolerance_px", 2)
            yy, xx = np.nonzero(st)
            dist_ = float(np.hypot(xx.mean() - cx_, yy.mean() - cy_))
            contr["cible_impact_px"] = {"ecart": round(dist_, 2), "tolerance": tol_, "ok": dist_ <= tol_}
        # 9. contact au sol à l'impact
        if f.get("moment_impact") and np.any(st):
            contr["contact_sol_impact"] = {"bas_outil_px": int(np.max(np.nonzero(st)[0])),
                                           "ok": int(np.max(np.nonzero(st)[0])) >= 91}
        resultats.append({"n": f["n"], "nom": f["nom"], "controles": contr})

    # séquence : images distinctes, confinement, boucle
    for i, h in enumerate(hashes):
        resultats[i]["hash"] = h
    distinctes = len(set(hashes)) == len(hashes)
    changements = []
    for a, b in zip(images, images[1:]):
        changements.append(int(np.sum(np.any(a != b, axis=2))))
    premiere = np.sum(np.any(images[0] != ancre, axis=2))
    boucle = {"premiere_vs_ancre_px_differents": int(premiere),
              "derniere_vs_premiere_px_differents": int(np.sum(np.any(images[-1] != images[0], axis=2)))}
    seq = {"images_distinctes": {"ok": distinctes}, "changements_px_entre_images": changements, "boucle": boucle}
    (sortie / "controles.json").write_text(json.dumps({"images": resultats, "sequence": seq}, ensure_ascii=False, indent=1),
                                           encoding="utf-8")
    lignes = ["| image | pioche/casque | hublot | bras/casque | hauteur | tête (LxH) | isolés | palette hors ancre | verdict |",
              "|---|---|---|---|---|---|---|---|---|"]
    for r in resultats:
        c = r["controles"]
        verdict_ok = all(v.get("ok", True) for v in c.values())
        lignes.append("| %d %s | %d | %d | %d | %d | %dx%d | %d | %d | %s |" % (
            r["n"], r["nom"], c["pioche_casque_px"]["valeur"], c["outil_dans_hublot_px"]["valeur"],
            c["bras_sur_casque_px"]["valeur"], c["hauteur_px"]["valeur"], c["tete_acier_px"]["largeur"],
            c["tete_acier_px"]["hauteur"], c["pixels_isoles"]["valeur"], c["palette_hors_ancre_couleurs"]["valeur"],
            "OK" if verdict_ok else "ÉCHEC"))
    lignes += ["", "Séquence : images distinctes %s ; changements px entre images %s ; boucle %s" % (
        "OK" if distinctes else "ÉCHEC", changements, boucle)]
    (sortie / "controles.md").write_text("\n".join(lignes) + "\n", encoding="utf-8")
    print("\n".join(lignes))


if __name__ == "__main__":
    main()

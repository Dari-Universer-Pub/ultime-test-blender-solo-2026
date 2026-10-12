#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
intention.py - planche d'intention d'un lot d'animation (RÈGLE ANIMATION, étape A bis).

    python3 tools/planches/intention.py DONNEES.json ANCRE.png SORTIE.png [--echelle 4]

Une image par pose : l'ancre estompée en fond, un squelette à plat (tête, buste, épaules, coudes, mains,
hanches, jambes) et l'outil (manche et tête) en coordonnées écran du sprite 112 x 112. Sous la grille,
les contrôles 2D calculés : portée des bras avec la triche déclarée (en % d'allongement), écart d'angle
entre images successives, outil hors du torse, mains sur l'outil, hauteur de la tête.

Outil de PLANIFICATION : c'est un schéma de pose, il ne dessine aucun asset. Les coordonnées de l'ancre
viennent de la projection Blender de l'idle (voir ETAT.md, creusage).
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw

# projection écran de l'idle (px), mesurée dans Blender avec world_to_camera_view
ANCRE = {
    "casque": (55.29, 42.56), "cou": (55.29, 54.10), "poitrine": (55.29, 58.19), "taille": (55.29, 63.24),
    "bassin": (55.29, 66.60), "ep_g": (46.72, 56.64), "ep_d": (63.85, 59.74),
    "hanche_g": (50.80, 67.71), "hanche_d": (59.77, 69.34),
    "genou_g": (49.54, 77.57), "genou_d": (59.32, 79.34),
    "cheville_g": (49.99, 83.91), "cheville_d": (60.59, 85.83),
    "botte_g": (48.99, 89.57), "botte_d": (59.59, 91.49),
}
L_BRAS = 9.7          # épaule -> coude (px)
L_AVANT = 9.9         # coude -> gant, y compris le gant (px)
PORTEE = L_BRAS + L_AVANT   # bras tendu, sans triche (19,6 px)
TORSE = (46.5, 53.0, 66.5, 71.0)   # rectangle du torse (x0, y0, x1, y1)
SOL = 91.5            # ligne de sol (bas des bottes)
TETE_R = 13.5         # rayon de la tête (px)
DEMI_TETE = 6.5       # demi-longueur de la barre de tête (13 px)
ECH = 4
FOND = (30, 120, 150, 255)


TRANSLIT = str.maketrans({"é": "e", "è": "e", "ê": "e", "à": "a", "â": "a", "ç": "c", "ù": "u", "ô": "o",
                          "î": "i", "É": "E", "È": "E", "’": "'", "°": " deg", "→": "->", "≥": ">=", "Δ": "d"})


def arm(S, H, hint):
    """Coude pour que le gant arrive en H. Triche = allongement nécessaire (1.0 = pas de triche)."""
    dx, dy = H[0] - S[0], H[1] - S[1]
    d = math.hypot(dx, dy)
    k = max(1.0, d / PORTEE)
    l1, l2 = L_BRAS * k, L_AVANT * k
    ux, uy = dx / d, dy / d
    a = (l1 * l1 - l2 * l2 + d * d) / (2 * d)
    h = math.sqrt(max(0.0, l1 * l1 - a * a))
    px, py = -uy, ux
    if px * hint[0] + py * hint[1] < 0:
        px, py = -px, -py
    coude = (S[0] + ux * a + px * h, S[1] + uy * a + py * h)
    return coude, k


def angle_phi(butt, head):
    """Direction butt -> tête, en degrés, sens horaire depuis la verticale haute (0 = haut, 90 = droite, 180 = bas)."""
    return math.degrees(math.atan2(head[0] - butt[0], -(head[1] - butt[1]))) % 360


def dans_torse(p, q):
    x0, y0, x1, y1 = TORSE
    for i in range(1, 60):
        t = i / 60
        x = p[0] + (q[0] - p[0]) * t
        y = p[1] + (q[1] - p[1]) * t
        if x0 < x < x1 and y0 < y < y1:
            return True
    return False


def ecart_angle(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("donnees")
    ap.add_argument("ancre")
    ap.add_argument("sortie")
    ap.add_argument("--echelle", type=int, default=ECH)
    args = ap.parse_args()
    e = args.echelle
    data = json.loads(Path(args.donnees).read_text(encoding="utf-8"))
    frames = data["frames"]
    ancre = Image.open(args.ancre).convert("RGBA")

    lignes, controles, phis = [], [], []
    panneaux = []
    for f in frames:
        n, nom = f["n"], f["nom"]
        dx, dy = f.get("dx", 0), f.get("dy", 0)
        S = {"g": (ANCRE["ep_g"][0] + dx, ANCRE["ep_g"][1] + dy), "d": (ANCRE["ep_d"][0] + dx, ANCRE["ep_d"][1] + dy)}
        cou = (ANCRE["cou"][0] + dx, ANCRE["cou"][1] + dy)
        tete = (ANCRE["casque"][0] + dx, ANCRE["casque"][1] + dy)
        main = f["hands"]
        triche = {}
        coudes = {}
        for cote, hint in (("g", (-1.0, 0.6)), ("d", (1.0, 0.6))):
            cle = "L" if cote == "g" else "R"
            H = tuple(main[cle])
            c, k = arm(S[cote], H, hint)
            coudes[cote] = c
            triche[cote] = round((k - 1.0) * 100)
        panneau = Image.new("RGBA", (112 * e, 112 * e), FOND)
        fond = ancre.resize((112 * e, 112 * e), Image.NEAREST)
        fond.putalpha(fond.getchannel("A").point(lambda v: int(v * 0.35)))
        panneau.alpha_composite(fond)
        d = ImageDraw.Draw(panneau)

        def P(p):
            return (p[0] * e, p[1] * e)

        blanc = (235, 235, 235, 255)
        d.ellipse([P((tete[0] - TETE_R, tete[1] - TETE_R)), P((tete[0] + TETE_R, tete[1] + TETE_R))], outline=blanc, width=2)
        d.line([P(cou), P((ANCRE["bassin"][0] + dx, ANCRE["bassin"][1] + dy))], fill=blanc, width=2)
        d.line([P(S["g"]), P(S["d"])], fill=blanc, width=2)
        for cote in ("g", "d"):
            d.line([P(S[cote]), P(coudes[cote]), P(tuple(main["L" if cote == "g" else "R"]))], fill=(255, 255, 255, 255), width=3)
            d.ellipse([P((coudes[cote][0] - 1.5, coudes[cote][1] - 1.5)), P((coudes[cote][0] + 1.5, coudes[cote][1] + 1.5))], fill=(255, 255, 255, 255))
        for cote in ("L", "R"):
            h = main[cote]
            d.ellipse([P((h[0] - 2.5, h[1] - 2.5)), P((h[0] + 2.5, h[1] + 2.5))], fill=(160, 110, 255, 255))
        for cote in ("g", "d"):
            hanche = ANCRE["hanche_" + cote]
            genou = ANCRE["genou_" + cote]
            cheville = ANCRE["cheville_" + cote]
            botte = ANCRE["botte_" + cote]
            d.line([P(hanche), P(genou), P(cheville), P(botte)], fill=(180, 180, 255, 255), width=2)
        d.line([P(ANCRE["hanche_g"]), P(ANCRE["hanche_d"])], fill=(180, 180, 255, 255), width=2)

        verdict_torse = "pas d'outil"
        if f["phi"] is not None:
            butt, head = tuple(f["butt"]), tuple(f["head"])
            phi = angle_phi(butt, head)
            phis.append((n, phi))
            d.line([P(butt), P(head)], fill=(230, 170, 90, 255), width=3 * e // 2)
            ux, uy = (head[0] - butt[0]), (head[1] - butt[1])
            L = math.hypot(ux, uy)
            px, py = -uy / L, ux / L
            d.line([P((head[0] - DEMI_TETE * px, head[1] - DEMI_TETE * py)), P((head[0] + DEMI_TETE * px, head[1] + DEMI_TETE * py))],
                   fill=(200, 215, 240, 255), width=4)
            bas = max(head[1] - DEMI_TETE * py, head[1] + DEMI_TETE * py)
            verdict_torse = "OUTIL DANS LE TORSE" if dans_torse(butt, head) else "outil hors du torse"
            mains_ok = abs(math.hypot(main["L"][0] - main["R"][0], main["L"][1] - main["R"][1])) >= 8.0
            tete_bas_ok = bas <= SOL + 0.5 if n == 5 else True
            hauteur_tete = bas
        else:
            phi = None
            mains_ok = True
            tete_bas_ok = True
            bas = None
        d.text((6, 4), "%d  %s" % (n, nom), fill=(255, 255, 255, 255))
        panneaux.append(panneau)

        ang_verticale = "" if phi is None else "%.0f" % abs(phi - 180)
        lignes.append("%d. %s : angle outil phi = %s deg (depuis la verticale basse : %s deg) ; buste dx %+d px, dy %+d px ; "
                      "triche bras gauche +%d %%, bras droit +%d %% ; %s. A lire : %s" % (
                          n, nom, "-" if phi is None else "%.0f" % phi, ang_verticale or "-", dx, dy,
                          triche["g"], triche["d"], verdict_torse, f["lire"]))
        controles.append({"n": n, "mains_espacees_8px": mains_ok, "outil_hors_torse": verdict_torse == "outil hors du torse" or phi is None,
                          "triche_bras": triche, "bas_tete_px": None if bas is None else round(bas, 2),
                          "tete_au_sol_ok": tete_bas_ok})

    # écarts d'angle entre images successives
    ecarts = []
    for (n1, p1), (n2, p2) in zip(phis, phis[1:]):
        ecarts.append("images %d -> %d : %.0f deg" % (n1, n2, ecart_angle(p1, p2)))
    ecarts_txt = "ecarts d'angle entre images successives : " + " ; ".join(ecarts) + " (cible >= 40)"

    colonnes = 3
    lignes_ctrl = [ecarts_txt]
    for c in controles:
        lignes_ctrl.append("controle image %d : mains espacees >= 8 px %s ; outil hors torse %s ; triche bras %s ; bas de la tete %s px (sol %.1f) %s" % (
            c["n"], "OK" if c["mains_espacees_8px"] else "ECHEC",
            "OK" if c["outil_hors_torse"] else "ECHEC", c["triche_bras"],
            "-" if c["bas_tete_px"] is None else c["bas_tete_px"], SOL,
            "OK" if c["tete_au_sol_ok"] else "ECHEC"))
    lignes_all = lignes + [""] + lignes_ctrl
    Path(args.sortie).with_suffix(".txt").write_text("\n".join(lignes_all) + "\n", encoding="utf-8")

    w_case = 112 * e
    marge = 12
    rangees = math.ceil(len(panneaux) / colonnes)
    haut_texte = 24 + 15 * len(lignes_all) + marge
    W = colonnes * w_case + (colonnes + 1) * marge
    H = rangees * (w_case + marge) + marge + haut_texte
    planche = Image.new("RGBA", (W, H), (28, 28, 28, 255))
    dtxt = ImageDraw.Draw(planche)
    for i, p in enumerate(panneaux):
        r, c = divmod(i, colonnes)
        x = marge + c * (w_case + marge)
        y = marge + r * (w_case + marge)
        planche.alpha_composite(p, (x, y))
    y0 = marge + rangees * (w_case + marge)
    dtxt.text((marge, y0), "Planche d'intention (creusage) : ancre estompee, squelette a plat, outil en coordonnees ecran ; controles 2D ci-dessous",
              fill=(255, 220, 120, 255))
    for k, t in enumerate(lignes_all):
        dtxt.text((marge, y0 + 24 + 15 * k), t.translate(TRANSLIT), fill=(235, 235, 235, 255))
    planche.convert("RGB").save(args.sortie)
    print("planche :", args.sortie)
    print("image_sha256 :", hashlib.sha256(Path(args.sortie).read_bytes()).hexdigest())
    print("\n".join(lignes_ctrl))


if __name__ == "__main__":
    main()

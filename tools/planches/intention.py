#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
intention.py - planche d'intention d'un lot d'animation (RÈGLE ANIMATION, étape A bis).

    python3 tools/planches/intention.py DONNEES.json ANCRE.png SORTIE.png [--echelle 4]

Produit trois fichiers à côté de SORTIE : la planche (.png), la liste des contrôles calculés (.txt)
et la table d'intention (.md) avec les étirements déclarés, les écarts d'angle et les durées.

Par image : l'ancre estompée en fond, une silhouette pleine simplifiée, le squelette à plat (tête,
buste, épaules, coudes, mains, hanches, pieds), l'outil avec ses deux extrémités (manche de 35 px,
tête d'acier de 13 px), les mains sur le manche, et les lignes de contrôle (sol, haut de 72 px,
hublot, portée des bras avec la triche de 25 %).

Outil de PLANIFICATION : c'est un schéma de pose en coordonnées écran du sprite 112 x 112, il ne
dessine aucun asset. Les coordonnées de l'ancre viennent de la projection Blender de l'idle.
La bbox alpha de l'ancre (art/references/ancre_plongeur_v6.png) donne le haut 20 et le sol 92.
"""
import argparse
import hashlib
import json
import math
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw

# projection écran de l'idle (px sprite 112), mesurée dans Blender avec world_to_camera_view
ANCRE = {
    "casque": (55.29, 42.56), "cou": (55.29, 54.10), "poitrine": (55.29, 58.19), "taille": (55.29, 63.24),
    "bassin": (55.29, 66.60), "ep_g": (46.72, 56.64), "ep_d": (63.85, 59.74),
    "hanche_g": (50.80, 67.71), "hanche_d": (59.77, 69.34),
    "genou_g": (49.54, 77.57), "genou_d": (59.32, 79.34),
    "cheville_g": (49.99, 83.91), "cheville_d": (60.59, 85.83),
    "botte_g": (48.99, 89.57), "botte_d": (59.59, 91.49),
}
HAUT = 20.0           # haut du sprite de l'ancre (bbox alpha, première ligne occupée)
SOL = 92.0            # sol de l'ancre (bbox alpha, dernière ligne occupée + 1)
HAUTEUR_MAX = 72.0    # plongeur 72 px au plus, outil compris
L_BRAS = 9.7          # épaule -> coude (px)
L_AVANT = 9.9         # coude -> gant, gant compris (px)
PORTEE = L_BRAS + L_AVANT   # bras tendu sans triche (19,6 px)
ETIRE_MAX = 0.25      # triche de la fiche : +25 % au plus
MANCHE = 35.0         # longueur du manche, de la tête au bout (px)
TETE_DEMI = 6.5       # demi-longueur de la tête d'acier (13 px, >= 12 demandés)
TETE_R = 11.5         # rayon du casque (dessin)
HUBLOT = (46.5, 43.5) # centre du hublot à l'ancre
HUBLOT_R = 7.5        # rayon du cadre du hublot, marge comprise
TORSE = (44.0, 57.0, 67.0, 71.0)     # poitrine et ventre (x0, y0, x1, y1)
JAMBE_G = (43.0, 76.0, 53.0, 92.0)   # jambe gauche (écran)
JAMBE_D = (53.0, 78.0, 66.0, 92.0)   # jambe droite (écran)
PIED_D_DROIT = 66.0   # bord droit de la botte droite
ECART_MIN = 40.0      # écart d'angle entre images successives
ECH = 4
FOND = (30, 120, 150, 255)

TRANSLIT = str.maketrans({"é": "e", "è": "e", "ê": "e", "à": "a", "â": "a", "ç": "c", "ù": "u", "ô": "o",
                          "î": "i", "É": "E", "È": "E", "’": "'", "°": " deg", "→": "->", "≥": ">=", "≤": "<=",
                          "Δ": "d", "φ": "phi", "–": "-", "—": "-", "×": "x"})


def sh(p, s):
    return (p[0] + s[0], p[1] + s[1])


def arm(S, H, hint):
    """Coude pour que le gant arrive en H. k = allongement nécessaire (1.0 = pas de triche)."""
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
    return (S[0] + ux * a + px * h, S[1] + uy * a + py * h), k


def angle_phi(butt, head):
    """Direction butt -> tête, en degrés, sens horaire depuis la verticale haute."""
    return math.degrees(math.atan2(head[0] - butt[0], -(head[1] - butt[1]))) % 360


def ecart_angle(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)


def sur_segment(P, A, B):
    ax, ay = B[0] - A[0], B[1] - A[1]
    L2 = ax * ax + ay * ay
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((P[0] - A[0]) * ax + (P[1] - A[1]) * ay) / L2))
    return math.hypot(A[0] + ax * t - P[0], A[1] + ay * t - P[1])


def longueur_dans_rect(A, B, r, N=200):
    x0, y0, x1, y1 = r
    n = 0
    for i in range(N + 1):
        t = i / N
        x = A[0] + (B[0] - A[0]) * t
        y = A[1] + (B[1] - A[1]) * t
        if x0 <= x <= x1 and y0 <= y <= y1:
            n += 1
    return MANCHE * n / (N + 1)


def calcul(f):
    """Géométrie d'une image : outil, mains, bras, contrôles. Tout est recalculé ici, rien n'est saisi à la main."""
    phi = math.radians(f["phi"])
    u = (math.sin(phi), -math.cos(phi))          # butt -> tête
    p = (math.cos(phi), math.sin(phi))           # perpendiculaire (tête d'acier)
    head = tuple(f["head"])
    butt = (head[0] - MANCHE * u[0], head[1] - MANCHE * u[1])
    bar_a = (head[0] - TETE_DEMI * p[0], head[1] - TETE_DEMI * p[1])
    bar_b = (head[0] + TETE_DEMI * p[0], head[1] + TETE_DEMI * p[1])
    bx, by = f["buste"]
    cx, cy = f["casque"]
    mains = {c: (butt[0] + f["f"][c] * MANCHE * u[0], butt[1] + f["f"][c] * MANCHE * u[1]) for c in ("L", "R")}
    ep = f.get("epaule", {"g": [0, 0], "d": [0, 0]})
    S = {"g": sh(ANCRE["ep_g"], (bx + ep["g"][0], by + ep["g"][1])),
         "d": sh(ANCRE["ep_d"], (bx + ep["d"][0], by + ep["d"][1]))}
    coude, etire = {}, {}
    for cote, cle, hint in (("g", "L", (-1.0, 0.6)), ("d", "R", (1.0, 0.6))):
        coude[cote], k = arm(S[cote], mains[cle], hint)
        etire[cote] = (k - 1.0) * 100.0
    corps = {
        "casque": sh(ANCRE["casque"], (cx, cy)),
        "cou": sh(ANCRE["cou"], (bx, by)),
        "poitrine": sh(ANCRE["poitrine"], (bx, by)),
        "taille": sh(ANCRE["taille"], (bx / 2, by / 2)),
    }
    hublot = sh(HUBLOT, (cx, cy))
    bar_haut = min(bar_a[1], bar_b[1])
    bar_bas = max(bar_a[1], bar_b[1])
    haut_outil = min(butt[1], bar_haut)
    bas_outil = max(butt[1], bar_bas)
    haut = min(HAUT + cy, haut_outil)
    hublot_d = min(sur_segment(hublot, butt, head), sur_segment(hublot, bar_a, bar_b))
    return {
        "phi": f["phi"], "phi_obt": angle_phi(butt, head), "butt": butt, "head": head,
        "bar": (bar_a, bar_b), "mains": mains, "S": S, "coude": coude, "etire": etire, "corps": corps,
        "hublot": hublot, "hauteur": SOL - haut, "bas_outil": bas_outil, "haut_outil": haut_outil,
        "hublot_d": hublot_d, "torse_px": longueur_dans_rect(butt, head, TORSE),
        "jambe_g_px": longueur_dans_rect(butt, head, JAMBE_G),
        "jambe_d_px": longueur_dans_rect(butt, head, JAMBE_D),
    }


def controles(n, r):
    """Liste (nom, ok, texte). ok = True / False / None (information seulement)."""
    out = []
    e_max = max(r["etire"].values())
    out.append(("bras", e_max <= ETIRE_MAX * 100 + 0.05,
                "etirement G %+.0f %% D %+.0f %%" % (r["etire"]["g"], r["etire"]["d"])))
    out.append(("hauteur", r["hauteur"] <= HAUTEUR_MAX + 0.05, "hauteur %.1f px (max 72)" % r["hauteur"]))
    out.append(("sol", r["bas_outil"] <= SOL + 0.05, "outil bas y=%.1f (sol 92)" % r["bas_outil"]))
    out.append(("hublot", r["hublot_d"] >= HUBLOT_R, "outil a %.1f px du hublot (cadre %.1f)" % (r["hublot_d"], HUBLOT_R)))
    out.append(("torse", r["torse_px"] < 0.5, "manche dans le torse %.1f px" % r["torse_px"]))
    out.append(("jambe G", r["jambe_g_px"] < 0.5, "manche dans la jambe gauche %.1f px" % r["jambe_g_px"]))
    if n == 5:
        touche = r["bas_outil"] >= SOL - 0.5
        devant = r["head"][0] >= PIED_D_DROIT + 4
        out.append(("impact", touche and devant,
                    "tete au sol %s ; a droite des pieds (x %.1f > %.0f) %s" % (
                        "oui" if touche else "non", r["head"][0], PIED_D_DROIT, "oui" if devant else "non")))
    return out


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
    sortie = Path(args.sortie)

    R = [calcul(f) for f in frames]
    phis = [(f["n"], r["phi_obt"]) for f, r in zip(frames, R)]
    gaps = []
    for i, f in enumerate(frames):
        j = (i - 1) % len(frames)
        g = ecart_angle(R[j]["phi_obt"], R[i]["phi_obt"])
        gaps.append((frames[j]["n"], f["n"], g))

    # ---- planche : une image par pose
    panneaux = []
    for f, r in zip(frames, R):
        n, nom = f["n"], f["nom"]
        panneau = Image.new("RGBA", (112 * e, 112 * e), FOND)
        fond = ancre.resize((112 * e, 112 * e), Image.NEAREST)
        fond.putalpha(fond.getchannel("A").point(lambda v: int(v * 0.35)))
        panneau.alpha_composite(fond)
        d = ImageDraw.Draw(panneau)

        def P(q):
            return (q[0] * e, q[1] * e)

        def pointille(A, B, couleur, cadence=3, larg=1):
            L = math.hypot(B[0] - A[0], B[1] - A[1])
            m = max(1, int(L // cadence))
            for i in range(0, m, 2):
                t0, t1 = i / m, min(1.0, (i + 1) / m)
                d.line([P((A[0] + (B[0] - A[0]) * t0, A[1] + (B[1] - A[1]) * t0)),
                        P((A[0] + (B[0] - A[0]) * t1, A[1] + (B[1] - A[1]) * t1))], fill=couleur, width=larg)

        def cercle_pointille(C, rayon, couleur):
            pts = [(C[0] + rayon * math.cos(2 * math.pi * k / 48), C[1] + rayon * math.sin(2 * math.pi * k / 48))
                   for k in range(49)]
            for a, b in zip(pts, pts[1:]):
                pointille(a, b, couleur, cadence=2)

        # lignes de contrôle (dessous)
        pointille((0, SOL), (112, SOL), (255, 90, 90, 255), cadence=4, larg=max(1, e // 2))
        pointille((0, HAUT), (112, HAUT), (120, 255, 160, 255), cadence=4, larg=max(1, e // 2))
        for cote in ("g", "d"):
            cercle_pointille(r["S"][cote], PORTEE * (1 + ETIRE_MAX), (150, 190, 255, 255))
        hc = r["hublot"]
        d.ellipse([P((hc[0] - HUBLOT_R, hc[1] - HUBLOT_R)), P((hc[0] + HUBLOT_R, hc[1] + HUBLOT_R))],
                  outline=(255, 235, 90, 255), width=max(1, e // 2))

        c = r["corps"]
        sil = (74, 62, 104, 235)
        def trait(pts, larg, couleur):
            d.line([P(q) for q in pts], fill=couleur, width=int(larg * e), joint="curve")
            for q in pts:
                d.ellipse([P((q[0] - larg / 2, q[1] - larg / 2)), P((q[0] + larg / 2, q[1] + larg / 2))], fill=couleur)

        # silhouette pleine simplifiée
        d.ellipse([P((c["casque"][0] - TETE_R, c["casque"][1] - TETE_R)),
                   P((c["casque"][0] + TETE_R, c["casque"][1] + TETE_R))], fill=sil)
        trait([c["cou"], c["poitrine"], c["taille"], ANCRE["bassin"]], 11, sil)
        trait([r["S"]["g"], r["S"]["d"]], 6, sil)
        for cote in ("g", "d"):
            cle = "L" if cote == "g" else "R"
            trait([r["S"][cote], r["coude"][cote], r["mains"][cle]], 4.5, sil)
        for cote in ("g", "d"):
            trait([ANCRE["hanche_" + cote], ANCRE["genou_" + cote], ANCRE["cheville_" + cote], ANCRE["botte_" + cote]],
                  4.5, sil)
        # outil : manche et tête, une extrémité à chaque bout
        bois = (232, 168, 92, 255)
        acier = (214, 226, 246, 255)
        d.line([P(r["butt"]), P(r["head"])], fill=bois, width=int(2.5 * e))
        d.line([P(r["bar"][0]), P(r["bar"][1])], fill=acier, width=int(2.5 * e))
        for q in (r["bar"][0], r["bar"][1], r["butt"]):
            d.ellipse([P((q[0] - 1.2, q[1] - 1.2)), P((q[0] + 1.2, q[1] + 1.2))], fill=(255, 150, 60, 255))
        # squelette à plat (blanc, fin)
        blanc = (255, 255, 255, 255)
        d.ellipse([P((c["casque"][0] - TETE_R, c["casque"][1] - TETE_R)),
                   P((c["casque"][0] + TETE_R, c["casque"][1] + TETE_R))], outline=blanc, width=max(1, e // 2))
        d.line([P(c["cou"]), P(ANCRE["bassin"])], fill=blanc, width=max(1, e // 2))
        d.line([P(r["S"]["g"]), P(r["S"]["d"])], fill=blanc, width=max(1, e // 2))
        for cote in ("g", "d"):
            cle = "L" if cote == "g" else "R"
            d.line([P(r["S"][cote]), P(r["coude"][cote]), P(r["mains"][cle])], fill=blanc, width=max(1, e // 2))
        d.line([P(ANCRE["hanche_g"]), P(ANCRE["hanche_d"])], fill=blanc, width=max(1, e // 2))
        for cote in ("g", "d"):
            d.line([P(ANCRE["hanche_" + cote]), P(ANCRE["genou_" + cote]), P(ANCRE["cheville_" + cote]),
                    P(ANCRE["botte_" + cote])], fill=blanc, width=max(1, e // 2))
        # mains sur le manche
        for cle, couleur in (("L", (110, 230, 255, 255)), ("R", (255, 120, 220, 255))):
            h = r["mains"][cle]
            d.ellipse([P((h[0] - 2.2, h[1] - 2.2)), P((h[0] + 2.2, h[1] + 2.2))], fill=couleur)
        d.text((5, 4), "%d %s  phi %+d" % (n, nom.upper(), f["phi"]), fill=(255, 255, 255, 255))
        panneaux.append(panneau)

    # ---- textes : table, contrôles, conforme / écart
    lignes_table = []
    lignes_ctrl = []
    for i, (f, r) in enumerate(zip(frames, R)):
        ok_list = controles(f["n"], r)
        ko = [t for (_, ok, t) in ok_list if ok is False]
        phi_obt = ((r["phi_obt"] + 180) % 360) - 180      # affiché entre -180 et +180
        lignes_table.append("| %d | %s | %s | %+d | %+.0f | %.0f | %+.1f ; %+.1f | %+.1f ; %+.1f | G %+.0f %% / D %+.0f %% | "
                            "%.2f / %.2f | (%.1f, %.1f) / (%.1f, %.1f) | %s |" % (
                                f["n"], f["nom"], f["duree"], f["phi"], phi_obt,
                                gaps[i][2],
                                f["buste"][0], f["buste"][1], f["casque"][0], f["casque"][1],
                                r["etire"]["g"], r["etire"]["d"], f["f"]["L"], f["f"]["R"],
                                r["butt"][0], r["butt"][1], r["head"][0], r["head"][1],
                                "; ".join(ko) if ko else "OK"))
        lignes_ctrl.append("%d. %s (%s) : %s" % (f["n"], f["nom"], f["duree"], " ; ".join(t for (_, _, t) in ok_list)))
        lignes_ctrl.append("   conforme : %s" % f["conforme"])
        lignes_ctrl.append("   ECART : %s" % f["ecart"])
    gaps_txt = "ecarts d'angle successifs : " + " ; ".join(
        "%d -> %d : %.0f deg%s" % (a, b, g, "" if g >= ECART_MIN else " (ECART, cible >= 40)") for a, b, g in gaps)
    lignes_ctrl.insert(0, gaps_txt)
    lignes_all = lignes_ctrl

    texte_md = [
        "# Table d'intention : creusage (fiche « creusage à la pioche, style Stardew »)", "",
        "Angles : depuis la verticale haute, sens horaire ; le manche va du bout (butt) à la tête d'acier. "
        "Écart d'angle de l'image 1 : avec l'image 6 (la séquence boucle). "
        "Étirements : triche déclarée (bras allongé jusqu'à +25 % au plus). Décalages : buste et casque en px sprite. "
        "Mains : fraction du manche depuis le bout (0 = bout, 1 = tête).", "",
        "| image | nom | durée | phi cible | phi obtenu | écart d'angle avec l'image précédente | buste dx ; dy | casque dx ; dy | "
        "étirement des bras | mains L / R | bout / tête (x, y) | contrôles calculés |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ] + lignes_table + ["", "Écarts d'angle entre images successives (cible >= 40 deg) :", ""] + [
        "- %d -> %d : %.0f deg%s" % (a, b, g, "" if g >= ECART_MIN else " : ÉCART") for a, b, g in gaps]

    # ---- assemblage de la planche
    w_case = 112 * e
    marge = 12
    colonnes = 3
    rangees = math.ceil(len(panneaux) / colonnes)
    titre = ("Planche d'intention (creusage, fiche Stardew) : ancre estompee, silhouette pleine, squelette a plat, "
             "outil bout + tete ; sol rouge, haut 72 px vert, hublot jaune, portee des bras +25 % bleu")
    lignes_wrap = []
    for t in lignes_all:
        lignes_wrap.extend(textwrap.wrap(t.translate(TRANSLIT), 200) or [""])
    haut_texte = 24 + 15 * len(lignes_wrap) + marge
    W = colonnes * w_case + (colonnes + 1) * marge
    H = rangees * (w_case + marge) + marge + haut_texte
    planche = Image.new("RGBA", (W, H), (28, 28, 28, 255))
    dtxt = ImageDraw.Draw(planche)
    for i, pnl in enumerate(panneaux):
        rr, cc = divmod(i, colonnes)
        planche.alpha_composite(pnl, (marge + cc * (w_case + marge), marge + rr * (w_case + marge)))
    y0 = marge + rangees * (w_case + marge)
    dtxt.text((marge, y0), titre.translate(TRANSLIT), fill=(255, 220, 120, 255))
    for k, t in enumerate(lignes_wrap):
        dtxt.text((marge, y0 + 24 + 15 * k), t, fill=(235, 235, 235, 255))

    sortie.parent.mkdir(parents=True, exist_ok=True)
    planche.convert("RGB").save(sortie)
    sortie.with_suffix(".txt").write_text("\n".join(lignes_all) + "\n", encoding="utf-8")
    sortie.with_suffix(".md").write_text("\n".join(texte_md) + "\n", encoding="utf-8")
    print("planche :", sortie)
    print("image_sha256 :", hashlib.sha256(sortie.read_bytes()).hexdigest())
    print("\n".join(lignes_all))


if __name__ == "__main__":
    main()

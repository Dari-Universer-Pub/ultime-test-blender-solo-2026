"""dessin.py (passe 7) : cartes de pixels EXPLICITES, formes arrondies redessinées.
Calques dans l'ordre du peintre. Casque, arc de lumière, hublot et collerette : repris des passes approuvées.
Corps, membres, gants, bottes, bouteille et corde : lignes écrites pixel par pixel (rangée par rangée).
Chaque ligne = (x de départ, chaîne de caractères) ; une chaîne se lit de gauche à droite ; '#' = contour."""
import sys

W, H = 51, 72


def ligne(y, x0, texte, contour_droite=False):
    """Une rangée explicite : chaque caractère est un pixel. contour_droite ajoute '#' juste à droite."""
    if contour_droite:
        texte = texte + "#"
    return (x0, texte)


def band(y, gauche, droite, segs, contour=True):
    """Ligne de gauche à droite (incluse) : segs = [(caractère, nombre)] ; '#' à droite si contour."""
    total = sum(n for _, n in segs)
    assert total == droite - gauche + 1, (y, gauche, droite, total)
    return (gauche, "".join(c * n for c, n in segs) + ("#" if contour else ""))


def calque_torse():
    """Tonneau rond : lumière clusterisée en haut à gauche (h), ombre à droite (e), ceinture de cuir (j/i),
    ombre arrondie sous la ceinture (e), bassin. Contour à droite seulement."""
    r = {}
    r[34] = [ligne(34, 16, "hhhggffffffffeeeeeeee", True)]
    r[35] = [ligne(35, 15, "hhhggfffffffffffffeeeee", True)]
    r[36] = [ligne(36, 14, "ggggfffffffffffffffeeeeee", True)]
    r[37] = [ligne(37, 14, "ggggfffffffffffffffeeeeee", True)]
    for y in (38, 39, 40, 41):
        r[y] = [ligne(y, 13, "ggggfffffffffffffffffeeeeee", True)]
    r[42] = [ligne(42, 14, "ggggfffffffffffffffeeeeee", True)]
    r[43] = [ligne(43, 14, "ggggfffffffffffffffeeeeee", True)]
    r[44] = [ligne(44, 15, "iijjjjjjjjjjjjjjjjjjjji", True)]
    r[45] = [ligne(45, 16, "ijjjjjjjjjjjjjjjjjjjji", True)]
    r[46] = [ligne(46, 17, "iiiiiiiiiiiiiiiiiii", True)]
    r[47] = [ligne(47, 18, "eeeeeeeeeeeeeeeee", True)]
    r[48] = [ligne(48, 16, "eeeeeeeeeeeeeeeeeeeee", True)]
    r[49] = [ligne(49, 16, "eeeeeeeeeeeeeeeeeeeee", True)]
    r[50] = [ligne(50, 17, "eeeeeeeeeeeeeeeeeee", True)]
    r[51] = [ligne(51, 17, "eeeeeeeeeeeeeeeeeee", True)]
    return r


def calque_zip_plis():
    """Fermeture centrale (1 px, indigo), trois plis longs et nets dessinés à la main."""
    r = {}
    def a(y, x0, t):
        r.setdefault(y, []).append((x0, t))
    for y in range(34, 44):
        a(y, 26, "%")                            # fermeture
    a(36, 19, "ff")                              # pli 1 : 2 px au départ, puis 1 px en diagonale 2:1
    a(37, 19, "f")
    a(38, 20, "f")
    a(39, 20, "f")
    a(40, 21, "f")
    a(41, 21, "f")
    a(37, 31, "e")                               # pli 2 côté ombre
    a(38, 32, "e")
    a(39, 32, "e")
    a(40, 33, "e")
    a(41, 33, "e")
    a(44, 25, "ddc")                             # boucle laiton 3 x 2 sur la ceinture
    a(45, 25, "ccc")
    return r


def calque_bras_lointain():
    """Bras lointain (gauche), derrière le torse. Diagonale en rythme 2:1, coude arrondi, manche qui s'évase,
    manchette sombre de 2 px, gant en mitaine ronde avec pouce et reflet."""
    r = {}
    gauche = {36: 11, 37: 11, 38: 10, 39: 10, 40: 9, 41: 9, 42: 8, 43: 8, 44: 7, 45: 6, 46: 5, 47: 4, 48: 4, 49: 5}
    for y, g in gauche.items():
        w = 7 if y in (44, 45, 46, 47) else 6
        t = ("ggggfff" if w == 7 else "gggfff")
        r[y] = [ligne(y, g, t)]
    r[50] = [ligne(50, 5, "mmmmmm")]
    r[51] = [ligne(51, 5, "mmmmmm")]
    r[52] = [ligne(52, 4, "oonnnnn")]
    r[53] = [ligne(53, 3, "onnnnnnnn")]
    r[54] = [ligne(54, 2, "onnnnnnnnn")]
    r[55] = [ligne(55, 2, "nnnnnnnnnn")]
    r[56] = [ligne(56, 2, "nnnnnnnnn")]
    r[57] = [ligne(57, 3, "nnnnnnnn")]
    r[58] = [ligne(58, 4, "nnnnnn")]
    r[54] = r[54] + [(1, "n")]                   # pouce
    r[55] = r[55] + [(1, "n")]
    r[59] = [ligne(59, 4, "######")]
    return r


def calque_bras_proche():
    """Bras proche (droite), devant le torse : épaule ronde, coude plié, manche qui s'évase,
    manchette sombre de 2 px, gant en mitaine ronde avec pouce et reflet."""
    r = {}
    rows = {
        36: (37, "ffffff", True), 37: (38, "ffffff", True), 38: (39, "ffffff", True),
        39: (40, "ffffee", True), 40: (41, "ffffee", True), 41: (42, "fffeee", True),
        42: (42, "fffeee", True), 43: (43, "fffeee", True), 44: (44, "ffffee", True),
        45: (44, "fffffee", True), 46: (44, "ffffee", True), 47: (44, "fffee", True),
        48: (43, "fffee", True), 49: (43, "fffee", True), 50: (43, "mmmmmm", True),
        51: (43, "mmmmmm", True),
    }
    for y, (x0, t, c) in rows.items():
        r[y] = [ligne(y, x0, t, c)]
    r[52] = [ligne(52, 41, "oonnnnn", True)]
    r[53] = [ligne(53, 40, "onnnnnnnn", True)]
    r[54] = [ligne(54, 40, "onnnnnnnnn", True)]
    r[55] = [ligne(55, 40, "nnnnnnnnnn", True)]
    r[56] = [ligne(56, 41, "nnnnnnnn", True)]
    r[57] = [ligne(57, 41, "nnnnnnn", True)]
    r[58] = [ligne(58, 42, "nnnnn", True)]
    r[53] = r[53] + [(39, "n")]                  # pouce
    r[54] = r[54] + [(39, "n")]
    r[59] = [ligne(59, 42, "#####")]
    return r


def calque_jambes():
    """Deux jambes épaisses qui s'affinent vers les bottes, genoux arrondis, vide de 3 px entre elles,
    plaques de genouillère collées."""
    r = {}
    gauche = {51: (15, "ffffeeeee"), 52: (15, "ffffeeeee"), 53: (15, "ffffeeeee"), 54: (15, "ffffeeeee"),
              55: (15, "ffffeeeee"), 56: (14, "fffffeeeeee"), 57: (14, "fffffeeeeee"), 58: (14, "fffffeeeeee"),
              59: (16, "ffffeeeee"), 60: (16, "ffffeeeee"), 61: (16, "fffeeeee"), 62: (17, "fffeeee")}
    droite = {51: (28, "ffffeeeee"), 52: (28, "ffffeeeee"), 53: (28, "ffffeeeee"), 54: (28, "ffffeeeee"),
              55: (28, "ffffeeeee"), 56: (27, "fffffeeeeee"), 57: (27, "fffffeeeeee"), 58: (27, "fffffeeeeee"),
              59: (28, "ffffeeeee"), 60: (28, "ffffeeeee"), 61: (28, "fffeeeee"), 62: (29, "fffeeee")}
    for y, (x0, t) in gauche.items():
        r.setdefault(y, []).append(ligne(y, x0, t, True))
    for y, (x0, t) in droite.items():
        r.setdefault(y, []).append(ligne(y, x0, t, True))
    r[56] = r[56] + [(17, "nnnn")]                 # genouillère gauche : reflet puis plaque
    r[57] = r[57] + [(17, "mmmmmm")]
    r[58] = r[58] + [(18, "mmmmm")]
    r[56] = r[56] + [(30, "nnnn")]                 # genouillère droite
    r[57] = r[57] + [(30, "mmmmmm")]
    r[58] = r[58] + [(31, "mmmmm")]
    return r


def calque_bottes():
    """Bottes lourdes et arrondies, haut de botte en manchette sombre, pied qui dépasse vers l'avant, semelle."""
    r = {}
    r[63] = [ligne(63, 14, "mmmmmmmmmm")]
    r[64] = [ligne(64, 13, "nnlllllllll")]
    r[65] = [ligne(65, 12, "nnlllllllllll", True)]
    r[66] = [ligne(66, 12, "lllllllllllll", True)]
    r[67] = [ligne(67, 12, "lllllllllllll", True)]
    r[68] = [ligne(68, 13, "lllllllllllll", True)]
    r[69] = [ligne(69, 14, "lllllllllll", True)]
    r[70] = [ligne(70, 14, "llllllllll", True)]
    r[71] = [ligne(71, 14, "##########")]
    r[63] = r[63] + [(28, "mmmmmmmmmm")]
    r[64] = r[64] + [(27, "nnlllllllllll")]
    r[65] = r[65] + [ligne(65, 27, "nnlllllllllllll", True)]
    r[66] = r[66] + [ligne(66, 27, "llllllllllllll", True)]
    r[67] = r[67] + [ligne(67, 27, "llllllllllllll", True)]
    r[68] = r[68] + [ligne(68, 27, "lllllllllllll", True)]
    r[69] = r[69] + [ligne(69, 28, "lllllllllll", True)]
    r[70] = r[70] + [ligne(70, 28, "llllllllll", True)]
    r[71] = r[71] + [(28, "##########")]
    return r


def calque_bouteille():
    """Bouteille : valve laiton 2 x 2, col étroit, épaule arrondie, corps large et légèrement renflé, base arrondie."""
    r = {}
    r[9] = [(7, "dc")]
    r[10] = [(7, "cc")]
    r[11] = [(7, "Bz#")]
    r[12] = [(6, "BAAz#")]
    r[13] = [(5, "BAAAAz#")]
    for y in range(14, 24):
        r[y] = [(4, "BAAAAAz#")]
    r[24] = [(4, "BAAAAz#")]
    r[25] = [(5, "BAAAAz#")]
    r[26] = [(5, "BAAAz#")]
    r[27] = [(6, "BAAz#")]
    r[28] = [(6, "zAz#")]
    r[29] = [(7, "zz#")]
    return r


def calque_corde():
    """Corde de 3 px : boucle au-dessus du casque (anneau régulier), descente courbe derrière le casque, puis
    départ vers la valve de la bouteille."""
    r = {}
    r[0] = [(27, "#########")]
    r[1] = [(25, "#qqqqqqqqq#")]
    r[2] = [(24, "#qqq"), (32, "qqq#")]
    r[3] = [(23, "#qqq"), (32, "qqq#")]
    r[4] = [(24, "#qq"), (33, "qq#")]
    r[5] = [(25, "#qq"), (33, "qq#")]
    r[6] = [(26, "#pq"), (33, "pq#")]
    r[7] = [(26, "#pp"), (34, "p#")]
    r[8] = [(26, "#p")]
    r[10] = [(9, "qqqqqqq")]
    r[11] = [(9, "qqqqq")]
    return r


def calque_casque():
    """Dôme laiton : clair en haut-gauche, moyen au centre, sombre à droite ; contour sombre à droite."""
    dome = {9: (22, 30), 10: (20, 32), 11: (18, 34), 12: (17, 35), 13: (16, 36), 14: (15, 37), 15: (15, 37),
            16: (14, 38), 17: (14, 38), 18: (14, 38), 19: (13, 39), 20: (13, 39), 21: (13, 39), 22: (13, 39),
            23: (13, 39), 24: (14, 38), 25: (14, 38), 26: (15, 37), 27: (15, 37), 28: (16, 36), 29: (17, 35),
            30: (18, 34)}
    r = {}
    for y, (g, d) in dome.items():
        n = d - g + 1
        clair = min(4, n // 4)
        fonce = min(4, n // 4)
        r[y] = [band(y, g, d, [("c", clair), ("b", n - clair - fonce), ("a", fonce)])]
    return r


def calque_lumiere_casque():
    """Passe 2 : arc clair de 2 px le long du bord haut-gauche du dôme (lumière haut-gauche), sans tache."""
    return {
        9: [(22, "dddddd")],
        10: [(20, "ddd")],
        11: [(19, "dd")],
        12: [(18, "dd")],
        13: [(17, "dd")],
        14: [(16, "dd")],
        15: [(16, "dd")],
        16: [(15, "dd")],
    }


def calque_hublot():
    """Hublot avant : anneau gris 2 px (w), vitre bleu-noir (s), reflet (u), deux barres de 1 px (x)."""
    return {
        15: [(18, "wwwww")],
        16: [(17, "wwwwwww")],
        17: [(16, "ww"), (18, "sssss"), (23, "ww")],
        18: [(15, "ww"), (17, "uusssss"), (24, "ww")],
        19: [(15, "ww"), (17, "uxssxss"), (24, "ww")],
        20: [(14, "ww"), (16, "ssxsssssss"[:9]), (25, "ww")],
        21: [(14, "ww"), (16, "sssxsssss"), (25, "ww")],
        22: [(14, "ww"), (16, "sssxsssss"), (25, "ww")],
        23: [(15, "ww"), (17, "sssxsss"), (24, "ww")],
        24: [(15, "ww"), (17, "sssxsss"), (24, "ww")],
        25: [(16, "ww"), (18, "sssss"), (23, "ww")],
        26: [(17, "wwwwwww")],
        27: [(18, "wwwww")],
    }


def calque_col():
    """Collerette laiton claire, 3 px de haut, sous le casque."""
    return {31: [band(31, 15, 37, [("c", 17), ("b", 6)])],
            32: [band(32, 11, 40, [("c", 14), ("b", 16)])],
            33: [band(33, 13, 41, [("b", 29)])]}


CALQUES = [calque_bras_lointain, calque_bouteille, calque_corde, calque_casque, calque_lumiere_casque,
           calque_hublot, calque_col, calque_torse, calque_zip_plis, calque_bras_proche, calque_jambes,
           calque_bottes]


def construire():
    grille = [["."] * W for _ in range(H)]
    for calque in CALQUES:
        for y, runs in calque().items():
            for x0, texte in runs:
                for i, c in enumerate(texte):
                    x = x0 + i
                    if 0 <= x < W and 0 <= y < H:
                        grille[y][x] = c
    return ["".join(l) for l in grille]


if __name__ == "__main__":
    passe = int(sys.argv[1])
    g = construire()
    assert all(len(l) == W for l in g) and len(g) == H
    open(f"carte_{passe}.txt", "w").write("\n".join(g) + "\n")
    print("ok", W, H)

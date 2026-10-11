#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
robot.py - robot de test de LES CLOCHES DE VAREKH (M2).

Il lance le jeu (bin/godot) dans l'écran virtuel et joue avec de VRAIES touches : les événements
passent par le serveur X (extension XTest), comme un vrai clavier. Il prend une capture de l'écran
à chaque étape (bin/capture-ecran) et lit l'état que le jeu écrit (argument --etat-robot).
Il écrit tests/robot_rapport.json. Il ne modifie ni le jeu ni les données.

Lancement (depuis la racine du projet) :  python3 tests/robot/robot.py
"""
import ctypes
import json
import os
import subprocess
import sys
import time
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent.parent
BIN = Path("/opt/outils-varekh/bin")
GODOT = str(BIN / "godot")
CAPTURE = str(BIN / "capture-ecran")
XVFB = str(BIN / "xvfb-demarrer")
ETAT = RACINE / "tests" / "robot_etat.json"
RAPPORT = RACINE / "tests" / "robot_rapport.json"
CAPTURES = RACINE / "shots" / "robot"
JOURNAL = RACINE / "tests" / "robot_godot.log"

ETAPES = ["demarrer_radeau", "plonger", "nager", "combattre", "oxygene", "lampe", "creuser", "poser", "ramasser",
          "fabriquer", "sortir_eau_radeau", "sauvegarder", "recharger"]

# ----------------------------------------------------------------- X11 / XTest : vrais événements
X11 = ctypes.cdll.LoadLibrary("libX11.so.6")
XTST = ctypes.cdll.LoadLibrary("libXtst.so.6")
X11.XOpenDisplay.restype = ctypes.c_void_p
X11.XOpenDisplay.argtypes = [ctypes.c_char_p]
X11.XStringToKeysym.restype = ctypes.c_ulong
X11.XStringToKeysym.argtypes = [ctypes.c_char_p]
X11.XKeysymToKeycode.restype = ctypes.c_ubyte
X11.XKeysymToKeycode.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
X11.XFlush.argtypes = [ctypes.c_void_p]
XTST.XTestFakeKeyEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_ulong]
XTST.XTestFakeMotionEvent.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_ulong]

AFFICHAGE = None
POSITION_SAUVEGARDEE = None


class Clavier:
    """Garde les touches tenues : on appuie et on relâche par différence, comme un vrai clavier."""

    def __init__(self):
        self.tenues = set()

    def tenir(self, touches):
        for t in self.tenues - set(touches):
            self._envoyer(t, False)
        for t in set(touches) - self.tenues:
            self._envoyer(t, True)
        self.tenues = set(touches)
        X11.XFlush(AFFICHAGE)

    def relacher(self):
        self.tenir([])

    def frapper(self, touche, duree=0.08):
        self.tenir([touche])
        time.sleep(duree)
        self.tenir([])

    def _envoyer(self, touche, appui):
        code = X11.XKeysymToKeycode(AFFICHAGE, X11.XStringToKeysym(touche.encode()))
        if code == 0:
            raise RuntimeError(f"touche inconnue : {touche}")
        XTST.XTestFakeKeyEvent(AFFICHAGE, code, 1 if appui else 0, 0)


CLAVIER = Clavier()


def souris_dans_le_jeu():
    XTST.XTestFakeMotionEvent(AFFICHAGE, -1, 640, 360, 0)
    X11.XFlush(AFFICHAGE)


# ----------------------------------------------------------------- lecture de l'état du jeu
def etat():
    for _ in range(20):
        try:
            return json.loads(ETAT.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            time.sleep(0.05)
    raise RuntimeError("état du jeu illisible (le jeu tourne-t-il ?)")


def attendre(condition, delai, pas=0.05):
    fin = time.time() + delai
    while time.time() < fin:
        try:
            if condition(etat()):
                return True
        except (KeyError, IndexError, TypeError, RuntimeError):
            pass
        time.sleep(pas)
    return False


def inventaire_de(item):
    return int(etat()["inventaire"].get(item, 0))


def attendre_inventaire(item, avant, delai=3.0):
    return attendre(lambda e: int(e["inventaire"].get(item, 0)) > avant, delai)


def capture(nom):
    CAPTURES.mkdir(parents=True, exist_ok=True)
    chemin = CAPTURES / f"{nom}.png"
    if chemin.exists():
        chemin.unlink()
    subprocess.run([CAPTURE, str(chemin)], check=True, capture_output=True)
    return str(chemin.relative_to(RACINE))


# ----------------------------------------------------------------- déplacements
def aller_vers(x, y, tolerance=5, delai=30.0):
    """Navigue jusqu'au point (x, y) en pixels-monde, en lisant la position du jeu."""
    fin = time.time() + delai
    while time.time() < fin:
        px, py = etat()["position"]
        dx, dy = x - px, y - py
        if abs(dx) <= tolerance and abs(dy) <= tolerance:
            CLAVIER.relacher()
            return True
        touches = []
        if dx < -tolerance:
            touches.append("a")
        if dx > tolerance:
            touches.append("d")
        if dy < -tolerance:
            touches.append("w")
        if dy > tolerance:
            touches.append("s")
        CLAVIER.tenir(touches)
        time.sleep(0.05)
    CLAVIER.relacher()
    return False


def approcher(cible, portee=18.0, delai=6.0):
    """Suit une créature qui bouge, avec les vraies touches, jusqu'à une distance réelle (euclidienne) de
    `portee` px. La position de la cible et du plongeur est relue à chaque pas. La portée du jeu est de 26 px,
    donc 18 px laisse de la marge. Renvoie True dès que la distance est atteinte."""
    fin = time.time() + delai
    while time.time() < fin:
        c = cible()
        if c is None:
            break
        px, py = etat()["position"]
        dx, dy = c["x"] - px, c["y"] - py
        if (dx * dx + dy * dy) ** 0.5 <= portee:
            CLAVIER.relacher()
            return True
        touches = []
        if dx < -4:
            touches.append("a")
        if dx > 4:
            touches.append("d")
        if dy < -4:
            touches.append("w")
        if dy > 4:
            touches.append("s")
        CLAVIER.tenir(touches)
        time.sleep(0.05)
    CLAVIER.relacher()
    return False


def cellule_vers_px(cx, cy):
    return cx * 16 + 8, cy * 16 + 8


def viser(cx, cy, essais=6):
    """Place le plongeur à droite de la case (cx, cy) et le fait regarder à gauche. Vérifié dans l'état du
    jeu (case visée exacte) ; après chaque déplacement on attend que l'élan dans l'eau retombe."""
    x, y = cellule_vers_px(cx + 1, cy)
    for _ in range(essais):
        if not aller_vers(x, y):
            continue
        CLAVIER.frapper("a", 0.04)
        time.sleep(0.6)
        e = etat()
        if e["case_visee"] == [cx, cy] and e["regarde"] == -1:
            return True
    return False


def creuser_tuile(cx, cy):
    if not viser(cx, cy):
        return False
    avant = int(etat()["tuiles_modifiees"])
    CLAVIER.tenir(["e"])
    ok = attendre(lambda e: int(e["tuiles_modifiees"]) > avant, 4.0)
    CLAVIER.relacher()
    time.sleep(0.2)
    return ok


def ramasser_objet(objet):
    """Va jusqu'à l'objet au sol le plus proche (position donnée par le jeu), puis appuie sur R."""
    avant = inventaire_de(objet)
    sol = [o for o in etat()["objets_sol"] if o[2] == objet]
    if sol:
        px, py = etat()["position"]
        x, y, _ = min(sol, key=lambda o: (o[0] - px) ** 2 + (o[1] - py) ** 2)
        # On se place à côté de l'objet, dans l'eau libre (la case creusée peut être bordée de solide) :
        # la portée de ramassage du jeu est de 28 px, on reste à 16 px.
        aller_vers(x + 16, y, tolerance=6, delai=8.0)
        time.sleep(0.6)
    CLAVIER.frapper("r", 0.1)
    return attendre_inventaire(objet, avant, 2.0)


def revenir_sous_l_eau():
    """Si le plongeur est remonté sur le radeau, il replonge comme à l'étape « plonger » (marche vers la droite)."""
    if etat()["dans_eau"] is True:
        return True
    CLAVIER.tenir(["d"])
    time.sleep(1.2)
    CLAVIER.relacher()
    return attendre(lambda e: e["dans_eau"] is True, 4.0)


# ----------------------------------------------------------------- scénario
def scenario(rapport):
    def etape(nom, fonction):
        try:
            ok, detail = fonction()
        except Exception as e:  # noqa: BLE001 - tout échec est consigné, jamais caché
            ok, detail = False, f"exception : {e}"
        capture_nom = None
        try:
            capture_nom = capture(nom)
        except Exception as e:  # noqa: BLE001
            detail += f" ; capture impossible : {e}"
            ok = False
        rapport["etapes"].append({"nom": nom, "ok": bool(ok), "capture": capture_nom, "detail": detail})
        ecrire_rapport(rapport)
        print(("OK " if ok else "ECHEC ") + nom + " : " + detail, flush=True)
        return ok

    if not etape("demarrer_radeau", lambda: (etat()["sur_radeau"] is True, "le plongeur est sur le radeau")):
        return
    CLAVIER.frapper("d", 0.1)

    def plonger():
        CLAVIER.tenir(["d"])
        time.sleep(1.2)
        CLAVIER.relacher()
        ok = attendre(lambda e: e["dans_eau"] is True, 4.0)
        return ok, f"le plongeur est entré dans l'eau en {etat()['position']}"
    if not etape("plonger", plonger):
        return

    def nager():
        x0, y0 = etat()["position"]
        CLAVIER.tenir(["s"])
        time.sleep(0.8)
        CLAVIER.tenir(["a"])
        time.sleep(1.2)
        CLAVIER.relacher()
        x1, y1 = etat()["position"]
        dist = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
        return dist >= 40 and etat()["dans_eau"] is True, f"déplacement de {dist:.0f} px dans l'eau"
    if not etape("nager", nager):
        return

    def combattre():
        # Le poisson volant du radeau : le robot le suit avec les vraies touches jusqu'à 18 px (distance réelle),
        # puis frappe avec X jusqu'à ce qu'il meure (3 coups). L'état écrit par le jeu donne sa position et sa vie.
        def poisson():
            return next((c for c in etat().get("creatures", []) if c["id"] == "poisson_volant"), None)

        def cible():
            c = poisson()
            return c if c is not None and not c["morte"] else None
        if cible() is None:
            return False, "aucune créature poisson_volant vivante dans l'état du jeu"
        depart_combat = etat()["position"]     # le robot revient ici : les étapes suivantes en dépendent
        coups = 0
        essais = 0
        while cible() is not None and essais < 24:
            essais += 1
            if not approcher(cible, portee=18.0, delai=6.0):
                continue                        # la créature a bougé pendant l'approche : on la rattrape
            CLAVIER.frapper("x", 0.1)
            coups += 1
            time.sleep(0.6)
        # la créature morte reste dans l'état deux secondes avant de disparaître
        ok = attendre(lambda e: any(c["id"] == "poisson_volant" and c["morte"] is True
                                    for c in e.get("creatures", [])), 2.0)
        aller_vers(depart_combat[0], depart_combat[1], tolerance=12, delai=15.0)
        return ok, (f"poisson_volant {'morte' if ok else 'toujours vivante'} après {coups} coups "
                    f"({essais} approches) ; retour à {depart_combat}")
    etape("combattre", combattre)

    def oxygene():
        o0 = float(etat()["oxygene"])
        CLAVIER.tenir(["s"])
        time.sleep(2.5)
        CLAVIER.relacher()
        o1 = float(etat()["oxygene"])
        return o1 < o0 - 1.5, f"air : {o0:.1f} -> {o1:.1f} sur {etat()['oxygene_max']}"
    if not etape("oxygene", oxygene):
        return

    def lampe():
        CLAVIER.frapper("l", 0.1)
        ok = attendre(lambda e: e["lampe"] is True, 2.0)
        return ok, "la lampe frontale est allumée"
    if not etape("lampe", lampe):
        return

    # L'épave : planches aux rangées 18 et 19, colonne de tôle en x = -16 à -14, y = 20 à 25.
    def creuser():
        ok = creuser_tuile(-14, 19)
        return ok, "une case de planche creusée (un morceau tombe au sol)"
    if not etape("creuser", creuser):
        return

    def ramasser():
        ok = ramasser_objet("planche_epave")
        return ok, f"planche_epave dans l'inventaire : {inventaire_de('planche_epave')}"
    if not etape("ramasser", ramasser):
        return

    # Récolte du reste pour la forge : une planche de plus, quatre morceaux de tôle.
    for cx, cy, objet in ((-14, 18, "planche_epave"), (-14, 20, "tole_rouillee"), (-14, 21, "tole_rouillee"),
                          (-14, 22, "tole_rouillee"), (-14, 23, "tole_rouillee")):
        # le plongeur peut remonter sur le radeau pendant une manœuvre : il replonge, puis on réessaie la case
        for _ in range(3):
            if revenir_sous_l_eau() and creuser_tuile(cx, cy):
                break
        else:
            e = etat()
            raise RuntimeError(f"la case {cx},{cy} ne se creuse pas (position {e['position']}, "
                               f"case visée {e['case_visee']}, regarde {e['regarde']})")
        for _ in range(3):                      # un ramassage peut rater si le plongeur dérive : on réessaie
            if ramasser_objet(objet):
                break

    def poser():
        if inventaire_de("tole_rouillee") < 1:
            return False, "pas de tôle à poser"
        idx = etat()["barre"].index("tole_rouillee")
        CLAVIER.frapper(str(idx + 1), 0.08)
        if not viser(-14, 23):
            return False, "impossible de viser la case vide"
        avant = int(etat()["poses"])
        CLAVIER.frapper("f", 0.15)
        ok = attendre(lambda e: int(e["poses"]) > avant, 2.0)
        return ok, f"poses : {avant} -> {etat()['poses']} ; inventaire : {etat()['inventaire']}"
    if not etape("poser", poser):
        return

    def fabriquer():
        if not viser(-14, 22):
            return False, "impossible de se placer pour fabriquer"
        CLAVIER.frapper("c", 0.1)
        if not attendre(lambda e: e["panneau"] == "fabrication", 2.0):
            return False, "le panneau de fabrication ne s'ouvre pas"
        avant = inventaire_de("module_forge")
        CLAVIER.frapper("Return", 0.1)
        ok = attendre_inventaire("module_forge", avant, 2.0)
        inv = etat()["inventaire"]
        CLAVIER.frapper("c", 0.1)
        attendre(lambda e: e["panneau"] == "", 2.0)
        return ok, f"module de forge fabriqué (tôle et planches de l'épave) ; inventaire : {inv}"
    if not etape("fabriquer", fabriquer):
        return

    def sortir():
        # Le quai ne se franchit que d'en dessous : on remonte sous le radeau, puis on bondit près de la surface.
        # Trois tentatives, chacune avec une nouvelle approche (l'élan dans l'eau peut décaler le plongeur).
        for _ in range(3):
            if etat()["sur_radeau"]:
                return True, "le plongeur est sur le radeau"
            aller_vers(0, 40, tolerance=6, delai=20.0)
            time.sleep(0.4)
            CLAVIER.tenir(["w"])
            attendre(lambda e: e["position"][1] < 20 or e["sur_radeau"], 4.0, pas=0.02)
            CLAVIER.frapper("space", 0.06)
            CLAVIER.relacher()
            if attendre(lambda e: e["sur_radeau"] is True, 4.0):
                return True, f"le plongeur est monté sur le radeau (position {etat()['position']})"
        return False, f"le plongeur ne monte pas sur le radeau (position {etat()['position']})"
    if not etape("sortir_eau_radeau", sortir):
        return

    def sauvegarder():
        global POSITION_SAUVEGARDEE
        # on ne sauvegarde qu'une fois posé sur le radeau (pas en plein saut)
        attendre(lambda e: e["sur_radeau"] is True and abs(e["position"][1] + 24) < 3, 4.0)
        time.sleep(0.4)
        e = etat()
        POSITION_SAUVEGARDEE = e["position"]
        CLAVIER.frapper("F5", 0.1)
        chemin = Path(e["fichier_sauvegarde"])
        ok = attendre(lambda _: chemin.exists() and chemin.stat().st_size > 20, 3.0)
        return ok, f"sauvegarde écrite : {chemin}"
    if not etape("sauvegarder", sauvegarder):
        return

    def recharger():
        CLAVIER.tenir(["d"])
        time.sleep(0.8)
        CLAVIER.relacher()
        decale = etat()["position"]
        CLAVIER.frapper("F9", 0.1)
        ok = attendre(lambda e: abs(e["position"][0] - POSITION_SAUVEGARDEE[0]) < 3 and
                      abs(e["position"][1] - POSITION_SAUVEGARDEE[1]) < 3, 3.0)
        return ok, f"après déplacement {decale}, après F9 {etat()['position']}, sauvegardée {POSITION_SAUVEGARDEE}"
    etape("recharger", recharger)


def ecrire_rapport(rapport):
    RAPPORT.parent.mkdir(parents=True, exist_ok=True)
    RAPPORT.write_text(json.dumps(rapport, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    global AFFICHAGE
    rapport = {"etapes": []}
    for ancien in (RAPPORT, ETAT):
        if ancien.exists():
            ancien.unlink()
    sortie = subprocess.run([XVFB], capture_output=True, text=True, check=True).stdout
    display = [l.split("=", 1)[1].strip() for l in sortie.splitlines() if l.startswith("export DISPLAY=")][0]
    os.environ["DISPLAY"] = display
    AFFICHAGE = X11.XOpenDisplay(display.encode())
    if not AFFICHAGE:
        raise SystemExit("écran X inaccessible")
    print("écran :", display, flush=True)
    JOURNAL.parent.mkdir(parents=True, exist_ok=True)
    with open(JOURNAL, "w", encoding="utf-8") as journal:
        jeu = subprocess.Popen([GODOT, "--path", str(RACINE), "--", f"--etat-robot={ETAT}"],
                               stdout=journal, stderr=subprocess.STDOUT, cwd=str(RACINE))
        try:
            if not attendre(lambda e: e.get("pret") is True, 90):
                raise SystemExit("le jeu ne démarre pas (pas d'état)")
            souris_dans_le_jeu()
            time.sleep(0.5)
            scenario(rapport)
        finally:
            CLAVIER.relacher()
            jeu.terminate()
            try:
                jeu.wait(timeout=20)
            except subprocess.TimeoutExpired:
                jeu.kill()
    ecrire_rapport(rapport)
    reussi = len(rapport["etapes"]) == len(ETAPES) and all(e["ok"] for e in rapport["etapes"])
    print("ROBOT :", "SUCCES" if reussi else "ECHEC", f"({sum(e['ok'] for e in rapport['etapes'])}/{len(ETAPES)})")
    return 0 if reussi else 1


if __name__ == "__main__":
    sys.exit(main())

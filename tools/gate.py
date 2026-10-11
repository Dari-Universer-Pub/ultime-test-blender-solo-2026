#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gate.py - CONTROLE DE PHASE du projet LES CLOCHES DE VAREKH.

    python tools/gate.py M0      (ou M1 ... M6)

Une phase est terminee UNIQUEMENT quand ce script affiche "SUCCES" pour elle.
Chaque phase reverifie aussi toutes les phases precedentes (pas de regression).

CE FICHIER APPARTIENT A JULIEN. L'AGENT N'A PAS LE DROIT DE LE MODIFIER, DE LE
COPIER SOUS UN AUTRE NOM POUR LE CONTOURNER, NI D'EN AFFAIBLIR UN SEUIL.
Son empreinte SHA-256 est affichee a chaque execution et verifiee a l'audit.

Bibliotheque standard Python uniquement (aucune dependance).
"""
import hashlib
import json
import math
import os
import platform
import re
import shutil
import struct
import subprocess
import sys
import time
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PHASES = ["M0", "M1", "M2", "M3", "M4", "M5", "M6"]

# ----------------------------------------------------------------- resultats
ERREURS = []
OKS = []
AVERTS = []


def ko(msg):
    ERREURS.append(msg)


def ok(msg):
    OKS.append(msg)


def avert(msg):
    AVERTS.append(msg)


def rel(p):
    try:
        return str(Path(p).resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(p)


def fichier(relpath):
    """Chemin absolu d'un chemin relatif au projet (accepte / et \\)."""
    if relpath is None:
        return None
    return ROOT / str(relpath).replace("\\", "/")


def charger_json(relpath, obligatoire=True):
    p = fichier(relpath)
    if not p.exists():
        if obligatoire:
            ko(f"{relpath} : fichier absent")
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:  # noqa
        ko(f"{relpath} : JSON invalide ({e})")
        return None


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()


# ------------------------------------------------------------- lecture PNG
class Image:
    def __init__(self, w, h, px):
        self.w, self.h, self.px = w, h, px  # px : liste de tuples RGBA

    def pixel(self, x, y):
        return self.px[y * self.w + x]


def lire_png(p):
    """Decodeur PNG minimal (8 bits, non entrelace). Renvoie Image ou leve ValueError."""
    data = Path(p).read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("pas un PNG")
    pos, idat, plte, trns = 8, b"", None, None
    w = h = prof = typ = entrelace = None
    while pos < len(data):
        n = struct.unpack(">I", data[pos:pos + 4])[0]
        t = data[pos + 4:pos + 8]
        c = data[pos + 8:pos + 8 + n]
        pos += 12 + n
        if t == b"IHDR":
            w, h, prof, typ, _, _, entrelace = struct.unpack(">IIBBBBB", c)
        elif t == b"PLTE":
            plte = c
        elif t == b"tRNS":
            trns = c
        elif t == b"IDAT":
            idat += c
        elif t == b"IEND":
            break
    if prof != 8:
        raise ValueError(f"profondeur {prof} bits non geree (exporter en 8 bits)")
    if entrelace:
        raise ValueError("PNG entrelace non gere (reexporter sans entrelacement)")
    canaux = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}.get(typ)
    if canaux is None:
        raise ValueError(f"type de couleur {typ} non gere")
    brut = zlib.decompress(idat)
    bpp = canaux
    pas = w * bpp
    lignes, prec, i = [], bytearray(pas), 0
    for _ in range(h):
        f = brut[i]
        ligne = bytearray(brut[i + 1:i + 1 + pas])
        i += 1 + pas
        if f == 1:
            for x in range(bpp, pas):
                ligne[x] = (ligne[x] + ligne[x - bpp]) & 255
        elif f == 2:
            for x in range(pas):
                ligne[x] = (ligne[x] + prec[x]) & 255
        elif f == 3:
            for x in range(pas):
                a = ligne[x - bpp] if x >= bpp else 0
                ligne[x] = (ligne[x] + ((a + prec[x]) >> 1)) & 255
        elif f == 4:
            for x in range(pas):
                a = ligne[x - bpp] if x >= bpp else 0
                b = prec[x]
                c = prec[x - bpp] if x >= bpp else 0
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                ligne[x] = (ligne[x] + pr) & 255
        lignes.append(bytes(ligne))
        prec = ligne
    px = []
    for ligne in lignes:
        if typ == 6:
            px.extend(tuple(ligne[k:k + 4]) for k in range(0, pas, 4))
        elif typ == 2:
            px.extend((ligne[k], ligne[k + 1], ligne[k + 2], 255) for k in range(0, pas, 3))
        elif typ == 0:
            px.extend((v, v, v, 255) for v in ligne)
        elif typ == 4:
            px.extend((ligne[k], ligne[k], ligne[k], ligne[k + 1]) for k in range(0, pas, 2))
        elif typ == 3:
            for v in ligne:
                r, g, b = plte[3 * v:3 * v + 3]
                a = trns[v] if (trns is not None and v < len(trns)) else 255
                px.append((r, g, b, a))
    return Image(w, h, px)


def png_valide(relpath, quoi, min_opaque=0.01, uniforme_max=0.95):
    """Verifie qu'un PNG existe, se lit, n'est pas vide ni uniforme. Renvoie Image ou None."""
    p = fichier(relpath)
    if not relpath or not p.exists():
        ko(f"{quoi} : fichier absent ({relpath})")
        return None
    try:
        img = lire_png(p)
    except Exception as e:  # noqa
        ko(f"{quoi} : PNG illisible {relpath} ({e})")
        return None
    opaques = [q for q in img.px if q[3] > 0]
    if len(opaques) < min_opaque * len(img.px):
        ko(f"{quoi} : image vide ou presque transparente ({relpath})")
        return None
    compte = {}
    for q in opaques:
        compte[q[:3]] = compte.get(q[:3], 0) + 1
    if max(compte.values()) > uniforme_max * len(opaques):
        ko(f"{quoi} : image uniforme a plus de {int(uniforme_max*100)} % d'une seule couleur "
           f"(ecran noir ou rendu rate ?) ({relpath})")
        return None
    return img


def luminance(rgb):
    def lin(c):
        c /= 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = rgb
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def hex_rgb(s):
    s = s.strip().lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def teinte(rgb):
    r, g, b = [c / 255.0 for c in rgb]
    mx, mn = max(r, g, b), min(r, g, b)
    if mx == mn:
        return None
    d = mx - mn
    if mx == r:
        hh = ((g - b) / d) % 6
    elif mx == g:
        hh = (b - r) / d + 2
    else:
        hh = (r - g) / d + 4
    return hh * 60.0


# --------------------------------------------------------------- outils
def outils():
    return charger_json("tools/outils.json") or {}


def en_wsl():
    return platform.system() == "Linux" and "microsoft" in platform.release().lower()


def chemin_pour_exe(chemin_projet, exe):
    """Godot/Blender Windows lances depuis WSL veulent un chemin Windows."""
    if platform.system() == "Linux" and str(exe).lower().endswith(".exe"):
        try:
            return subprocess.check_output(["wslpath", "-w", str(chemin_projet)], text=True).strip()
        except Exception:  # noqa
            return str(chemin_projet)
    return str(chemin_projet)


def adapter_cmd(cmd):
    """Adapte une commande decrite dans outils.json a la plateforme courante."""
    cmd = list(cmd)
    sysname = platform.system()
    if sysname == "Linux":
        if cmd and cmd[0].lower() in ("wsl", "wsl.exe"):
            # depuis WSL on rappelle wsl.exe (interop) : garde l'utilisateur root demande
            cmd[0] = "wsl.exe" if shutil.which("wsl.exe") else cmd[0]
            if cmd[0] == "wsl":
                cmd = cmd[cmd.index("-e") + 1:] if "-e" in cmd else cmd[-1:]
        if cmd and re.match(r"^[A-Za-z]:\\", cmd[0]):
            d = cmd[0][0].lower()
            cmd[0] = f"/mnt/{d}/" + cmd[0][3:].replace("\\", "/")
    elif sysname == "Windows":
        if cmd and cmd[0].startswith("/"):
            cmd = ["wsl", "-d", "Ubuntu", "-u", "root", "-e"] + cmd
    return cmd


def lancer(cmd, timeout=180, cwd=None):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                           cwd=cwd or ROOT, errors="replace")
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except (FileNotFoundError, PermissionError, OSError) as e:
        return 127, f"commande impossible a lancer : {cmd[0]} ({e})"
    except subprocess.TimeoutExpired:
        return 124, f"delai depasse ({timeout} s)"


def verifier_outils():
    o = outils()
    for nom in ("godot", "blender", "aseprite"):
        if nom not in o:
            ko(f"tools/outils.json : cle '{nom}' absente")
            continue
        cmd = adapter_cmd(o[nom]) + ["--version"]
        if nom == "aseprite":
            cmd = adapter_cmd(o[nom]) + ["--batch", "--version"]
        code, sortie = lancer(cmd, timeout=120)
        if code != 0 or not re.search(r"\d+\.\d+", sortie):
            ko(f"outil {nom} : '{' '.join(cmd)}' a echoue (code {code}) : {sortie.strip()[:200]}")
        else:
            ok(f"outil {nom} : {sortie.strip().splitlines()[0][:80]}")


def verifier_godot():
    o = outils()
    if "godot" not in o:
        return
    exe = adapter_cmd(o["godot"])
    projet = chemin_pour_exe(ROOT, exe[-1])
    code, sortie = lancer(exe + ["--headless", "--path", projet, "--quit"], timeout=300)
    erreurs = re.findall(r"(SCRIPT ERROR|Parse Error|ERROR: Failed to load|Failed loading resource)[^\n]*", sortie)
    if code != 0 or erreurs:
        ko(f"Godot : le projet ne se charge pas proprement (code {code}) : "
           f"{'; '.join(erreurs[:5]) or sortie.strip()[-300:]}")
    else:
        ok("Godot : projet charge sans erreur de script")


# ------------------------------------------------------- dessin par code
MOTIFS_INTERDITS = [
    (r"putpixel\s*\(", "putpixel (dessin pixel par pixel)"),
    (r"\.(line|rectangle|rounded_rectangle|ellipse|polygon|point|arc|pieslice|chord|regular_polygon)\s*\(",
     "primitive ImageDraw (dessin par code)"),
]


def verifier_dessin_par_code():
    exts = {".py", ".gd", ".js", ".ts", ".sh", ".ps1", ".bat", ".cs"}
    for p in ROOT.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in exts:
            continue
        r = rel(p)
        if r.startswith((".git/", "assets/sources/", ".godot/")) or r == "tools/gate.py":
            continue
        try:
            txt = p.read_text(encoding="utf-8", errors="replace")
        except Exception:  # noqa
            continue
        dans_mesure = r.startswith(("tools/mesure/", "tools/pixelisation/", "tests/robot/"))
        dans_planches = r.startswith("tools/planches/")
        if p.suffix == ".py":
            if re.search(r"\b(import\s+PIL|from\s+PIL|import\s+numpy|from\s+numpy|import\s+cv2|from\s+skimage)", txt):
                if not (dans_mesure or dans_planches):
                    ko(f"{r} : Pillow/numpy/OpenCV hors de tools/mesure/, tools/pixelisation/, tools/planches/ ou tests/robot/ (interdit)")
            if "ImageDraw" in txt:
                for motif, quoi in MOTIFS_INTERDITS[1:]:
                    if re.search(motif, txt):
                        ko(f"{r} : {quoi} interdite")
            if re.search(MOTIFS_INTERDITS[0][0], txt):
                ko(f"{r} : {MOTIFS_INTERDITS[0][1]} interdit")
            if re.search(r"Image\.(new|fromarray)\s*\(", txt) and not (dans_mesure or dans_planches):
                ko(f"{r} : creation d'image par code hors outils de mesure/planches (interdit)")
        if p.suffix == ".gd":
            if re.search(r"\bdraw_(rect|circle|polygon|colored_polygon|arc)\s*\(", txt):
                avert(f"{r} : draw_* dans un script Godot. Autorise pour une jauge d'interface, "
                      f"INTERDIT pour representer un personnage, une creature, un objet ou un decor")
    ok("recherche de dessin par code terminee")


# ------------------------------------------------------------ provenance
LICENCES_OK = {"CC0", "CC0-1.0", "CC-BY", "CC-BY-3.0", "CC-BY-4.0", "OFL", "OFL-1.1"}


def verifier_provenance():
    prov = charger_json("PROVENANCE.json")
    if prov is None:
        return {}
    sources = {}
    for s in prov.get("sources", []):
        sid = s.get("id")
        if not sid or sid in sources:
            ko(f"PROVENANCE.json : id manquant ou en double ({sid})")
            continue
        sources[sid] = s
        lic = str(s.get("licence", "")).upper().replace(" ", "-")
        if lic not in LICENCES_OK or re.search(r"\b(NC|ND|SA)\b", lic):
            ko(f"PROVENANCE {sid} : licence '{s.get('licence')}' refusee (CC0, CC-BY, OFL seulement)")
        if not str(s.get("url", "")).startswith("http"):
            ko(f"PROVENANCE {sid} : url absente")
        if s.get("type") not in ("modele3d", "pack2d", "son", "musique", "police"):
            ko(f"PROVENANCE {sid} : type '{s.get('type')}' invalide")
        f = fichier(s.get("fichier"))
        if not f or not f.exists():
            ko(f"PROVENANCE {sid} : fichier telecharge absent ({s.get('fichier')})")
        elif str(s.get("sha256", "")).lower() != sha256(f):
            ko(f"PROVENANCE {sid} : SHA-256 faux pour {s.get('fichier')}")
        pl = fichier(s.get("page_licence"))
        if not pl or not pl.exists():
            ko(f"PROVENANCE {sid} : copie de la page de licence absente ({s.get('page_licence')})")
    ok(f"provenance : {len(sources)} sources lues")
    return sources


# ----------------------------------------------------------------- palette
def verifier_palette():
    pal = charger_json("art/palette.json")
    if not pal:
        return set()
    rampes = pal.get("rampes", {})
    couleurs = set()
    for nom, tons in rampes.items():
        rgb = [hex_rgb(t) for t in tons]
        couleurs.update(rgb)
        if not 5 <= len(rgb) <= 7:
            ko(f"palette : rampe '{nom}' a {len(rgb)} tons (5 a 7 demandes)")
        hs = [teinte(c) for c in rgb if teinte(c) is not None]
        if len(hs) >= 2:
            d = abs(hs[0] - hs[-1]) % 360
            d = min(d, 360 - d)
            if d < 15:
                ko(f"palette : rampe '{nom}' : decalage de teinte {d:.0f} deg (< 15)")
    if not 64 <= len(couleurs) <= 96:
        ko(f"palette : {len(couleurs)} couleurs (64 a 96 demandees)")
    if (0, 0, 0) in couleurs:
        ko("palette : noir pur interdit")
    ok(f"palette : {len(couleurs)} couleurs, {len(rampes)} rampes")
    return couleurs


# ------------------------------------------------------------------- sprites
def frames_aseprite(meta):
    """Renvoie (liste de rectangles, dict tag -> (from, to))."""
    fr = meta.get("frames", [])
    if isinstance(fr, dict):
        fr = list(fr.values())
    rects = [(f["frame"]["x"], f["frame"]["y"], f["frame"]["w"], f["frame"]["h"]) for f in fr]
    tags = {t["name"].lower(): (t["from"], t["to"]) for t in meta.get("meta", {}).get("frameTags", [])}
    return rects, tags


def empreinte_frame(img, r):
    x0, y0, w, h = r
    h_ = hashlib.md5()
    for y in range(y0, min(y0 + h, img.h)):
        for x in range(x0, min(x0 + w, img.w)):
            h_.update(bytes(img.pixel(x, y)))
    return h_.hexdigest()


def pixels_isoles(img, r):
    x0, y0, w, h = r
    n, total = 0, 0
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            if img.pixel(x, y)[3] == 0:
                continue
            total += 1
            voisin = False
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dx == dy == 0:
                        continue
                    xx, yy = x + dx, y + dy
                    if x0 <= xx < x0 + w and y0 <= yy < y0 + h and img.pixel(xx, yy)[3] > 0:
                        voisin = True
                        break
                if voisin:
                    break
            if not voisin:
                n += 1
    return n, total


EXIGENCES_TAGS = {
    "plongeur_M0": {"nage": 8, "idle": 6},
    "plongeur": {"nage": 8, "idle": 6, "creusage": 6, "attaque": 6, "saut": 4, "degats": 3, "mort": 8},
    "creature": {"nage": 8, "attaque": 4, "mort": 6},
    "boss": {"attaque": 4, "mort": 6},
}


def verifier_sprite(s, palette, sources, exig_tags=None):
    sid = s.get("id", "?")
    quoi = f"sprite {sid}"
    typ, fil = s.get("type"), s.get("filiere")
    if typ not in ("vivant", "objet", "prop", "tuileset", "fond", "effet", "icone", "interface"):
        ko(f"{quoi} : type '{typ}' invalide")
    if fil not in ("3d", "construit", "aseprite", "pack2d"):
        ko(f"{quoi} : filiere '{fil}' invalide")
    if typ == "vivant" and fil != "construit":
        ko(f"{quoi} : un etre vivant doit etre construit par toi dans Blender (filiere construit), aucun modele telecharge")
    if fil == "pack2d":
        ko(f"{quoi} : filiere pack2d interdite : aucun pack telecharge, tu fais tout dans Blender ou Aseprite")
    if fil == "3d":
        ko(f"{quoi} : filiere 3d interdite : aucun modele 3D telecharge, tu construis tout toi-meme dans Blender")
    if fil == "construit":   # construit de zero par l'agent : son script Blender decrit tout l'asset
        sc = fichier(s.get("script"))
        if not sc or not sc.exists() or sc.suffix != ".py":
            ko(f"{quoi} : filiere construit : script Blender absent (cle \"script\" : art/source/blender/<id>.py) ({s.get('script')})")
        for x in s.get("sources", []):
            if x not in sources:
                ko(f"{quoi} : source '{x}' absente de PROVENANCE.json")
    if fil in ("3d", "pack2d"):
        srcs = s.get("sources", [])
        if not srcs:
            ko(f"{quoi} : aucune source telechargee citee")
        for x in srcs:
            if x not in sources:
                ko(f"{quoi} : source '{x}' absente de PROVENANCE.json")
            elif fil == "3d" and sources[x].get("type") != "modele3d":
                ko(f"{quoi} : la source '{x}' n'est pas un modele 3D")
    if fil in ("3d", "construit"):
        b = fichier(s.get("blend"))
        if not b or not b.exists():
            ko(f"{quoi} : fichier .blend absent ({s.get('blend')})")
        pl = s.get("planches", {})
        png_valide(pl.get("base"), f"{quoi} planche base 3D brute")
        png_valide(pl.get("modifie"), f"{quoi} planche version modifiee")
    a = fichier(s.get("aseprite"))
    if not a or not a.exists():
        ko(f"{quoi} : source .aseprite absente ({s.get('aseprite')})")
    if typ == "vivant":
        its = s.get("planches", {}).get("iterations", [])
        if len(its) < 3:
            ko(f"{quoi} : {len(its)} planche(s) d'iteration Aseprite (3 minimum)")
        empreintes = set()
        for it in its:
            if png_valide(it, f"{quoi} iteration") is not None:
                empreintes.add(sha256(fichier(it)))
        if its and len(empreintes) < len(its):
            ko(f"{quoi} : planches d'iteration identiques ({len(empreintes)} differentes sur {len(its)}) : "
               f"chaque iteration doit montrer une vraie correction")
    img = png_valide(s.get("sheet"), f"{quoi} feuille de sprites")
    meta = charger_json(s.get("data"), obligatoire=True) if s.get("data") else None
    if s.get("data") is None:
        ko(f"{quoi} : export JSON Aseprite (data) absent")
    if img is None:
        return
    # palette
    if palette:
        hors, opq = 0, 0
        for q in img.px:
            if q[3] == 0:
                continue
            opq += 1
            if q[:3] not in palette or q[3] != 255:
                hors += 1
        if opq and hors > 0.005 * opq:
            ko(f"{quoi} : {hors} pixels hors palette ou semi-transparents "
               f"({100*hors/opq:.1f} %) : quantifier a la palette du projet")
    if meta is None:
        return
    rects, tags = frames_aseprite(meta)
    if not rects:
        ko(f"{quoi} : aucune image dans l'export JSON")
        return
    if typ == "tuileset" and len(rects) < 47:
        ko(f"{quoi} : {len(rects)} tuiles (autotile 47 minimum)")
    for tag, mini in (exig_tags or {}).items():
        if tag not in tags:
            ko(f"{quoi} : animation '{tag}' absente (tags : {', '.join(tags) or 'aucun'})")
            continue
        a_, b_ = tags[tag]
        if a_ < 0 or b_ >= len(rects) or a_ > b_:
            ko(f"{quoi} : animation '{tag}' pointe vers les images {a_}-{b_} alors que la feuille en a "
               f"{len(rects)} (numerotees 0 a {len(rects)-1})")
            continue
        n = b_ - a_ + 1
        if n < mini:
            ko(f"{quoi} : animation '{tag}' a {n} images ({mini} minimum)")
            continue
        distinctes = len({empreinte_frame(img, rects[i]) for i in range(a_, b_ + 1) if i < len(rects)})
        if distinctes < math.ceil(0.75 * n):
            ko(f"{quoi} : animation '{tag}' : seulement {distinctes} images differentes sur {n}")
    if typ == "vivant":
        tot_iso = tot = 0
        for r in rects[:24]:
            i_, t_ = pixels_isoles(img, r)
            tot_iso += i_
            tot += t_
        if tot and tot_iso / max(1, min(len(rects), 24)) > 3:
            ko(f"{quoi} : {tot_iso} pixels isoles sur {min(len(rects),24)} images (moyenne > 3 par image)")
        verifier_lisibilite(img, rects, s, quoi)
        verifier_journal(s, quoi)


def boite(img, r):
    x0, y0, w, h = r
    ys = [y for y in range(y0, min(y0 + h, img.h)) for x in range(x0, min(x0 + w, img.w))
          if img.pixel(x, y)[3] > 0]
    xs = [x for y in range(y0, min(y0 + h, img.h)) for x in range(x0, min(x0 + w, img.w))
          if img.pixel(x, y)[3] > 0]
    if not ys:
        return 0, 0
    return max(xs) - min(xs) + 1, max(ys) - min(ys) + 1


HAUTEUR_PLONGEUR = (28, 48)   # pixels, dans le sprite final
REMPLISSAGE_MIN = 0.55        # hauteur du personnage / hauteur de la case
SATURATION_MIN = 0.12         # saturation moyenne (un rendu gris est refuse)
COULEURS_MIN = 8              # couleurs differentes dans le sprite


def verifier_lisibilite(img, rects, s, quoi):
    """Refuse les defauts visibles mesurables : sprite minuscule dans sa case,
    personnage trop petit ou trop grand, rendu gris, sprite pauvre en couleurs."""
    hauteurs, remplis = [], []
    for r in rects[:24]:
        _, hh = boite(img, r)
        if hh:
            hauteurs.append(hh)
            remplis.append(hh / r[3])
    if not hauteurs:
        ko(f"{quoi} : toutes les images sont vides")
        return
    if max(remplis) < REMPLISSAGE_MIN:
        ko(f"{quoi} : le personnage n'occupe que {max(remplis)*100:.0f} % de la hauteur de sa case "
           f"({REMPLISSAGE_MIN*100:.0f} % minimum) : cadrage a refaire ou case a reduire")
    if str(s.get("data_id", "")).startswith("plongeur"):
        hmin, hmax = HAUTEUR_PLONGEUR
        if not hmin <= max(hauteurs) <= hmax:
            ko(f"{quoi} : le plongeur mesure {max(hauteurs)} px de haut ({hmin} a {hmax} px attendus)")
    sats, couleurs = [], set()
    for q in img.px:
        if q[3] == 0:
            continue
        couleurs.add(q[:3])
        mx, mn = max(q[:3]), min(q[:3])
        sats.append(0 if mx == 0 else (mx - mn) / mx)
    if sats and sum(sats) / len(sats) < SATURATION_MIN:
        ko(f"{quoi} : rendu quasi gris (saturation moyenne {sum(sats)/len(sats):.2f} < {SATURATION_MIN}) : "
           f"les couleurs du modele de base ont ete perdues (Workbench : color_type TEXTURE ou MATERIAL)")
    if len(couleurs) < COULEURS_MIN:
        ko(f"{quoi} : seulement {len(couleurs)} couleurs dans le sprite ({COULEURS_MIN} minimum)")


CHAMPS_OEIL = ("silhouette", "couleurs", "cadrage", "taille", "details", "coherence_base", "pixels_parasites")
ENTREES_MIN = {"vivant": 6}


def verifier_journal(s, quoi):
    """Le journal visuel prouve que chaque changement a ete REGARDE : une image de
    comparaison par changement, un avis sur chaque critere, une decision."""
    chemin = f"art/journal/{s.get('id')}.json"
    j = charger_json(chemin, obligatoire=False)
    if j is None:
        ko(f"{quoi} : journal visuel {chemin} absent (une entree par changement regarde)")
        return
    entrees = j.get("entrees", [])
    mini = ENTREES_MIN.get(s.get("type"), 3)
    if len(entrees) < mini:
        ko(f"{quoi} : journal visuel avec {len(entrees)} entree(s) ({mini} minimum)")
    vues = set()
    for k, e in enumerate(entrees, 1):
        qe = f"{quoi} journal entree {k}"
        if not isinstance(e.get("changement"), str) or len(e["changement"]) < 15:
            ko(f"{qe} : 'changement' absent ou trop vague")
        im = e.get("image")
        f = fichier(im) if im else None
        if not f or not f.exists():
            ko(f"{qe} : image de comparaison absente ({im})")
            continue
        h = sha256(f)
        if str(e.get("image_sha256", "")).lower() != h:
            ko(f"{qe} : image_sha256 ne correspond pas a {im} (image remplacee apres coup ?)")
        if h in vues:
            ko(f"{qe} : meme image de comparaison qu'une entree precedente")
        vues.add(h)
        ctrl = e.get("controle", {})
        for c in CHAMPS_OEIL:
            v = ctrl.get(c)
            if not isinstance(v, str) or len(v.strip()) < 12:
                ko(f"{qe} : critere '{c}' non evalue (phrase precise attendue)")
        if e.get("verdict") not in ("garde", "annule"):
            ko(f"{qe} : verdict 'garde' ou 'annule' attendu")


def manifeste():
    m = charger_json("art/manifest.json")
    return (m or {}).get("sprites", [])


# ----------------------------------------------------------------- donnees
TEXTE_VIDE = re.compile(r"(TODO|TBD|lorem|a completer|à compléter|placeholder|\.\.\.$)", re.I)


def texte(obj, champ, mini, quoi):
    v = obj.get(champ)
    if not isinstance(v, str) or len(v.strip()) < mini:
        ko(f"{quoi} : champ '{champ}' absent ou trop court (< {mini} caracteres)")
        return False
    if TEXTE_VIDE.search(v):
        ko(f"{quoi} : champ '{champ}' contient un texte provisoire")
        return False
    return True


def liste(nom, cle, mini):
    d = charger_json(f"data/{nom}.json")
    if d is None:
        return []
    items = d.get(cle) if isinstance(d, dict) else d
    if not isinstance(items, list):
        ko(f"data/{nom}.json : liste '{cle}' absente")
        return []
    if len(items) < mini:
        ko(f"data/{nom}.json : {len(items)} {cle} ({mini} minimum)")
    ids, noms = set(), set()
    for x in items:
        i = x.get("id")
        if not i or i in ids:
            ko(f"data/{nom}.json : id manquant ou en double ({i})")
        ids.add(i)
        n = str(x.get("nom", x.get("titre", ""))).strip().lower()
        if n and n in noms:
            ko(f"data/{nom}.json : nom en double '{n}'")
        noms.add(n)
    return items


CATS = {"materiau", "minerai", "outil", "arme", "equipement", "consommable",
        "construction", "vehicule", "relique", "cle"}


def verifier_univers():
    lore = charger_json("data/lore.json") or {}
    q = "data/lore.json"
    civ = lore.get("civilisation", {})
    texte(civ, "nom", 3, q + " civilisation")
    texte(civ, "description", 800, q + " civilisation")
    texte(civ, "chute", 300, q + " civilisation")
    texte(lore.get("signal", {}), "description", 300, q + " signal")
    if len(lore.get("chronologie", [])) < 8:
        ko(f"{q} : chronologie de moins de 8 evenements")
    for e in lore.get("chronologie", []):
        texte(e, "evenement", 80, q + " chronologie")
    factions = lore.get("factions", [])
    if len(factions) < 3:
        ko(f"{q} : moins de 3 factions")
    for f in factions:
        texte(f, "description", 150, f"{q} faction {f.get('id')}")
    if len(lore.get("glossaire", [])) < 10:
        ko(f"{q} : glossaire de moins de 10 termes")
    sujets = {"civilisation", "signal", "chronologie"} | {f.get("id") for f in factions}

    biomes = liste("biomes", "biomes", 8)
    items = liste("items", "items", 60)
    recettes = liste("recipes", "recipes", 45)
    stations = liste("stations", "stations", 4)
    creatures = liste("creatures", "creatures", 16)
    boss = liste("bosses", "bosses", 3)
    quetes = liste("quests", "quests", 12)
    notes = liste("notes", "notes", 24)
    fins = liste("endings", "endings", 3)
    depart = charger_json("data/depart.json") or {}

    B = {b["id"]: b for b in biomes if "id" in b}
    I = {i["id"]: i for i in items if "id" in i}
    R = {r["id"]: r for r in recettes if "id" in r}
    S = {s["id"]: s for s in stations if "id" in s}
    C = {c["id"]: c for c in creatures if "id" in c}
    X = {x["id"]: x for x in boss if "id" in x}
    Q = {x["id"]: x for x in quetes if "id" in x}
    N = {n["id"]: n for n in notes if "id" in n}
    F = {f["id"]: f for f in fins if "id" in f}

    def ref(val, table, quoi, nomtable):
        if val not in table:
            ko(f"{quoi} : reference '{val}' introuvable dans {nomtable}")
            return False
        return True

    # biomes
    tr1 = [b for b in biomes if b.get("tranche") == 1]
    tr2 = [b for b in biomes if b.get("tranche") == 2]
    if not tr1 or not tr2:
        ko("biomes : il faut des biomes 'tranche': 1 (surface + peu profond) et 'tranche': 2 (plus sombre)")
    for b in biomes:
        qb = f"biome {b.get('id')}"
        texte(b, "description", 200, qb)
        texte(b, "ambiance", 80, qb)
        if len(b.get("couleurs", [])) < 3:
            ko(f"{qb} : moins de 3 couleurs d'identite")
        if not isinstance(b.get("palier_requis"), int):
            ko(f"{qb} : palier_requis (entier) absent")
        if len(b.get("ressources", [])) < 3:
            ko(f"{qb} : moins de 3 ressources")
        for r_ in b.get("ressources", []):
            ref(r_, I, qb, "items")
        for c in b.get("creatures", []):
            if ref(c, C, qb, "creatures") and b["id"] not in C[c].get("biomes", []):
                ko(f"{qb} : la creature {c} ne liste pas ce biome dans ses biomes")
        if len(b.get("points_interet", [])) < 2:
            ko(f"{qb} : moins de 2 points d'interet")

    # items
    paliers = set()
    for i in items:
        qi = f"objet {i.get('id')}"
        if i.get("categorie") not in CATS:
            ko(f"{qi} : categorie '{i.get('categorie')}' invalide")
        texte(i, "description", 60, qi)
        if not isinstance(i.get("palier"), int):
            ko(f"{qi} : palier (entier) absent")
        else:
            paliers.add(i["palier"])
        if i.get("categorie") in ("outil", "arme", "equipement", "consommable", "vehicule", "construction") \
                and not i.get("effets"):
            ko(f"{qi} : effets absents pour un objet utilisable")
        if not i.get("obtention"):
            ko(f"{qi} : aucune facon de l'obtenir (obtention)")
        for o in i.get("obtention", []):
            t, r_ = o.get("type"), o.get("ref")
            if t == "recette":
                if ref(r_, R, qi, "recipes") and R[r_].get("resultat") != i.get("id"):
                    ko(f"{qi} : la recette {r_} ne produit pas cet objet")
            elif t == "biome":
                ref(r_, B, qi, "biomes")
            elif t == "butin":
                if r_ not in C and r_ not in X:
                    ko(f"{qi} : butin de '{r_}' introuvable (creatures/bosses)")
            elif t == "quete":
                ref(r_, Q, qi, "quests")
            elif t not in ("depart", "tresor"):
                ko(f"{qi} : type d'obtention '{t}' invalide")
    if len(paliers) < 6:
        ko(f"objets : {len(paliers)} paliers differents (6 minimum)")
    vehicules = [i for i in items if i.get("categorie") == "vehicule"]
    if len(vehicules) < 3:
        ko(f"objets : {len(vehicules)} vehicules (3 minimum, dont le sous-marin geant)")
    equip = [i for i in items if isinstance(i.get("donne_palier"), int)]
    if not equip:
        ko("objets : aucun equipement avec 'donne_palier' (acces aux profondeurs)")

    # recettes et stations
    for s in stations:
        texte(s, "description", 60, f"station {s.get('id')}")
        if s.get("debloque_par") is not None:
            ref(s["debloque_par"], I, f"station {s.get('id')}", "items")
    utilises = set()
    for r_ in recettes:
        qr = f"recette {r_.get('id')}"
        ref(r_.get("resultat"), I, qr, "items")
        ref(r_.get("station"), S, qr, "stations")
        ing = r_.get("ingredients", [])
        if not ing:
            ko(f"{qr} : aucun ingredient")
        for g in ing:
            if ref(g.get("item"), I, qr, "items"):
                utilises.add(g["item"])
            if not isinstance(g.get("qte"), int) or g["qte"] < 1:
                ko(f"{qr} : quantite invalide pour {g.get('item')}")
        if r_.get("resultat") in [g.get("item") for g in ing]:
            ko(f"{qr} : l'objet produit est aussi un ingredient")
    for x in quetes:
        utilises.update(x.get("objets_requis", []))
    for i in items:
        if i.get("categorie") in ("materiau", "minerai") and i.get("id") not in utilises:
            ko(f"objet {i.get('id')} : materiau/minerai jamais utilise (ni recette ni quete)")

    # creatures et boss
    for c in creatures:
        qc = f"creature {c.get('id')}"
        texte(c, "description", 100, qc)
        texte(c, "comportement", 40, qc)
        texte(c, "silhouette", 20, qc)
        if c.get("taille") not in ("petite", "moyenne", "grande", "colosse"):
            ko(f"{qc} : taille invalide")
        if c.get("danger") not in ("inoffensif", "defensif", "agressif"):
            ko(f"{qc} : danger invalide")
        if not c.get("biomes"):
            ko(f"{qc} : aucun biome")
        for b in c.get("biomes", []):
            ref(b, B, qc, "biomes")
        for o in c.get("butin", []):
            ref(o, I, qc, "items")
    if not any(c.get("taille") == "colosse" and c.get("danger") == "inoffensif" for c in creatures):
        ko("creatures : il manque le colosse inoffensif de fond")
    for x in boss:
        qx = f"boss {x.get('id')}"
        texte(x, "description", 200, qx)
        ref(x.get("biome"), B, qx, "biomes")
        if len(x.get("phases", [])) < 2:
            ko(f"{qx} : moins de 2 phases")
        for o in x.get("butin", []):
            ref(o, I, qx, "items")
    if not any(x.get("mini") and B.get(x.get("biome"), {}).get("tranche") in (1, 2) for x in boss):
        ko("boss : aucun mini-boss ('mini': true) dans un biome de la tranche verticale")

    # quetes
    for x in quetes:
        qq = f"quete {x.get('id')}"
        texte(x, "description", 100, qq)
        ref(x.get("biome"), B, qq, "biomes")
        if not x.get("objectifs"):
            ko(f"{qq} : aucun objectif")
        for p in x.get("prerequis", []):
            ref(p, Q, qq, "quests")
        for o in x.get("recompenses", []):
            ref(o, I, qq, "items")
        for o in x.get("objets_requis", []):
            ref(o, I, qq, "items")
        for n in x.get("notes_liees", []):
            ref(n, N, qq, "notes")
    # cycle de prerequis
    etat = {}

    def visite(k):
        if etat.get(k) == 1:
            return True
        if etat.get(k) == 2:
            return False
        etat[k] = 1
        for p in Q.get(k, {}).get("prerequis", []):
            if p in Q and visite(p):
                return True
        etat[k] = 2
        return False
    for k in Q:
        if visite(k):
            ko(f"quetes : cycle de prerequis autour de {k}")
            break

    # notes et fins
    par_biome = {}
    for n in notes:
        qn = f"note {n.get('id')}"
        texte(n, "texte", 250, qn)
        if ref(n.get("biome"), B, qn, "biomes"):
            par_biome[n["biome"]] = par_biome.get(n["biome"], 0) + 1
        if not n.get("sujets"):
            ko(f"{qn} : aucun sujet de lore")
        for s in n.get("sujets", []):
            if s not in sujets:
                ko(f"{qn} : sujet '{s}' inconnu (civilisation, signal, chronologie ou id de faction)")
        if n.get("indice_fin"):
            ref(n["indice_fin"], F, qn, "endings")
    for b in biomes:
        if par_biome.get(b.get("id"), 0) < 2:
            ko(f"biome {b.get('id')} : moins de 2 notes cachees")
    for f in fins:
        qf = f"fin {f.get('id')}"
        texte(f, "condition", 80, qf)
        texte(f, "description", 250, qf)
        if len(f.get("notes_requises", [])) < 2:
            ko(f"{qf} : moins de 2 notes requises")
        for n in f.get("notes_requises", []):
            ref(n, N, qf, "notes")
        ref(f.get("quete_finale"), Q, qf, "quests")

    # progression atteignable
    dispo = {g.get("item") for g in depart.get("inventaire", [])}
    for g in dispo:
        ref(g, I, "depart", "items")
    for i in items:
        if any(o.get("type") == "depart" for o in i.get("obtention", [])):
            dispo.add(i["id"])
    palier0 = depart.get("palier", 0)
    quetes_faites = set()
    for _ in range(500):
        avant = (len(dispo), len(quetes_faites))
        palier = max([palier0] + [I[i]["donne_palier"] for i in dispo
                                  if i in I and isinstance(I[i].get("donne_palier"), int)])
        acces = {b for b, v in B.items() if isinstance(v.get("palier_requis"), int) and v["palier_requis"] <= palier}
        for b in acces:
            dispo.update(B[b].get("ressources", []))
            for c in B[b].get("creatures", []):
                dispo.update(C.get(c, {}).get("butin", []))
        for x in X.values():
            if x.get("biome") in acces:
                dispo.update(x.get("butin", []))
        for i in items:
            if any(o.get("type") == "tresor" and o.get("ref") in acces for o in i.get("obtention", [])):
                dispo.add(i["id"])
        stations_ok = {s for s, v in S.items() if v.get("debloque_par") in (None, "") or v["debloque_par"] in dispo}
        for r_ in R.values():
            if r_.get("station") in stations_ok and all(g.get("item") in dispo for g in r_.get("ingredients", [])):
                dispo.add(r_.get("resultat"))
        for k, x in Q.items():
            if k in quetes_faites:
                continue
            if x.get("biome") in acces and all(p in quetes_faites for p in x.get("prerequis", [])) \
                    and all(o in dispo for o in x.get("objets_requis", [])):
                quetes_faites.add(k)
                dispo.update(x.get("recompenses", []))
        if (len(dispo), len(quetes_faites)) == avant:
            break
    manquants = [i for i in I if i not in dispo]
    if manquants:
        ko(f"progression : {len(manquants)} objets impossibles a obtenir en partant du radeau : "
           f"{', '.join(manquants[:12])}")
    inaccessibles = [b for b, v in B.items() if not (isinstance(v.get("palier_requis"), int) and v["palier_requis"] <= palier)]
    if inaccessibles:
        ko(f"progression : biomes jamais accessibles : {', '.join(inaccessibles)}")
    q_ko = [k for k in Q if k not in quetes_faites]
    if q_ko:
        ko(f"progression : quetes impossibles a terminer : {', '.join(q_ko[:12])}")
    ok(f"univers : {len(biomes)} biomes, {len(items)} objets, {len(recettes)} recettes, "
       f"{len(creatures)} creatures, {len(boss)} boss, {len(quetes)} quetes, {len(notes)} notes, {len(fins)} fins")
    return {"B": B, "C": C, "X": X, "I": I}


def verifier_bible():
    p = fichier("BIBLE.md")
    if not p.exists() or len(p.read_text(encoding="utf-8", errors="replace")) < 4000:
        ko("BIBLE.md absente ou trop courte (4000 caracteres minimum : concept, boucle, univers, progression)")


# ---------------------------------------------------------------- robot
ETAPES = {
    "M2": ["demarrer_radeau", "plonger", "nager", "oxygene", "lampe", "creuser", "poser", "ramasser",
           "fabriquer", "sortir_eau_radeau", "sauvegarder", "recharger"],
    "M3": ["combattre"],
    "M4": ["mini_boss"],
    "M5": ["menu_jouer", "menu_continuer", "menu_options", "pause_echap", "plein_ecran", "touches"],
}


def verifier_robot(phase):
    o = outils()
    if "robot" not in o:
        ko("tools/outils.json : commande 'robot' absente")
        return
    requises = []
    for ph in PHASES[:PHASES.index(phase) + 1]:
        requises += ETAPES.get(ph, [])
    rapport = fichier("tests/robot_rapport.json")
    if rapport.exists():
        rapport.unlink()  # jamais de rapport perime : le robot doit le reecrire maintenant
    debut = time.time()
    code, sortie = lancer(adapter_cmd(o["robot"]), timeout=1800)
    if code != 0:
        ko(f"robot : la commande a echoue (code {code}) : {sortie.strip()[-300:]}")
    if not rapport.exists():
        ko("robot : tests/robot_rapport.json n'a pas ete ecrit par ce lancement du robot")
        return
    r = charger_json("tests/robot_rapport.json") or {}
    etapes = {e.get("nom"): e for e in r.get("etapes", [])}
    for nom in requises:
        e = etapes.get(nom)
        if not e:
            ko(f"robot : etape '{nom}' absente")
        elif e.get("ok") is not True:
            ko(f"robot : etape '{nom}' en echec ({e.get('detail', '')})")
        else:
            cap = fichier(e.get("capture"))
            if cap and cap.exists() and cap.stat().st_mtime < debut - 2:
                ko(f"robot : capture de l'etape '{nom}' perimee (pas prise pendant ce lancement)")
            else:
                ic = png_valide(e.get("capture"), f"robot capture '{nom}'")
                if ic is not None:
                    pas_un_editeur(ic, f"robot capture '{nom}'", e.get("capture"))
    ok(f"robot : {len(requises)} etapes exigees")


# -------------------------------------------------------------- captures
PROFONDEURS = [0, 30, 60, 100, 150, 250, 400]


def mesurer_capture(relpath, quoi, profonde=False):
    img = png_valide(relpath, quoi)
    if img is None:
        return
    pas_un_editeur(img, quoi, relpath)
    n = len(img.px)
    compte, noir, sombre = {}, 0, 0
    for q in img.px:
        c = q[:3]
        compte[c] = compte.get(c, 0) + 1
        if c == (0, 0, 0):
            noir += 1
        if luminance(c) < 0.05:
            sombre += 1
    dom = max(compte.values()) / n
    if noir:
        ko(f"{quoi} : {noir} pixels noir pur ({relpath})")
    if dom >= 0.40:
        ko(f"{quoi} : couleur dominante {dom*100:.0f} % (>= 40 %) ({relpath})")
    if not profonde and sombre / n >= 0.35:
        ko(f"{quoi} : {sombre/n*100:.0f} % de pixels sous luminance 0,05 (>= 35 %) ({relpath})")


def pas_un_editeur(img, quoi, relpath):
    """Une capture de preuve doit montrer le JEU LANCE, pas le gestionnaire de projets ni l'editeur de Godot
    (gris-bleu sombre et uni de l'interface sur la majorite de l'image)."""
    ech = img.px[::7]; ui = {}
    for q in ech:
        r, g, b = q[:3]
        if 20 <= r <= 75 and 0 <= b - r <= 28 and abs(g - (r + b) / 2) <= 10 and max(r, g, b) <= 90:
            ui[q[:3]] = ui.get(q[:3], 0) + 1
    part = sum(ui.values()) / max(1, len(ech))
    plages = sum(1 for v in ui.values() if v > 0.05 * len(ech))   # l'interface : plusieurs gris en grandes plages
    if part > 0.6 and plages >= 2:
        ko(f"{quoi} : ressemble a l'editeur ou au gestionnaire de projets de Godot ({part*100:.0f} % de gris-bleu "
           f"d'interface) : lance le JEU (godot --path . ou la scene principale) et capture sa fenetre ({relpath})")


def verifier_captures(univers, tranche_max):
    B = univers["B"]
    biomes = [b for b in B.values() if b.get("tranche") in range(1, tranche_max + 1)]
    if not biomes:
        return
    pmax = max(b.get("profondeur_max", 0) for b in biomes)
    prof = [p for p in PROFONDEURS if p <= pmax]
    for p in prof:
        for sens in ("descente", "remontee"):
            for lampe in ("lampe", "sans"):
                mesurer_capture(f"shots/profondeur/{p}m_{sens}_{lampe}.png",
                                f"capture {p} m {sens} {lampe}", profonde=(p == prof[-1]))
    for b in biomes:
        mesurer_capture(f"shots/biomes/{b['id']}.png", f"capture du biome {b['id']}")


def verifier_contenu_tranche(univers, tranche, sprites, palette, sources):
    B, C, X = univers["B"], univers["C"], univers["X"]
    par_data = {}
    for s in sprites:
        par_data.setdefault(s.get("data_id"), []).append(s)
    for b in [b for b in B.values() if b.get("tranche") == tranche]:
        bid = b["id"]
        for c in b.get("creatures", []):
            ss = [s for s in par_data.get(c, []) if s.get("type") == "vivant"]
            if not ss:
                ko(f"tranche {tranche} / {bid} : creature {c} sans sprite vivant dans art/manifest.json")
            for s in ss:
                verifier_sprite(s, palette, sources, EXIGENCES_TAGS["creature"])
        for typ, mini in (("prop", 12), ("fond", 4), ("tuileset", 1)):
            n = [s for s in sprites if s.get("type") == typ and s.get("biome") == bid]
            if len(n) < mini:
                ko(f"tranche {tranche} / {bid} : {len(n)} sprite(s) '{typ}' ({mini} minimum)")
            for s in n:
                verifier_sprite(s, palette, sources)
    if tranche == 2:
        minis = [x for x in X.values() if x.get("mini") and B.get(x.get("biome"), {}).get("tranche") in (1, 2)]
        for x in minis:
            ss = [s for s in par_data.get(x["id"], []) if s.get("type") == "vivant"]
            if not ss:
                ko(f"mini-boss {x['id']} : aucun sprite vivant")
            for s in ss:
                verifier_sprite(s, palette, sources, EXIGENCES_TAGS["boss"])
                rects, tags = frames_aseprite(charger_json(s.get("data")) or {})
                if not any(t.startswith("phase2") for t in tags):
                    ko(f"mini-boss {x['id']} : aucune animation 'phase2...' (phases visibles)")


# ------------------------------------------------------------------ phases
def phase_M0(ph):
    verifier_outils()
    verifier_dessin_par_code()
    sources = verifier_provenance()
    palette = verifier_palette()
    sprites = manifeste()
    pl = [s for s in sprites if s.get("data_id") == "plongeur" and s.get("type") == "vivant"]
    if not pl:
        ko("M0 : aucun sprite 'plongeur' (type vivant) dans art/manifest.json")
    exig = EXIGENCES_TAGS["plongeur_M0"] if ph in ("M0", "M1", "M2") else EXIGENCES_TAGS["plongeur"]
    for s in pl[:1]:
        verifier_sprite(s, palette, sources, exig)
    img_m0 = png_valide("shots/m0_plongeur_godot.png", "M0 capture du plongeur dans Godot")
    if img_m0 is not None:
        pas_un_editeur(img_m0, "M0 capture du plongeur dans Godot", "shots/m0_plongeur_godot.png")
    png_valide("boards/plongeur_reference.png", "M0 planche de reference (images de reference + ton rendu)")
    code, sortie = lancer(["git", "log", "--oneline", "-1"], timeout=30)
    if code != 0 or not sortie.strip():
        ko("git : aucun commit (un commit par etape claire est obligatoire)")
    etat = fichier("ETAT.md")
    if etat.exists() and "(aucun) — colle ici" in etat.read_text(encoding="utf-8", errors="replace"):
        ko("ETAT.md jamais mis a jour (dernier controle, en cours, prochaine etape)")
    verifier_godot()
    return sources, palette, sprites


def executer(phase):
    print(f"gate.py SHA-256 : {sha256(__file__)}")
    print(f"Phase controlee : {phase} (et toutes les precedentes)\n")
    idx = PHASES.index(phase)
    sources, palette, sprites = phase_M0(phase)
    univers = None
    if idx >= 1:
        univers = verifier_univers()
        verifier_bible()
    if idx >= 2:
        verifier_robot(phase)
    if idx >= 3 and univers:
        verifier_contenu_tranche(univers, 1, sprites, palette, sources)
        verifier_captures(univers, 1)
        n_son = sum(1 for s in sources.values() if s.get("type") == "son")
        n_mus = sum(1 for s in sources.values() if s.get("type") == "musique")
        n_eff = sum(1 for s in sprites if s.get("type") == "effet")
        if n_son < (14 if idx >= 4 else 8):
            ko(f"sons : {n_son} sources de sons ({14 if idx >= 4 else 8} minimum)")
        if n_mus < 1:
            ko("musique : aucune piste")
        if n_eff < (15 if idx >= 4 else 8):
            ko(f"effets : {n_eff} sprites d'effets ({15 if idx >= 4 else 8} minimum)")
    if idx >= 4 and univers:
        verifier_contenu_tranche(univers, 2, sprites, palette, sources)
        verifier_captures(univers, 2)
        var = [s for s in sprites if str(s.get("data_id", "")).startswith("plongeur") and s.get("type") == "vivant"]
        if len(var) < 3:
            ko(f"plongeur : {len(var)} variante(s) de scaphandre (3 minimum)")
    if idx >= 5:
        if not list(ROOT.glob("builds/**/*.exe")):
            ko("export Windows : aucun .exe dans builds/")
        ico = fichier("icon.ico")
        if not ico.exists():
            ko("icon.ico absente")
        else:
            d = ico.read_bytes()
            if len(d) < 6 or struct.unpack("<HHH", d[:6])[2] < 5:
                ko("icon.ico : moins de 5 tailles (16 a 256 demandees)")
        pj = fichier("PLAYTEST_JOURNAL.md")
        if not pj.exists() or len(re.findall(r"^##\s*Partie", pj.read_text(encoding="utf-8", errors="replace"), re.M)) < 2:
            ko("PLAYTEST_JOURNAL.md : moins de 2 parties completes ('## Partie ...')")
        p = fichier("PLAYTEST.md")
        if not p.exists() or len(p.read_text(encoding="utf-8", errors="replace")) < 500:
            ko("PLAYTEST.md absent ou trop court")
    if idx >= 6:
        rr = fichier("RELECTURE.md")
        if not rr.exists() or len(rr.read_text(encoding="utf-8", errors="replace")) < 1500:
            ko("RELECTURE.md (relecture par un sous-agent independant) absente ou trop courte")
        rp = fichier("RAPPORT.md")
        t = rp.read_text(encoding="utf-8", errors="replace") if rp.exists() else ""
        for titre in ("Fait", "Non verifie", "Limites", "Ecarts vers Dead Cells"):
            if not re.search(r"^#+.*" + titre.replace("e", "[eé]").replace("E", "[EÉ]"), t, re.M | re.I):
                ko(f"RAPPORT.md : section '{titre}' absente")

    print("Verifications reussies :")
    for m in OKS:
        print(f"  [ok] {m}")
    if AVERTS:
        print("\nAvertissements (a verifier, ne bloquent pas) :")
        for m in AVERTS:
            print(f"  [!] {m}")
    resultat = "SUCCES" if not ERREURS else "ECHEC"
    if ERREURS:
        print(f"\n{len(ERREURS)} probleme(s) a corriger AVANT toute autre tache :")
        for m in ERREURS:
            print(f"  [X] {m}")
    print(f"\n==> {phase} : {resultat}")
    try:
        (ROOT / "tests").mkdir(exist_ok=True)
        (ROOT / "tests" / f"gate_{phase}.txt").write_text(
            f"{time.strftime('%Y-%m-%d %H:%M:%S')} {phase} {resultat} "
            f"erreurs={len(ERREURS)} gate_sha256={sha256(__file__)}\n", encoding="utf-8")
    except Exception:  # noqa
        pass
    return 0 if not ERREURS else 1


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:  # noqa
        pass
    if len(sys.argv) != 2 or sys.argv[1] not in PHASES:
        print("usage : python tools/gate.py M0|M1|M2|M3|M4|M5|M6")
        sys.exit(2)
    sys.exit(executer(sys.argv[1]))

#!/usr/bin/env python3
"""
envoyer.py - envoie une commande Python à la session Blender (voir serveur.py) et attend le résultat.

    python3 tools/blender_session/envoyer.py DOSSIER fichier.py [--delai 600]
    python3 tools/blender_session/envoyer.py DOSSIER --code "print(1)"

Affiche la sortie de la commande ; code de retour 0 si OK, 1 si ERREUR ou délai dépassé.
"""
import argparse
import os
import sys
import time


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dossier")
    ap.add_argument("fichier", nargs="?")
    ap.add_argument("--code")
    ap.add_argument("--delai", type=float, default=600.0)
    args = ap.parse_args()
    dossier = os.path.abspath(args.dossier)
    if args.code is not None:
        code = args.code
    elif args.fichier:
        with open(args.fichier, encoding="utf-8") as f:
            code = f.read()
    else:
        sys.exit("indiquer un fichier ou --code")
    fini = os.path.join(dossier, "fini.txt")
    if not os.path.exists(os.path.join(dossier, "pret.txt")):
        sys.exit("session absente : lancer serveur.py d'abord")
    if os.path.exists(fini):
        os.remove(fini)
    tmp = os.path.join(dossier, "commande.py.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(code)
    os.replace(tmp, os.path.join(dossier, "commande.py"))
    debut = time.time()
    while not os.path.exists(fini):
        if time.time() - debut > args.delai:
            sys.exit("délai dépassé")
        time.sleep(0.1)
    with open(fini, encoding="utf-8") as f:
        statut = f.read().strip()
    with open(os.path.join(dossier, "sortie.txt"), encoding="utf-8") as f:
        print(f.read(), end="")
    print(f"[{statut} en {time.time() - debut:.1f} s]")
    sys.exit(0 if statut == "OK" else 1)


if __name__ == "__main__":
    main()

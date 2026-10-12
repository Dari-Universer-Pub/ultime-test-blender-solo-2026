"""
serveur.py - session Blender PERSISTANTE (rendu rapide, sans relancer Blender à chaque essai).

Lancement (en arrière-plan, une seule fois) :
    /opt/outils-varekh/bin/blender -b --factory-startup --python tools/blender_session/serveur.py -- DOSSIER

Le serveur attend un fichier DOSSIER/commande.py, l'exécute dans un espace de noms gardé d'un appel à
l'autre (les objets Blender restent en mémoire), écrit sa sortie dans DOSSIER/sortie.txt puis crée
DOSSIER/fini.txt contenant OK ou ERREUR. La commande STOP arrête le serveur.
Client : python3 tools/blender_session/envoyer.py DOSSIER fichier.py
"""
import contextlib
import io
import os
import sys
import time
import traceback

DOSSIER = os.path.abspath(sys.argv[sys.argv.index("--") + 1])
os.makedirs(DOSSIER, exist_ok=True)
ESPACE = {"__name__": "__session__"}
COMMANDE = os.path.join(DOSSIER, "commande.py")
SORTIE = os.path.join(DOSSIER, "sortie.txt")
FINI = os.path.join(DOSSIER, "fini.txt")


def ecrire(chemin, texte):
    tmp = chemin + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(texte)
    os.replace(tmp, chemin)


ecrire(os.path.join(DOSSIER, "pret.txt"), "pret")
while True:
    if os.path.exists(COMMANDE):
        with open(COMMANDE, encoding="utf-8") as f:
            code = f.read()
        os.remove(COMMANDE)
        if code.strip() == "STOP":
            ecrire(FINI, "OK")
            break
        tampon = io.StringIO()
        statut = "OK"
        try:
            with contextlib.redirect_stdout(tampon), contextlib.redirect_stderr(tampon):
                exec(compile(code, "commande.py", "exec"), ESPACE)
        except BaseException:
            statut = "ERREUR"
            tampon.write(traceback.format_exc())
        ecrire(SORTIE, tampon.getvalue())
        ecrire(FINI, statut)
    time.sleep(0.1)

#!/usr/bin/env bash
# Test de l'export (retouche 4 de ETAT.md) : exporte un PCK du projet, le lance avec le moteur
# (--main-pack, comme un export le ferait), vérifie que le jeu démarre sans erreur, que le
# plongeur est sur le radeau et que la capture montre les images (radeau, tuiles).
# Le .exe Windows n'est pas lancé ici (pas de Wine dans l'environnement) : c'est le PCK qui est testé.
set -u
RACINE="$(cd "$(dirname "$0")/../.." && pwd)"
G=/opt/outils-varekh/bin/godot
cd "$RACINE" || exit 1
mkdir -p builds tests/export
PCK=builds/test_export.pck
ETAT=tests/export/etat_pck.json
JOURNAL=tests/export/godot_pck.log
rm -f "$PCK" "$ETAT" tests/export/pck.png
"$G" --headless --path . --export-pack "Windows Desktop" "$PCK" > tests/export/export_pck.log 2>&1 || { echo "EXPORT ECHEC"; exit 1; }
[ -s "$PCK" ] || { echo "EXPORT ECHEC : PCK absent"; exit 1; }
grep -q "assets/" tests/export/export_pck.log && echo "export : images importées présentes dans le log"
( timeout 60 "$G" --main-pack "$PCK" -- --etat-robot="$RACINE/$ETAT" > "$JOURNAL" 2>&1 & )
for _ in $(seq 1 80); do [ -s "$ETAT" ] && grep -q '"pret": true' "$ETAT" && break; sleep 0.25; done
sleep 2
/opt/outils-varekh/bin/capture-ecran tests/export/pck.png > /dev/null 2>&1
pkill -f "main-pack $PCK" 2>/dev/null
python3 - "$ETAT" "$JOURNAL" <<'PY'
import json, sys, re
etat, journal = sys.argv[1], sys.argv[2]
try:
    d = json.load(open(etat, encoding="utf-8"))
except Exception as e:
    print("ETAT illisible :", e); sys.exit(1)
erreurs = [l for l in open(journal, encoding="utf-8", errors="replace") if re.search(r"SCRIPT ERROR|Failed loading|Parse Error", l)]
print("position :", d.get("position"), "| sur le radeau :", d.get("sur_radeau"), "| inventaire :", d.get("inventaire"))
print("erreurs de script :", len(erreurs))
ok = d.get("sur_radeau") is True and not erreurs
print("EXPORT PCK :", "SUCCES" if ok else "ECHEC")
sys.exit(0 if ok else 1)
PY

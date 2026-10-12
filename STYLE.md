# STYLE.md — Réglages communs de la chaîne d'assets (héros v6, décision de Julien du 12/10)

Ces réglages servent à TOUS les assets. Ils remplacent ceux de M0 (case 64 px, plongeur 40 px, contour
sélectif) : voir `DECISIONS.md`. Référence visuelle : `art/references/ancre_plongeur_v6.png` (et ses rendus x6).

## 1. Cadre et échelle
- Case d'un sprite : **112 × 112 px**. Héros : **70 à 74 px de haut** (au repos ; la nage : **56 à 80 px**).
- Trois quarts de face : caméra **orthographique**, azimut **35°**, élévation **15°** (depuis +X, -Y).
- Rendu DIRECT à la taille finale : pas de réduction après coup. Filtre de pixel 0, pas d'antialiasing,
  tramage 0. Fond transparent. Alpha **0 ou 255** seulement.
- Le héros regarde vers l'avant-droite de la caméra ; +Z = haut.

## 2. Lumière et ombrage
- **Une seule lumière, en haut à gauche.** Pas de spéculaire, pas de réflexion d'environnement.
- Ombrage PAR PALIERS : produit scalaire normale · lumière, ramené à [0, 1], puis rampe CONSTANTE de 3 ou 4 tons
  de la matière. Une arête entre deux paliers est nette.
- Ombres arrondies : sous les bras, sous la ceinture, sous le casque (décalage de palier par attribut OMB).
- Lumière de contour **cyan froid, en pixels clairs**, sur le bord droit seulement (pas un trait), si elle aide.
- Moteur : EEVEE, émission seule (les matières ne reçoivent pas la lumière de scène).

## 3. Contour : AUCUN
- Pas de trait indigo ni de trait sombre sur le pourtour, ni entre parties.
- La forme est définie uniquement par le contraste de couleurs et de valeurs entre matières, et par l'ombrage.
- Vérification obligatoire : sur eau claire, eau sombre et en niveaux de gris. Un bord qui se fond dans le fond
  se corrige par la VALEUR (éclaircir ou assombrir le bord), jamais par un trait.

## 4. Couleurs (palette du héros v6)
- Quantification PAR MATIÈRE : chaque pixel prend la rampe de SA matière, le ton est choisi par la lumière.
  Jamais la couleur la plus proche d'une palette globale.
- Matières : laiton (4 tons), toile beige (4), cuir (3), caoutchouc bleu-violet (3), métal (3), verre (3),
  reflet (1), corde (3). Environ 26 couleurs au total, cible 24 à 32.
- Décalage de teinte : ombres vers le bleu-violet, lumières vers le jaune chaud. Jamais de noir pur, jamais de blanc pur.
- Séparation par la valeur : bras et manches un ton plus clair ou plus foncé que le tronc ; gants et bottes
  nettement plus sombres ; ceinture marron ; manchettes sombres.

## 5. Pixelisation et nettoyage
- Pas de réduction : le rendu est déjà à la bonne taille.
- Carte d'identité des matières et des groupes à la même résolution (pour mesurer, pas pour dessiner).
- Nettoyage : **zéro pixel isolé** (aucun des 8 voisins de même couleur). `tools/pixelisation/nettoyage.py`.
- Aucune passe ne compte si elle modifie moins de **5 % des pixels**.

## 6. Membres (mesure obligatoire, image par image)
- Carte d'identité, `tools/mesure/membres.py <dossier> --facteur 1 --groupe idle|nage --cote-proche d`.
- Chaque membre (bras proche, bras lointain, jambe proche, jambe lointaine) : **>= 30 px visibles** et
  **>= 60 % non cachés**, sur CHAQUE image.

## 7. Animations (héros)
- Un seul squelette, mêmes réglages de rendu à chaque image.
- Pose de nage : corps de trois quarts ; bras et jambes écartés dans le plan visible ; anticipation et glisse.
  Amplitude du mouvement >= 0,45 (mesurée sur la course du poignet, en hauteurs de corps).
- Idle : 6 images, déjà validé (`art/pixel/plongeur_v6/idle_01.png`).

## 8. Journal visuel
- Une entrée par changement regardé, avec sa planche (`tools/planches/comparer.py`, x6 pour les retouches).
- Les 7 critères : silhouette, couleurs, cadrage, taille, détails, cohérence (avec l'ancre), pixels parasites.

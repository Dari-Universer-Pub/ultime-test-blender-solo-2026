# BRIEF.md — Cahier des charges de LES CLOCHES DE VAREKH (le QUOI ; le COMMENT est dans PLAN.md et AGENTS.md)

Tu vas concevoir et construire un jeu 2D pixel art sous Godot 4 (GL Compatibility), dans ce dossier. Le but n'est PAS un prototype grossier à améliorer plus tard : le but est un jeu qui vise dès le départ un niveau professionnel, avec Dead Cells comme référence de finition visuelle et de ressenti de jeu, Subnautica comme référence d'ambiance et de progression, et Terraria comme référence de monde modifiable. Ce sont des références de QUALITÉ, pas des modèles à copier : aucun personnage, décor, nom, objet ou composition de ces jeux ne doit être repris. Tout est original.



━━━ 1. LE JEU ━━━
Titre de travail : LES CLOCHES DE VAREKH (tu peux proposer mieux, avec trois alternatives originales).
Un jeu de survie, exploration et construction sous-marines, vu de côté, en pixel art. Le joueur commence sur un petit radeau à la surface, avec presque rien, puis plonge dans un océan immense, en largeur et en profondeur. Le monde est modifiable (on creuse, on pose, on construit), comme un bac à sable. On remonte pour se ravitailler en oxygène.
Contenu final visé (pour dimensionner l'architecture) : 8 à 10 biomes, des dizaines de paliers d'équipement (du scaphandre de toile jusqu'à un sous-marin géant), armes, ressources, minerais, notes cachées, ruines d'une civilisation disparue, 3 fins, plusieurs boss, un hub de base à construire, des véhicules.
Tu inventes la civilisation disparue, le signal, les créatures et les noms : tout doit être original.

━━━ 2. CE QUE TU LIVRES : TRANCHE VERTICALE PRO + UNIVERS COMPLET EN DONNÉES ━━━
Pour ne pas diluer la qualité :
- TRANCHE VERTICALE DE QUALITÉ PRO : le radeau et la surface, plus 2 biomes sous l'eau (le premier peu profond, le second plus sombre), plus 1 mini-boss. Là, tout est fait au niveau visé (visuels, animations, lumière, effets, sons, sensations). C'est ça qu'on regarde et qu'on juge.
- UNIVERS COMPLET EN DONNÉES pour tout le reste : chaque système existe déjà et fonctionne, et tout l'univers du jeu final (lore, biomes, progression jusqu'au sous-marin géant, objets, recettes, créatures, boss, quêtes, notes, fins, et leurs liens) est conçu en fichiers JSON riches, validés par tools/gate.py. Schéma et minimums : docs/DONNEES.md. Ajouter du contenu plus tard = ajouter des données, pas réécrire du code.
Les biomes et paliers non polis utilisent des placeholders lisibles marqués PROVISOIRE dans PROVENANCE.md.

━━━ 3. RÈGLES NON NÉGOCIABLES ━━━
- Git dès le début (git init), un commit par étape claire.
- Ne dis « fait » que si c'est vérifié par capture, mesure, script ou test réel. Sinon écris « non vérifié ». Un RAPPORT.md honnête (fait / non vérifié / limites / défauts connus) est OBLIGATOIRE à la fin.
- Tu dois REGARDER les images (lis le fichier image, pas seulement son nom) : chaque asset passe par une planche ×4 avec les autres assets du même groupe, et tu écartes ou retouches ce qui détonne.
- Tu joues réellement le jeu : tests avec de vraies touches clavier dans une vraie fenêtre (pas d'appels directs de fonctions), au moins deux parties complètes, journal PLAYTEST_JOURNAL.md. Un robot de test (vraies touches) doit réussir : démarrer sur le radeau, plonger, nager, utiliser l'oxygène et la lampe, creuser, poser, ramasser, sauter sur le radeau et en sortir de l'eau, combattre, sauvegarder puis recharger. Si le robot échoue, le jeu n'est pas terminé.
- Aucune source inventée : URL exacte, licence (CC0 de préférence, CC-BY crédité), SHA-256, copie de la page de licence, ligne dans PROVENANCE.md, script de contrôle. Site inaccessible = le dire et changer de source. Pas de pack qui interdit l'IA, pas de licence floue.
- AUCUNE LIMITE d'itérations ni d'essais. Quand un problème t'empêche d'avancer (rendu vide, import qui échoue, outil qui plante, test qui échoue, asset qui détonne), tu le résous, quel que soit le nombre d'essais, et tu ne fais RIEN d'autre tant qu'il n'est pas résolu. Tu ne le contournes jamais en dessinant par code ni en baissant la qualité visée. La méthode est au §5 ter (« règle d'or des blocages »).
- Relecture finale par un sous-agent indépendant qui n'a pas fait le travail : il lance le jeu, regarde les captures, cherche les défauts et les mesures hors seuil.
- Ne jamais générer par code ce qui doit être réel : musique, sons, sprites de créatures.

━━━ 4. DOCUMENTS À PRODUIRE D'ABORD ━━━
CLAUDE.md (règles du projet), BIBLE.md (concept, boucle de jeu, lore), DECISIONS.md (chaque choix technique avec alternatives mesurées), STYLE.md (direction artistique chiffrée, voir §6), ARCHITECTURE.md, IDEES.md (défauts remarqués, une ligne par défaut vu), PLAYTEST.md (protocole pour un humain), PROVENANCE.json (format dans PLAN.md).
Décisions à trancher dans DECISIONS.md avec chiffres :
- Résolution interne : elle doit diviser exactement 1920×1080 (pour zéro bande noire en plein écran) ; candidats 480×270, 640×360, 960×540. Je recommande 640×360 (plus de détail pour la beauté) mais tu justifies par un tableau (taille du joueur, nombre de tuiles à l'écran, lisibilité du HUD). Plein écran en mode entier exact, plus un mode « remplir », plus un choix de résolution dans les options.
- Taille de tuile compatible avec la résolution choisie (grille entière).
- Monde : tuiles modifiables dans un TileMapLayer, générées par chunks, sans simulation de fluide.
- Éclairage : un seul système cohérent pour fond, terrain, sprites et lumières (voir §7).

━━━ 5. ASSETS : TU FAIS TOUT TOI-MÊME DANS BLENDER ━━━
Aucun outil d'assets n'est fourni, et rien de visuel ne se télécharge : ni modèle 3D, ni rig, ni animation, ni pack 2D. Tu es l'artiste.
- Tout ce qui est vivant ou animé (plongeur, créatures, mini-boss), les objets volumineux et les props : construits par TOI dans Blender, par tes propres scripts Python (`/opt/outils-varekh/bin/blender -b --python art/source/blender/<id>.py`). Le script refait tout de zéro : modélisation (corps continus, sculptés ou modélisés, pas un assemblage visible de cubes et de sphères), matériaux, squelette, animations par os, caméra orthographique fixe, lumière, rendu.
- Pixelisation par TON script dans `tools/pixelisation/` : réduction, quantification aux rampes de la palette (3 à 4 tons par matière sur un sprite), contour sélectif. Mêmes réglages de caméra, de lumière et de pixelisation pour tous les assets, écrits dans STYLE.md.
- Ce qui est simple, rigide ou de profil (tuiles, icônes, interface, petits props) : Blender aussi, ou Aseprite (scripts Lua ou ligne de commande).
- Finition Aseprite sur chaque sprite vivant : sources .aseprite dans art/source/aseprite, export ×8, regarde, corrige (casque, hublot, mains, yeux, pixels isolés), au moins 3 itérations avec une planche par itération dans boards/iterations/.
- Un seul mannequin riggé par famille (le plongeur, un type de poisson…) pour toutes ses animations et variantes.
- Deux planches de contrôle par sujet : le premier rendu (base), puis la version actuelle (modifiée), côte à côte.
- Références : tu peux regarder des images libres pour t'inspirer (silhouette, proportions, couleurs), rangées dans art/references/ avec leur adresse. On ne copie jamais.
- Pillow et numpy servent uniquement à mesurer, contrôler, assembler des planches et pixeliser un rendu Blender, jamais à dessiner un asset.
- Pas de rectangle de repli visible en jeu : un placeholder est un vrai rendu Blender pixelisé, même imparfait.
- Effets : Godot (shaders, GPUParticles2D, PointLight2D, CanvasModulate) ou Blender.
- Sons et musique (seule chose qui se télécharge) : vrais enregistrements et vraies pistes libres (CC0 de préférence, CC-BY crédité), trouvés par toi-même ; interdit : musique synthétisée par code. Polices : licence OFL ou CC0.
- Tests : anti-scintillement entre images avec seuil mesuré, comptage des pixels isolés, silhouette noir et blanc.
- OUTILS : CHEMINS EXACTS, DÉJÀ COMPILÉS (Linux). Ne les cherche pas dans le PATH, ne les recompile jamais. Lance réellement les commandes de version au tout début :
  • Godot 4.4.1 : /opt/outils-varekh/bin/godot --version
  • Blender 5.2.1 LTS : /opt/outils-varekh/bin/blender --version   (rendu sans écran : -b)
  • Aseprite 1.3.18.6 : /opt/outils-varekh/bin/aseprite --batch --version
    En mode ligne de commande : ... aseprite --batch --script fichier.lua ... ; sans interface.
  • Si ces fichiers n'existent pas (sandbox neuve) : bash <dossier du dépôt kit-outil-v2 (dossier outils/)>/INSTALLER_OUTILS.sh, puis bash /opt/outils-varekh/verifier.sh (doit afficher SUCCES). Lis /opt/outils-varekh/LISEZMOI.md pour les captures (godot-capture, capture-ecran).
  • Chemins de fichiers : Linux pour les trois outils, entre guillemets s'ils contiennent des espaces.
  • Si une de ces commandes échoue, relance l'installateur puis le vérificateur et lis leurs .log ; ne conclus jamais « outil absent ».

━━━ 5 ter. RÈGLE D'OR DES BLOCAGES, ANTI-ABANDON ET SOURCES ━━━
RÈGLE D'OR DES BLOCAGES (elle remplace toute limite d'itérations). Il n'existe aucune limite d'essais. Un blocage se résout, il ne s'abandonne pas et ne se déclare pas « consigné, on passe à la suite ». Tant qu'il n'est pas résolu, tu ne travailles sur rien d'autre. Méthode :
1. Réduis le défaut au plus petit cas qui échoue (un seul modèle, un seul script, un seul appel).
2. Liste les causes possibles, puis teste-les une par une en changeant UNE seule chose à la fois.
3. Avant chaque essai, SUPPRIME le fichier de sortie attendu, puis vérifie le code de retour, la date et la taille du NOUVEAU fichier. Ne mesure jamais un fichier périmé : un rendu qui a échoué avant d'écrire laisse l'ancien fichier en place et fausse toutes les conclusions.
4. REGARDE l'image elle-même, pas seulement sa mesure.
5. Lis les messages d'erreur en entier, cherche dans la documentation officielle, essaie une autre version de l'outil (autres réglages de rendu Blender, Workbench ou EEVEE), une autre méthode de modélisation (modificateurs, sculpture, métaballes, courbes), un autre rig.
6. Consigne chaque hypothèse testée en une ligne dans IDEES.md.
7. Si la cause dépend de quelque chose que tu ne peux pas obtenir seul (compte, téléchargement bloqué), écris précisément ce qu'il te faut, puis cherche un autre chemin vers le MÊME but (autre méthode dans Blender ou Aseprite). Jamais de dessin par code à la place.
Piège connu à vérifier d'abord pour un rendu Blender vide : une caméra Blender regarde vers -Z ; l'orienter avec to_track_quat('Z','Y') la tourne vers l'extérieur du modèle et donne une image vide ; il faut to_track_quat('-Z','Y').

ANTI-ABANDON. Quand la chaîne 3D → Blender → pixel fonctionne sur un rocher, ce n'est que le début, pas une raison de changer de méthode. Il est INTERDIT de passer à Pillow, numpy ou du dessin par code pour un plongeur, une créature ou un objet volumineux, quelle que soit la raison (modèle introuvable, rendu moyen, manque de temps). Un placeholder valable est un vrai rendu Blender pixelisé de TON modèle, même imparfait. Il n'est jamais un dessin généré par code.

SOURCES : rien de visuel ne se télécharge. Pour les sons, la musique et les polices, tu cherches toi-même sur le Web, tu compares au moins 3 candidats, tu lis la licence sur la page, et tu notes ton choix dans DECISIONS.md.

━━━ 6. EXIGENCES VISUELLES (la beauté se mesure) ━━━
Palette et couleur :
- Palette de 64 à 96 couleurs organisée en rampes de 5 à 7 tons par matière, avec décalage de teinte (ombres vers le bleu-violet, lumières vers le jaune-chaud ; contrôle par script : la teinte varie d'au moins 15° le long de chaque rampe). Pas de simple « plus foncé ».
- Chaque biome a une identité de couleur reconnaissable de loin (pas seulement des variations de bleu) ; seuils mesurés sur chaque capture : couleur dominante < 40 %, famille eau < 60 %, zéro noir pur.
- Contour sélectif (épaisseur et couleur varient selon la matière et la lumière), jamais un trait uniforme noir. Lumière dominante en haut à gauche, rendue sur tous les sprites.
Personnage :
- Un plongeur à la silhouette immédiatement lisible et attachante (grosse tête/casque rond avec hublot clair, couleur qui tranche sur l'eau ; contraste mesuré ≥ 4:1 face à chaque fond).
- Animations (avec anticipation, impact et retour, écrasement/étirement, mouvement secondaire des tuyaux et bulles) : nage 8 images, idle flottant 6, creusage 6, attaque 6, saut (montée, apex, chute, atterrissage) 4, dégâts 3, mort 8. Équipement visible sur le sprite (au moins 3 variantes de scaphandre).
- Lumière sur sprites : cartes de normales (rendu Blender de la passe normale) utilisées par les Light2D de Godot pour le plongeur et les créatures.
Créatures :
- 12 espèces minimum, chacune avec une silhouette unique (test : planche en noir et blanc, on doit les distinguer), nage 8 images, attaque avec geste d'avertissement lisible 4, mort 6. Tailles variées (banc de petits poissons, moyens, grands, un colosse inoffensif de fond). Le mini-boss a des phases visibles. Pas de recoloration d'une même silhouette.
Décor et tuiles :
- Tuiles de terrain avec raccords automatiques (autotile 47 cases minimum pour les matières principales), au moins 3 variantes par tuile, transitions entre biomes. Textures qui disent la matière (roche mouillée, sable, corail, algue, métal rouillé, verre).
- Au moins 4 plans de fond en parallaxe par biome, dont des grandes silhouettes lointaines (piliers, ruines, créatures), plus un avant-plan sombre ou flou.
- Au moins 12 types de décors/props par biome, posés par règles (grille, groupes, pas de superposition), au moins 6 éléments non-sol et 3 familles de formes sur n'importe quel écran. Un point d'intérêt reconnaissable (épave, ruine, grotte lumineuse) régulièrement.
Effets :
- Au moins 15 types d'effets dessinés (bulles, éclats de roche au creusage, impact de coup, éclaboussure à la surface, étincelles, sang/encre des créatures, flash de dégâts, sonar, poussière, plancton, rais de lumière…), secousse d'écran, arrêt sur image au coup, lueurs (bloom léger), brume de profondeur en arrière-plan uniquement.
Interface :
- Icônes dessinées une à une, silhouette différente par catégorie d'objet (lisible en niveaux de gris à ×1), HUD compact, texte lisible à la résolution choisie, animations d'ouverture, retours visuels et sonores à chaque action.

━━━ 7. LUMIÈRE ET LISIBILITÉ (le piège à éviter absolument) ━━━
- Un seul système d'éclairage : le fond d'eau et le terrain obéissent à la même loi de profondeur. Couleur du fond = fonction continue de la profondeur (aucun saut brutal à l'entrée d'un biome, transition d'au moins 3 secondes). Plancher d'ambiance : le terrain proche du joueur reste lisible sans lampe (contraste terrain/fond ≥ 1,6:1, moins de 35 % de pixels sous luminance 0,05 hors zone la plus profonde). La lampe éclaire en plus, elle n'est pas la seule visibilité.
- Mesure obligatoire : captures à 0, 30, 60, 100, 150, 250, 400 m, à la descente ET à la remontée, avec et sans lampe, avec luminance, contraste et couleur dominante consignés. Pas de « brouillard » : rien qui délave les objets au passage de la surface.
- Le plongeur reste toujours lisible (halo minimal même lampe éteinte).

━━━ 8. SENSATIONS DE JEU (pro dès le départ) ━━━
- Contrôles complets dès le premier jour : déplacement, SAUT (hors de l'eau : saut variable, temps de coyote 0,1 s, saut tamponné 0,1 s ; depuis l'eau près de la surface : sortie de l'eau sur le radeau ; sous l'eau : impulsion de nage), attaque, creusage, pose, interaction, lampe, inventaire, pause, carte, plein écran. Toutes les touches dans un seul fichier de config modifiable en jeu, clavier AZERTY/QWERTY (codes physiques).
- Nage avec inertie agréable, creusage avec un vrai retour (délai ressenti, éclats, son, secousse légère), pose précise sous le curseur, aucune possibilité de rester coincé.
- Combat : gestes d'avertissement lisibles, recul, invincibilité courte, retours sonores et visuels. Le mini-boss a au moins 2 phases.
- Boucle de jeu claire en 15 à 20 minutes dans la tranche verticale : radeau → plongée → ressources → fabrication → palier suivant → mini-boss → retour au radeau.
- Sauvegarde fiable, menu complet (jouer, continuer, options, crédits, quitter), options (volumes, touches, plein écran + résolution + mode automatique qui s'adapte à l'écran, langue), icône de l'application = la tête du plongeur sur fond transparent (ICO multi-tailles 16 à 256, canal alpha réel, utilisée aussi pour la barre des tâches).
- Pause avec Échap partout, y compris pendant les panneaux et menus (touche testée avec de vraies touches).

━━━ 9. ORDRE DE TRAVAIL ━━━
L'ordre de travail est dans PLAN.md (phases M0 à M6 d'un seul et même jeu). Une phase est finie quand « python tools/gate.py <phase> » affiche SUCCES. Fais d'abord le fond (jouabilité, lisibilité), mais ne livre jamais un asset « en attendant mieux » qui ne ressemble à rien : chaque élément visible doit déjà être dans le style.

━━━ 10. LIVRABLES ━━━
Jeu qui se lance et se joue ; robot de test qui passe ; RAPPORT.md honnête ; PLAYTEST.md (protocole pour moi) et PLAYTEST_JOURNAL.md (ce que tu as joué) ; shots/ avec captures étiquetées (chaque profondeur, chaque biome, combat, menu, plein écran) ; planches ×4 de tous les assets ; PROVENANCE.md complet ; Git propre ; liste de ce que l'utilisateur doit juger lui-même (sons, ressenti, beauté) ; liste des écarts restants vers le niveau Dead Cells, classée par impact.
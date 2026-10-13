# TOEIC 990+ AI

Application web personnelle de préparation au TOEIC Listening & Reading. Fonctionne localement, sans dépendance Python supplémentaire ni installation npm.

## Démarrer

Python 3.10 ou plus récent :

```sh
git clone https://github.com/EvanGrv/Toeic_999.git
cd Toeic_999
python3 -m server.app
```

Si le projet est déjà téléchargé, ouvrir un terminal dans son dossier et exécuter seulement `python3 -m server.app`. Les audios et images sont inclus dans le dépôt. La base personnelle est créée automatiquement au premier lancement et n’est pas publiée sur GitHub.

Ouvrir **http://localhost:8787**. Sur Mac, le fichier `Lancer TOEIC.command` démarre également le serveur par double-clic. Arrêt : `Ctrl+C`. Autre port : `PORT=8788 python3 -m server.app`.

Le serveur reste lié à `127.0.0.1`. Cette version est personnelle et ne doit pas être exposée telle quelle à Internet. Aucune authentification multi-utilisateur n’est implémentée.

## Ce qui est disponible

- Profil Evan, 715/990 (Listening 405, Reading 310), premier objectif 900 et cap final 990.
- Programme interactif de 14 × 120 minutes, réglable par jour.
- **2 344 questions** : 236 items initiaux et 2 108 variantes paramétrées originales.
- Parties 1–7, documents multiples, conversations à plusieurs voix, supports visuels et corrections françaises.
- **305 flashcards**, répétition espacée, carnet d’erreurs, **11 cours**.
- **8 séries de 200 questions**, diagnostic et examen Reading de 100 questions.
- Échéances serveur, reprise de séance, repères, résultats par section et compétence.
- SQLite, export JSON, sauvegarde/restauration du fichier de données.
- Atelier de variantes locales, import JSON autorisé, génération OpenAI optionnelle avec seconde résolution indépendante.

Les séries partagent des familles de situations et six photos. Elles ne sont ni officielles, ni indépendamment étalonnées. Les voix et photos sont synthétiques. Les textes sont parfois plus courts que les passages exigeants du vrai test. Aucun score TOEIC n’est prédit à partir d’un pourcentage.

## Données et sauvegardes

Les données se trouvent dans `data/toeic.sqlite3`. Les réponses sont enregistrées au moment de la validation. Export JSON depuis « Mes préférences ». Pour une sauvegarde SQLite cohérente pendant l’utilisation :

```sh
python3 scripts/backup.py
```

Le script affiche le fichier créé sous `data/backups/`. Pour restaurer : arrêter le serveur, conserver le fichier actuel, puis utiliser `python3 scripts/backup.py --restore CHEMIN`. Une sauvegarde de l’état courant est créée avant restauration.

## Audios

Les fichiers WAV et le manifeste sont fournis dans `public/audio/`. Ils fonctionnent sans service externe. Pour les régénérer sur macOS :

```sh
python3 scripts/generate_audio.py
```

Voix : Samantha, Daniel, Karen, Moira. Le script détecte les sorties silencieuses et refuse de les considérer comme des médias valides. Il conserve les fichiers déjà valides. La synthèse macOS doit pouvoir accéder aux services système ; un bac à sable peut produire des fichiers vides.

## Génération optionnelle OpenAI

Définir `OPENAI_API_KEY` dans l’environnement local, sans mettre de secret dans le code ou dans un formulaire du navigateur. `OPENAI_MODEL` permet de choisir un modèle compatible avec Responses et les sorties structurées ; valeur par défaut : `gpt-4.1-mini`.

```sh
export OPENAI_MODEL=gpt-4.1-mini
python3 -m server.app
```

L’atelier ne fait un appel qu’après une demande explicite de génération en mode OpenAI. Deux requêtes par question : rédaction puis vérification sans la réponse attendue. `store: false` est envoyé. Les questions ne sont publiées qu’après relecture. Sans clé, les cours, examens, audios, révisions et variantes locales fonctionnent. Les appels réels nécessitent des crédits API et ne font pas partie des tests automatisés.

## Vérifier

```sh
python3 -m unittest discover -s tests -v
node --check app/main.js
python3 scripts/audit_content.py
```

Les tests utilisent une base temporaire indépendante. Voir `docs/architecture.md`, `docs/research/` et `docs/verification.md`.

## Périmètre reçu

Le texte fourni initialement s’arrête au milieu de la section 2.5. Le projet réalise le périmètre visible, complété par la demande de 28 heures de contenu. Pas de récupération de banques propriétaires, pas de paiement ou compte tiers créé, pas de déploiement public.

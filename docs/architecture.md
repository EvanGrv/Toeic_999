# Architecture et décisions

## Exécution

- Client : HTML/CSS et modules JavaScript natifs. Aucun CDN, paquet frontend, tracking ou build requis. Navigation par fragments, rendu des pages, formulaires et lecteur audio.
- Serveur : Python standard, `ThreadingHTTPServer`, API JSON ; port 8787, loopback uniquement.
- Données : SQLite en WAL, connexions par requête et verrou d’écriture local. Sessions avec copie des questions afin que des changements ultérieurs dans la banque ne changent pas les corrections d’une séance existante.
- Médias : WAV mono 22 050 Hz servis avec prise en charge de `Range`. Atlas photographique synthétique, affiché par cadrage CSS, sans altération du fichier source.

Choix motivé par un dossier vide, un usage personnel hors ligne et le souhait d’une application immédiatement utilisable. Aucun framework lourd ou compte cloud n’est nécessaire.

## État persistant

`settings` contient le profil ; `sessions` les passages et réponses ; `attempts` les observations uniques par séance/question ; `reviews` l’échéancier des cartes et erreurs ; `drafts` les propositions et publications ; `lesson_progress` les cours lus.

Un double envoi de réponse libre est idempotent. Une correction de choix pendant un examen remplace le choix avant correction finale. Les statistiques d’examen ne sont intégrées qu’à la fin. Une séance libre terminée tôt ne fabrique pas des erreurs sur toutes les questions restantes.

## Sélection

Les documents et conversations restent atomiques. La sélection combine nouveauté, faiblesse observée, difficulté et préférence. La proportion Reading est un objectif approximatif par séance ; la taille des groupes peut créer un écart. Le recalcul ne démarre qu’avec un minimum de réponses distinctes. Les seuils sont dans `server/engine.py`.

La base initiale utilise des niveaux éditoriaux. Les variantes ne sont pas des observations psychométriquement indépendantes ; les indicateurs sont destinés à orienter une pratique personnelle, pas à certifier un niveau.

## Examens

Huit ensembles structurés de 200 questions. Chaque série possède ses questions Reading et ses groupes Listening, avec les six photos communes. L’algorithme ne coupe jamais un texte à compléter ou un ensemble de documents multiples.

Les 45 minutes de Listening sont réparties selon la durée réelle des fichiers et des temps de réponse ; la marge est distribuée entre passages. Le temps serveur détermine le passage actuel et l’offset de reprise audio. La transition Reading et l’expiration s’effectuent dès la prochaine requête même si l’onglet a dormi. Le client se synchronise aux limites et le serveur vérifie les réponses.

Les fichiers sont accessibles localement : ce simulateur n’est pas un environnement anti-triche certifié. Aucun score équivalent ETS n’est calculé.

## Génération

Le mode local emploie des gabarits contraints et étiquette leur provenance. Le mode OpenAI utilise Responses, un schéma JSON strict puis une seconde résolution indépendante. Aucun historique personnel n’est nécessaire pour ces requêtes ; seuls consignes et exercice sont transmis. Refus, sortie incomplète ou divergence de clé interrompent l’ajout. Toutes les créations restent des brouillons jusqu’à la relecture explicite.

Référence technique consultée : [sorties structurées OpenAI](https://developers.openai.com/api/docs/guides/structured-outputs), 13 octobre 2026.

## Sécurité et limites opérationnelles

Contrôle de Host, origine même site et en-tête non simple pour les mutations ; taille JSON limitée ; requêtes SQL paramétrées ; contenu échappé côté client ; CSP ; chemins statiques confinés à `app`, `public` et aux Markdown de `docs`. La base et les secrets ne sont pas servis. Aucun accès extérieur activé.

Usage mono-utilisateur uniquement. Une vraie mise en ligne nécessiterait un serveur de production, authentification, isolation des utilisateurs, HTTPS, protection contre l’abus et supervision. La clé API se configure uniquement dans l’environnement du serveur.

# Vérifications — 13 octobre 2026

## Contrôles exécutés

- `python3 -m unittest discover -s tests -v` : **22 tests réussis**, bases temporaires séparées de la progression personnelle.
- `node --check app/main.js` et compilation des modules Python : réussies.
- `python3 scripts/audit_content.py` : aucune erreur structurelle ou de média.

L’audit dénombre **2 344 questions** : 6 / 205 / 312 / 240 / 1 021 / 128 / 432 pour les parties 1 à 7. Il vérifie les identifiants, les choix distincts, les clés, les métadonnées, les explications et chaque fichier audio.

**395 fichiers WAV non silencieux**, durée cumulée 191,3 minutes. Chaque série contient 6 / 25 / 39 / 30 / 30 / 16 / 54 questions. Les enregistrements et pauses minimales occupent environ 34–36 minutes par série ; la marge est distribuée pour atteindre exactement 45 minutes de Listening.

## Tests fonctionnels automatisés

Couverture : masquage des corrections et transcriptions, idempotence des réponses libres, reprise depuis SQLite, choix révisables en examen, accumulation du temps actif, refus des réponses tardives, transition Listening/Reading, offsets audio, échéances serveur, refus de deux examens simultanés, adaptation sur questions distinctes, seuil des défis, répétition espacée, import et publication après relecture, validation du profil, export et sauvegarde/restauration SQLite.

Les tests HTTP vérifient les médias et les requêtes Range, les réponses JSON, le parcours de génération locale, le contrôle d’origine et de Host, ainsi que le refus d’accès aux fichiers privés ou hors du répertoire statique.

## Parcours vérifiés dans le navigateur

Avec une base de test distincte, sur une fenêtre de bureau et à 390 × 844 pixels :

- Entraînement de partie 5 : choix, correction française, rechargement et conservation de la réponse, fin anticipée et bilan.
- Flashcard : révélation puis répétition programmée ; compteur de cartes dues diminué.
- Listening : lecture WAV, compteur audio avançant, propositions et transcription révélées après validation.
- Examen Reading, série 08 : choix sauvegardé immédiatement, rechargement conservant la réponse et le chronomètre, correction uniquement à la fin.
- Examen complet : test du son, photo, lecture automatique, passage suivant selon l’horloge, reprise après rechargement au passage courant.
- Atelier : génération locale, relecture de la question puis publication dans la banque de test.
- Préférences : changement de durée, application aux sept jours, sauvegarde et rechargement.
- Programme des 14 jours, cours, ouverture et fermeture du menu mobile ; absence de débordement horizontal constatée sur les pages contrôlées.

Aucune erreur JavaScript signalée par la console pendant ces parcours. Les essais ne modifient pas la progression personnelle d’Evan.

## Limites des vérifications

La présence de parole est vérifiée pour chaque fichier ; une écoute humaine exhaustive de plus de trois heures n’a pas été effectuée. Les huit examens n’ont pas été passés pendant deux heures réelles chacun : les frontières temporelles sont aussi vérifiées avec une horloge simulée. Les contrôles structurels ne certifient pas l’absence de toute ambiguïté linguistique, ni un étalonnage TOEIC. Les variantes réutilisent des familles de situations ; les six photos sont partagées.

Le service OpenAI réel n’a pas été appelé ; sa disponibilité dépend de la clé, du modèle et des crédits configurés par l’utilisateur. Le mode local a été testé de bout en bout. Aucune validation de compatibilité sur tous les navigateurs, ni audit d’accessibilité exhaustif, n’est revendiqué.

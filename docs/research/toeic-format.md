# Le format de référence

Recherche du 13 octobre 2026. [ETS : structure](https://www.ets.org/toeic/about/listening-reading.html), [manuel du candidat, pp. 1–5 et exemples](https://www.ets.org/content/dam/ets-org/pdfs/toeic/toeic-listening-reading-test-examinee-handbook.pdf), [ETS Global : variantes](https://www.etsglobal.org/fr/fr/test-type-family/test-toeic-listening-and-reading).

## Structure classique

| Partie | Support | Questions |
|---|---|---:|
| 1 | Photographie, quatre propositions orales | 6 |
| 2 | Question et trois réponses orales | 25 |
| 3 | Treize conversations, trois questions chacune | 39 |
| 4 | Dix exposés, trois questions chacun | 30 |
| 5 | Phrase avec élément manquant | 30 |
| 6 | Textes à compléter | 16 |
| 7 | Dix textes simples : 29 questions ; cinq ensembles multiples : 25 | 54 |

Listening : 100 questions, environ 45 minutes. Reading : 100 questions, 75 minutes. Les formalités administratives peuvent ajouter environ trente minutes. Les stimuli portent notamment sur bureaux, achats, déplacements et services. Certaines tâches croisent audio et graphique ou plusieurs documents. Les questions évaluent détails, sens global, implicite et relations entre informations.

La conversion officielle utilise un étalonnage propre aux formes du test. Une simple règle « bonnes réponses × points » ne la reproduit pas. Chaque section est notée de 5 à 495. Sources : ETS ci-dessus.

## Multistage Adaptive

ETS Global distingue la version d’environ une heure : Listening 45 questions/25 minutes et Reading 45 questions/environ 37 minutes. Les résultats d’une unité déterminent la suivante. Notre moteur pédagogique adaptatif n’est pas ce test ; aucun simulateur MSA n’est annoncé.

## Notre implémentation et ses limites

- Structure classique 6/25/39/30/30/16/54 contrôlée pour les huit séries.
- Échéances serveur : passage au Reading à 45 minutes, fin à 120 minutes. La page rechargée reprend l’échéance, pas un nouveau compte à rebours.
- En Listening, le temps courant détermine le passage et la position audio. Le serveur refuse les réponses d’un autre passage et les retours à la section après 45 minutes.
- En Reading, navigation libre, réponses modifiables et repères.
- Réponses et explications masquées dans les données de séance jusqu’à la correction.
- Matériel original : voix synthétiques, photographies synthétiques. Les pauses sont calculées pour remplir les 45 minutes. Ce n’est pas une bande officielle.
- Les textes sont généralement plus courts que les documents les plus exigeants du vrai test ; les variantes renforcent des compétences ciblées mais ne constituent pas un étalonnage.
- Le résultat est un nombre de réponses correctes et un pourcentage. Aucun score officiel prédit.
- Les styles des photos et les familles de situations se répètent. Utiliser aussi les exemples officiels liés dans les ressources.

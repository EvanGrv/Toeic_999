# Méthodes retenues et traduction en produit

Recherche : 13 octobre 2026. Les seuils du logiciel sont des choix pédagogiques transparents, pas des paramètres scientifiquement validés pour ce seul utilisateur.

| Méthode | Base documentaire | Traduction concrète |
|---|---|---|
| Rappel actif | [Dunlosky et al., 2013](https://acs.ist.psu.edu/ist521/dunloskyRMNW13.pdf) | Répondre avant correction ; rappeler le sens avant de retourner une carte |
| Espacement | Même revue ; [Rawson et al., 2013](https://eric.ed.gov/?id=EJ1036741) | Échec : nouvelle tentative après dix minutes ; succès : un jour, trois jours, puis intervalle multiplié par facilité |
| Alternance | Dunlosky et al. | Compétences mélangées ; un passage et ses questions restent inséparables |
| Suivi de maîtrise | [Abdelrahman et al., revue du knowledge tracing](https://arxiv.org/abs/2201.06953) | État par compétence, fondé sur les dernières réponses à des items distincts |
| Distracteurs | [Haladyna et Downing : recommandations](https://testing.byu.edu/handbooks/Multiple-Choice%20Item%20Writing%20Guidelines%20-%20Haladyna%20and%20Downing.pdf) | Une clé unique, erreurs plausibles, vérification grammaticale et contextuelle |
| Variété orale | [Travaux sur l’intelligibilité bilingue](https://www.cambridge.org/core/books/abs/cambridge-handbook-of-bilingual-phonetics-and-phonology/bilingual-speech-intelligibility/7B5DD87307F0C79F80C7EEB225A95DCB) | Plusieurs voix, alternance des interlocuteurs et accents, transcription après réponse |

La revue de Dunlosky soutient particulièrement les tests de récupération et la pratique distribuée. Les effets de l’interleaving dépendent des tâches et des connaissances déjà acquises ; il ne faut pas présenter toute alternance comme une garantie universelle. Le logiciel évite donc de découper arbitrairement des documents ou conversations.

## Heuristiques implémentées

- Départ : Reading 65 %, Listening 35 %, selon la demande et les scores déclarés.
- Recalcul uniquement après 30 réponses Reading et 20 Listening **distinctes**.
- Erreurs lissées avec deux pseudo-échecs et deux pseudo-succès ; partage Reading borné entre 35 et 80 %.
- Maîtrise par compétence : `(correctes + 2) / (distinctes + 4)`. Confiance descriptive, sans intervalle statistique trompeur.
- Questions inédites prioritaires, puis faiblesse, adéquation de difficulté et une composante d’exploration.
- Réponses incertaines : révision même si elles sont correctes.
- Défis C1/C2 : au moins quarante questions B2/C1 distinctes et 85 % de réussite. Ce seuil ne prouve pas un niveau C2.
- Une réponse répétée au même item ne multiplie pas artificiellement l’échantillon de calibration. Les variantes restent toutefois corrélées : limite explicitement documentée.

## Temps de lecture

Les budgets 10/8/57 minutes pour les parties 5/6/7 sont un **point de départ d’entraînement**, pas une règle ETS. Le cours recommande de repérer le type de document, lire les questions, rechercher une preuve et conserver une marge de relecture. Les temps observés doivent guider l’ajustement.

## Validation future

Des résultats longitudinaux, des réponses de plusieurs apprenants et une expertise linguistique seraient nécessaires pour calibrer la difficulté, la discrimination des items et une éventuelle estimation de score. La présente version ne prétend pas disposer de ces données.

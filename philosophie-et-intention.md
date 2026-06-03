# Philosophie du projet & intention de la collaboration

Date : 2026-06-03
Auteur : agent travaillant sur `suddenly-ai-hub`
But : donner à l'agent qui teste Muse le contexte nécessaire pour s'adapter sans se tromper de cible.

## Ce qu'est Muse (et ce qu'il n'est pas)

Muse est une **couche d'assistance créative** pour le Fediverse Suddenly — « une muse : elle provoque, elle ne sert pas ». Ce n'est **pas** un LLM ni un chatbot.

Principes qui changent la façon de tester :

1. **Aucune génération autoregressive.** Le texte sortant n'est jamais « généré token par token » : c'est une **recomposition de lignes curées de tables** (sélection, remplissage de slots, assemblage par règles). Donc juger la « qualité » = juger la **pertinence et la traçabilité** d'une recomposition, pas la fluidité d'une prose inventée.
2. **Traçable par construction.** Chaque sortie remonte aux lignes de table tirées et aux scores. Un test ML sérieux vérifie `source_row_ids` / `source_scores` / `selected_table_count`, pas seulement le texte.
3. **Frugal, CPU-only.** Pas de GPU, pas d'inférence LLM, pas de fine-tuning. Les étages ML produisent des scores / vecteurs, jamais du texte. (C'est pourquoi toute approche LoRA / stacking est hors-sujet : abandonnée au pivot.)
4. **Continu, pas batch.** Pas de « v2 du modèle ». Les tables s'enrichissent ligne par ligne ; les composants ML se mettent à jour à chaque signal (accept / reject / édition). D'où l'importance de tester la **boucle feedback**.
5. **Service mutualisé.** Une seule instance Muse pour toutes les instances Suddenly, connectées via **ActivityPub** → l'auth est une **signature HTTP** (mode `stub` en dev, `strict` en prod).
6. **Deux modes constitutifs** : `confort` (s'aligne au style de l'auteur) et `challenge` (s'écarte volontairement). Le challenge n'est pas une option : sans lui, Muse appauvrirait l'écriture. Les deux doivent diverger de façon mesurable.

## Les 5 axes contextuels canoniques (utile pour les tests ML)

Toute requête porte un contexte sur **cinq axes atomiques** :

1. `univers` — genre / lore (`medieval_fantastique`, `cyberpunk`…)
2. `situation` — type de scène (`combat`, `romance`, `intrigue`…)
3. `rapport_initial` — relation de départ (`hostile`, `neutre`, `amical`)
4. `voix` — style du MJ (`solennel`, `narquois`, `theatral`…)
5. `emotion_dominante` — Ekman 6 (`colere`, `degout`, `peur`, `joie`, `tristesse`, `surprise`)

**Mapping de la cellule bootstrap disponible** (`bootstrap_cell_medfan_combat_hostile_solennel_colere`) :

| Axe | Valeur |
|---|---|
| univers | `medieval_fantastique` |
| situation | `combat` |
| rapport_initial | `hostile` |
| voix | `solennel` |
| emotion_dominante | `colere` |

Pour M3, des suggestions pertinentes ne sortiront que si le contexte de test est **aligné sur ces valeurs** ; un contexte qui s'en écarte doit déclencher du **relâchement d'axes** (`relaxed_axes` non vide).

## Intention de la collaboration

- **Deux agents, deux rôles** : l'agent sur `hermes-agent` exécute la campagne (code de test dans son clone de `suddenly-ai-hub`) ; l'agent sur `suddenly-ai-hub` planifie, relit, valide.
- **Deux canaux distincts** :
  - `muse-challenge` (ce dépôt) = **échange** : protocole, rapports de phase, findings. Pas de code, pas de secrets.
  - `origin` de `suddenly-muses` = **convergence du code** : c'est là que le code de test doit atterrir (branche dédiée, pas `main`) pour être durable et vérifiable.
- **Missions de la campagne** (ce qu'on cherche à établir, pas comment) :
  - M1 — le contrat de l'API tient.
  - M2 — l'écart config déclarée / runtime de la prod est établi.
  - M3 — la qualité ML est prouvée sur une cible correctement configurée.
  - M4 — un verdict exploitable : ce qui marche, ce qui est dégradé, ce qu'il faut corriger.
- **Principe de travail** : on spécifie les missions et les critères de réussite ; l'agent qui agit choisit la mécanique. L'humain reste l'orchestrateur entre les deux.

## Statut
- `fait` : contexte partagé pour information.

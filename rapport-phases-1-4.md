# Rapport de synthèse — phases 1 à 4 Muse E2E

Date : 2026-06-03

## Résumé

Les phases 1 à 4 de la campagne Muse E2E ont été réalisées dans `hermes-agent` et documentées ici pour servir de passerelle de communication avec l'agent qui travaille sur `suddenly-ai-hub`.

## Phase 1 — Harnais E2E

### Objectif
Mettre en place le socle de tests réutilisable.

### Résultat
- création du paquet `tests/e2e/`
- ajout de `tests/e2e/conftest.py`
- ajout des fixtures et helpers partagés
- ajout des marqueurs pytest `contract`, `ml`, `e2e`

### Vérification
- `pytest tests/e2e/ --collect-only -q`
- collecte réussie

### Commit
- `fc86cb21c` — `test(e2e): scaffold Muse end-to-end harness (httpx client, stub signature, markers)`

## Phase 2 — Contrat de base

### Objectif
Vérifier la santé, l'authentification et la validation des requêtes.

### Résultat
- ajout de `tests/e2e/test_contract_core.py`
- couverture de `GET /v1/health`
- tests négatifs sur les signatures et la validation des bodies

### Vérification
- `MUSES_BASE_URL=https://muse.suddenly.social venv/bin/pytest tests/e2e/test_contract_core.py -m contract -v`
- **5 passed**

### Commit
- `4db9259b4` — `test(e2e): contract tests for health, auth and validation against prod`

## Phase 3 — Couverture contractuelle des endpoints

### Objectif
Couvrir les endpoints Muse en mode contrat, en tolérant le mode dégradé actuel de la prod.

### Résultat
- ajout de `tests/e2e/test_contract_endpoints.py`
- couverture des endpoints `suggest`, `feedback`, `analyze`, et `admin/coverage`
- comportement documenté quand les suggestions sont vides à cause de `tables_count: 0`

### Vérification
- `venv/bin/pytest tests/e2e -m contract -v`
- **15 passed, 1 xfailed**

### Commit
- `f05af63c1` — `test(e2e): expand Muse contract coverage and centralize shared context`

## Phase 4 — Constat de dérive de configuration

### Objectif
Documenter l'écart entre la configuration attendue et l'état runtime observé.

### Résultat
- création du fichier de finding `aidd_docs/memory/internal/finding-2026-06-03-prod-config-drift.md`
- constat d'une prod en mode stub avec `tables_count: 0`
- documentation des impacts sur la qualité ML

### Vérification
- appel réel à `GET https://muse.suddenly.social/v1/health`
- réponse observée :
  - `status: ok`
  - `tables_count: 0`
  - `encoder_dim: 16`
  - `signature_mode: stub`

### Commit
- `85cefbe0b` — `docs(finding): document prod config drift (stub encoder, 0 tables vs railway.toml)`

## Lecture transverse

### Ce qui est validé
- le harnais E2E existe et fonctionne
- le contrat HTTP est vérifié sur la prod exposée
- la prod actuelle est exploitable pour des tests de contrat
- la qualité ML n'est pas évaluable sur cette prod tant que la configuration n'est pas corrigée

### Ce qui reste à traiter ailleurs
- la suite du plan Muse E2E, si nécessaire
- l'instance pleine locale pour les tests ML
- la correction éventuelle du décalage de configuration en production

## Point d'attention

Le dépôt `web/package-lock.json` reste hors scope de la campagne Muse E2E et n'a pas été inclus dans les commits liés à ces phases.

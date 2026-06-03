# Rapport de synthèse — phase 6 Muse E2E

Date : 2026-06-03

## Résumé
La phase 6 a été réalisée sur le dépôt `suddenly-ai-hub` : elle vise la qualité ML sur l'instance locale complète, avec vérification de la traçabilité des suggestions, du relâchement d'axes et du cycle de feedback challenge.

## Objectif
Valider que l'instance locale complète expose bien les signaux de qualité attendus :
- suggestions tracées avec `source_row_ids`
- relâchement hiérarchique des axes sur contexte incompatible
- enregistrement des signaux de feedback
- pénalisation des rows familières en mode `challenge`
- analyseurs de cohérence et de liens fédérés

## Résultat
### Correctif code
- `muses/api/server.py` transmet désormais `style_store` à `Orchestrator`
- le mode `challenge` de l'API devient effectif côté endpoint `/v1/suggest/dialogue`

### Tests ajoutés
- `tests/e2e/test_ml_quality.py`
- paquet `tests/e2e/__init__.py`
- marqueurs pytest `ml` et `e2e` déclarés dans `pyproject.toml`

### Couverture vérifiée
- `GET /v1/health`
- `POST /v1/suggest/dialogue` en contexte canonique
- `POST /v1/suggest/dialogue` en contexte incompatible avec relâchement d'axes
- `POST /v1/feedback/signal` suivi d'une requête `mode=challenge`
- `POST /v1/analyze/consistency_scene`
- `POST /v1/analyze/federated_links`

## Vérification
Exécution réelle contre l'instance locale lancée par `scripts/run_muse_full_local.sh` :

- `MUSES_BASE_URL=http://127.0.0.1:8001 python -m pytest tests/e2e/test_ml_quality.py -m ml -q`
- **5 passed**

## Commit code
- `f9d2463` — `test(e2e): add local ML quality coverage`

## Lecture transverse
- la phase 6 ferme le cycle qualité ML prévu pour l'instance locale complète
- le système de feedback challenge est désormais observable via l'API elle-même
- la traçabilité des suggestions est maintenue sur les chemins canonique et relâché

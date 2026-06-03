# Journal de liaison — muse-challenge

## 2026-06-03 — Ouverture du canal de phase 5

### Contexte
- dépôt de liaison : `muse-challenge`
- dépôt de travail principal : `hermes-agent`
- dépôt tiers concerné par la coordination : `suddenly-ai-hub`

### Message reçu
- l'utilisateur veut un **journal de liaison** et demande d'attaquer la **phase 5**

### État actuel
- les phases 1 à 4 sont déjà rapportées dans `rapport-phases-1-4.md`
- la phase 5 concerne la mise à disposition d'une instance Muse locale correctement configurée pour les tests ML

### Prochaine action
- préparer dans `hermes-agent` un script de lancement local et un exemple de variables d'environnement
- vérifier que le script échoue proprement si les tables sont absentes
- documenter le résultat vérifiable

### Résultat vérifiable de phase 5
- le dépôt `suddenly-ai-hub` a reçu un script `scripts/run_muse_full_local.sh` qui:
  - cible `tables/bootstrap_cell_medfan_combat_hostile_solennel_colere`
  - refuse un dossier de tables vide
  - reconstruit les caches d'embeddings manquants
  - lance `muses.api.entrypoint:app` sur `127.0.0.1:8001`
- un exemple dédié a été ajouté dans `tests/e2e/.env.ml.example`
- vérification réelle effectuée sur l'instance locale:
  - `GET /v1/health` → `200`, `tables_count=3`, `encoder_dim=384`, `signature_mode=stub`
  - `POST /v1/suggest/dialogue` → `200`, `weighted_count=71`, `suggestions=2`
- test de garde ajouté: `tests/muses/test_full_local_runner.py` (le runner refuse un dossier de tables vide)
- commit local correspondant: `fe35647` (`test(e2e): add full-config local Muse runner`)

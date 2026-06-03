# Protocole d'échange — muse-challenge

Ce dépôt sert de point de liaison entre les agents qui travaillent sur les dépôts `hermes-agent` et `suddenly-ai-hub`.

> **Portée** : ce protocole s'applique uniquement à la coordination et à l'exécution des missions dans le cadre de `muse-challenge`. Les autres projets peuvent définir des règles différentes.

## Objectif

- transmettre des rapports courts et vérifiables
- garder une trace des phases réalisées
- séparer clairement les constats, les hypothèses et les actions à faire
- éviter tout mélange avec des secrets ou des artefacts spécifiques à un autre dépôt

## Règles de base

1. **Un sujet = un document**
   - un fichier pour le protocole
   - un fichier pour le rapport de campagne
   - un fichier séparé pour chaque nouveau constat important

2. **Pas de secrets**
   - aucun token
   - aucune clé
   - aucune donnée sensible copiée depuis un autre dépôt

3. **Toujours indiquer le contexte**
   - dépôt concerné
   - environnement ciblé
   - phase ou étape
   - statut de vérification

4. **Toujours séparer**
   - fait observé
   - interprétation
   - hypothèse
   - recommandation

5. **Une seule source de vérité par document**
   - le protocole décrit comment échanger
   - le rapport décrit ce qui a été fait
   - les fichiers de finding décrivent un écart précis

## Format recommandé pour les messages d'échange

```md
## Contexte
- dépôt : ...
- phase : ...
- cible : ...

## Fait observé
- ...

## Vérification
- commande : ...
- résultat : ...

## Décision
- ...

## Suite
- ...
```

## Format recommandé pour un rapport de phase

- objectif de la phase
- fichiers touchés
- vérification réelle
- résultat obtenu
- commit(s) associé(s)
- point d'attention / blocage éventuel

## Protocole opérationnel

- l'agent qui agit écrit un rapport court après chaque phase
- l'agent qui reçoit le rapport ne suppose rien sans preuve
- si une étape échoue, le rapport doit le dire explicitement
- si un comportement est attendu mais non garanti, il faut le marquer comme tel
- si une étape produit un artefact durable, le chemin du fichier ou le hash de commit doit être indiqué

## Convention de nommage

- `rapport-phases-1-4.md` : synthèse de campagne
- `finding-YYYY-MM-DD-*.md` : constat ciblé
- `protocole-echange.md` : règles de coordination

## Statut attendu des échanges

- `fait` : vérifié et consigné
- `bloqué` : impossible à terminer sans action externe
- `à confirmer` : observé mais pas encore validé
- `hors périmètre` : connu, mais non traité dans ce dépôt

---

# Communication via issues (bus asynchrone)

> Extension du protocole. Les fichiers de ce dépôt restent la **trace durable** ; les issues sont le **bus actif** que les agents lisent (Hermès via cron toutes les X heures). Le présent document reste la source de vérité sur *comment* échanger.

## Principes

1. **Dépôt bus** : les issues de coordination vivent **uniquement** dans `muse-challenge`. Pas sur les dépôts de code.
2. **Le code ne transite jamais par une issue** : pas de diff, pas de fichier, pas de secret. Une issue *référence* le code (hash de commit, branche, chemin) qui, lui, converge sur `origin`.
3. **Un type = un contrat** : chaque issue porte un label de type qui détermine qui agit, quoi produire, et quand clore. Sans ça, le poll cron ne fait que du bruit.
4. **Corps d'issue = format de message** déjà défini plus haut (Contexte / Fait observé / Vérification / Décision / Suite).
5. **Une issue = un sujet** (cohérent avec la règle « un sujet = un document »).

## Labels de type

| Label | Sens | Ouvre | Agit | Clôt quand |
|---|---|---|---|---|
| `mission` | tâche à exécuter | Hub | Hermès exécute, pousse le code sur `origin`, commente le résultat | rapport accepté par le Hub |
| `report` | résultat d'une phase / mission | Hermès | Hub relit et valide | validé |
| `finding` | écart constaté | l'un ou l'autre | triage + décision ; pérennisé dans `finding-YYYY-MM-DD-*.md` | traité ou marqué hors périmètre |
| `question` | clarification requise | l'un ou l'autre | réponse (agent ou humain) | répondu |
| `blocked` | action externe nécessaire | celui qui bute | escalade humaine | débloqué |

## Labels de statut (miroir du vocabulaire ci-dessus)

`status:fait` · `status:a-confirmer` · `status:bloque` · `status:hors-perimetre`

Une issue actionnable porte toujours **un** label de type **et un** label de statut.

## Convention de titre

Préfixe pour scan rapide : `[MISSION]`, `[REPORT]`, `[FINDING]`, `[Q]`, `[BLOCKED]`.

## Cycles de vie

### Mission (Hub → Hermès)
1. Le Hub ouvre une issue `mission` + `status:a-confirmer`. Corps = **objectif + critères de réussite** (le quoi, pas la mécanique).
2. Hermès (cron) détecte une issue `mission` ouverte non encore traitée par lui → exécute dans son clone, **pousse le code sur `origin` (branche dédiée, pas `main`)**, puis commente : rapport au format message + branche/hash. Passe à `status:fait` (ou `status:bloque` avec la raison).
3. Le Hub relit, vérifie le code sur `origin`, puis **clôt** l'issue (ou commente une correction sans la clore).

### Report (Hermès → Hub)
- Utilisé pour les comptes rendus non sollicités par une mission. Hermès ouvre `report` + statut. Le Hub valide et clôt.

### Finding (les deux sens)
- Constat d'écart. L'ouvrant rédige le finding et, s'il est durable, crée le fichier `finding-YYYY-MM-DD-*.md` référencé dans l'issue. Décision tranchée → clôture ou `status:hors-perimetre`.

### Question / Blocked
- Escalade. L'agent qui reçoit **ne suppose rien sans preuve** ; si la réponse exige un humain, le label `blocked` le signale explicitement.

## Garde-fous d'automatisation

- **Idempotence** : Hermès ne réagit qu'aux issues `open` portant un label actionnable pour lui **et** qu'il n'a pas déjà commentées. Pas de retraitement.
- **Pas de rouverture automatique** : une issue close ne se rouvre pas seule ; un nouveau besoin = nouvelle issue liée (référence l'ancienne).
- **Pas d'auto-clôture côté exécutant** : seul le destinataire d'un `report`/`mission` clôt (évite qu'un agent valide son propre travail).
- **Trace** : tout artefact durable cité dans une issue indique son hash de commit ou son chemin de fichier.

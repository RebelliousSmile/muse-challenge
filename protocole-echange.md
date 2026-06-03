# Protocole d'échange — muse-challenge

Ce dépôt sert de point de liaison entre les agents qui travaillent sur les dépôts `hermes-agent` et `suddenly-ai-hub`.

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

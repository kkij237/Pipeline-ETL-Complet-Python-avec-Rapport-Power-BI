# S3 Pipeline Etl

**Parcours** : Formuloo Data  
**Niveau** : Tous niveaux  
**Branche de livraison** : ta branche `prenom-nom`

## Convention de branchement — OBLIGATOIRE

```bash
git clone https://gitlab.formuloo.com/formuloo-data/mini-projets/s3-pipeline-etl.git
git checkout develop
git pull origin develop
git checkout -b prenom-nom   # ex: jean-dupont, sans accents, minuscules
```

Pour chaque feature ou tâche, crée une sous-branche :
```bash
git checkout -b prenom-nom/feature/nom-feature
# ... travail ...
git checkout prenom-nom
git merge prenom-nom/feature/nom-feature
git push origin prenom-nom
```

**Ta branche `prenom-nom` est ta branche de livraison — c'est ce qui sera évalué.**  
Ne jamais pousser directement sur `develop` ou `main`.

# IT Parc - Module Odoo 18
## Gestion de Parc Informatique - TECHPARK CI

Module personnalisé Odoo 18 pour la gestion complète du parc informatique de TECHPARK CI.

---

## Prérequis

- Odoo 18.0
- Python 3.11+
- PostgreSQL
- wkhtmltopdf (pour les rapports PDF)
- xlsxwriter : pip install xlsxwriter

---

## Installation

### 1. Copier le module

Copier le dossier it_parc dans votre dossier custom-addons :

cp -r it_parc/ /chemin/vers/custom-addons/

### 2. Configurer odoo.conf

Ajouter le chemin dans addons_path :

addons_path = ...,/chemin/vers/custom-addons

### 3. Installer les dépendances Python

pip install xlsxwriter

### 4. Mettre à jour la liste des modules

Dans Odoo : Apps > Mettre à jour la liste

### 5. Installer le module

Rechercher "IT Parc" et cliquer sur Installer.

### 6. Charger les données de démo

Le module charge automatiquement les données de démo à l'installation.

---

## Fonctionnalités

| N° | Fonctionnalité | Description |
|----|----------------|-------------|
| 01 | Équipements | Gestion complète avec workflow |
| 02 | Affectations | Historique des affectations |
| 03 | Interventions | Suivi des maintenances |
| 04 | Contrats | Gestion fournisseurs |
| 05 | Alertes | Notifications automatiques |
| 06 | Import CSV | Import en masse |
| 07 | Rapports PDF | 3 rapports QWeb |
| 08 | Exports Excel | 3 exports xlsxwriter |
| 09 | Dashboard OWL | Tableau de bord |

---

## Groupes utilisateurs

| Groupe | Droits |
|--------|--------|
| IT Technicien | Lecture + création interventions |
| IT Manager | Accès complet |

---

## URLs importantes

- Interface : http://localhost:8069/odoo
- Module : Menu IT Parc

---

## Mise à jour du module

python odoo-bin -d techpark -u it_parc

---

## Auteur

TECHPARK CI - Abidjan, Côte d'Ivoire

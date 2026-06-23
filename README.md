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

## Installation pas a pas

1. Copier le dossier it_parc dans le repertoire addons/ d'Odoo 18 :

       cp -r it_parc/ /chemin/vers/odoo/custom-addons/

2. Installer la dependance Python xlsxwriter :

       pip install xlsxwriter --break-system-packages

3. Redemarrer Odoo avec la mise a jour du module :

       python odoo-bin -c odoo.conf -d techpark -u it_parc

4. Activer le module dans Odoo :

   Aller dans Apps > Mettre a jour la liste > Rechercher "IT Parc" > Installer

5. Charger les donnees de demonstration :

   Les donnees de demo sont chargees automatiquement depuis it_parc_demo.xml
   lors de l'installation. Elles incluent des equipements, interventions et contrats
   d'exemple pour tester toutes les fonctionnalites du module.

---

## Fonctionnalites

- 01 - Equipements : Gestion complete avec workflow (brouillon, affecte, maintenance, retire)
- 02 - Affectations : Historique des affectations par employe
- 03 - Interventions : Suivi des maintenances avec vue calendrier
- 04 - Contrats : Gestion fournisseurs avec alertes d'expiration
- 05 - Alertes : Notifications automatiques (garanties et contrats)
- 06 - Import CSV : Import en masse d'equipements (delimiteur ; ou ,)
- 07 - Rapports PDF : 3 rapports QWeb (fiche, inventaire, historique maintenances)
- 08 - Exports Excel : 3 exports xlsxwriter (inventaire, couts, contrats expirants)
- 09 - Dashboard OWL : Tableau de bord interactif avec KPIs et graphiques

---

## Groupes utilisateurs

- IT Technicien : Lecture + creation interventions
- IT Manager : Acces complet

---

## URLs importantes

- Interface : http://localhost:8069/odoo
- Module : Menu IT Parc

---

## Mise a jour du module

    python odoo-bin -c odoo.conf -d techpark -u it_parc

---

## Auteur

TECHPARK CI - Abidjan, Cote d'Ivoire

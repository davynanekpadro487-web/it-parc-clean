from odoo import models, api

class ItDashboard(models.Model):
    _name = 'it.dashboard'
    _description = 'Dashboard IT Parc'

    @api.model
    def get_dashboard_data(self):
        from datetime import date, timedelta
        today = date.today()
        limite_30j = today + timedelta(days=30)
        limite_60j = today + timedelta(days=60)

        Equipement = self.env['it.equipement']
        Intervention = self.env['it.intervention']
        Contrat = self.env['it.contrat']
        Alerte = self.env['it.alerte']

        # KPI 1 - Total équipements
        total_equipements = Equipement.search_count([])
        
        # KPI 2 - Équipements par état
        par_etat = {}
        for etat in ['brouillon', 'affecte', 
                     'maintenance', 'retire']:
            par_etat[etat] = Equipement.search_count([
                ('state', '=', etat)
            ])

        # KPI 3 - Garanties expirant dans 30 jours
        garanties_critiques = Equipement.search_count([
            ('date_garantie', '!=', False),
            ('date_garantie', '<=', str(limite_30j)),
            ('date_garantie', '>=', str(today)),
            ('state', '!=', 'retire'),
        ])

        # KPI 4 - Contrats expirant dans 60 jours
        contrats_critiques = Contrat.search_count([
            ('date_fin', '<=', str(limite_60j)),
            ('date_fin', '>=', str(today)),
            ('state', '=', 'actif'),
        ])

        # KPI 5 - Alertes nouvelles
        alertes_nouvelles = Alerte.search_count([
            ('state', '=', 'nouvelle')
        ])

        # KPI 6 - Coût total maintenance
        interventions = Intervention.search([])
        cout_total = sum(interventions.mapped('cout'))

        # Données graphique - équipements par catégorie
        categories = [
            'poste_travail', 'serveur', 'imprimante',
            'reseau', 'telephone', 'autre'
        ]
        labels_cat = [
            'Postes de travail', 'Serveurs',
            'Imprimantes', 'Réseau',
            'Téléphones IP', 'Autres'
        ]
        data_categories = []
        for cat in categories:
            nb = Equipement.search_count([
                ('categorie', '=', cat)
            ])
            data_categories.append(nb)

        # Données graphique - interventions par mois
        from collections import defaultdict
        interventions_par_mois = defaultdict(int)
        for inter in interventions:
            if inter.date_debut:
                mois = inter.date_debut.strftime('%Y-%m')
                interventions_par_mois[mois] += 1
        
        mois_sorted = sorted(
            interventions_par_mois.keys()
        )[-6:]
        data_interventions = {
            'labels': mois_sorted,
            'data': [
                interventions_par_mois[m] 
                for m in mois_sorted
            ]
        }

        return {
            'kpis': {
                'total_equipements': total_equipements,
                'par_etat': par_etat,
                'garanties_critiques': garanties_critiques,
                'contrats_critiques': contrats_critiques,
                'alertes_nouvelles': alertes_nouvelles,
                'cout_total_maintenance': cout_total,
            },
            'graphiques': {
                'categories': {
                    'labels': labels_cat,
                    'data': data_categories,
                },
                'interventions': data_interventions,
            }
        }

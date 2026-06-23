from odoo import models, api
from datetime import date, timedelta

class ItCronAlertes(models.Model):
    _name = 'it.equipement'
    _inherit = 'it.equipement'

    @api.model
    def cron_generer_alertes(self):
        delai = 30
        today = date.today()
        limite = today + timedelta(days=delai)

        # Alertes garanties
        equipements = self.search([
            ('date_garantie', '!=', False),
            ('date_garantie', '<=', str(limite)),
            ('date_garantie', '>=', str(today)),
            ('state', '!=', 'retire'),
        ])
        for eq in equipements:
            existing = self.env['it.alerte'].search([
                ('equipement_id', '=', eq.id),
                ('type_alerte', '=', 'garantie'),
                ('state', '=', 'nouvelle'),
            ])
            if not existing:
                self.env['it.alerte'].create({
                    'name': f'Garantie expirante - {eq.name}',
                    'type_alerte': 'garantie',
                    'equipement_id': eq.id,
                    'date_expiration': eq.date_garantie,
                    'jours_restants': eq.jours_garantie_restants,
                    'message': f'La garantie de {eq.name} '
                               f'expire le {eq.date_garantie}',
                })

        # Alertes contrats
        contrats = self.env['it.contrat'].search([
            ('date_fin', '<=', str(limite)),
            ('date_fin', '>=', str(today)),
            ('state', '=', 'active'),
        ])
        for ct in contrats:
            existing = self.env['it.alerte'].search([
                ('contrat_id', '=', ct.id),
                ('type_alerte', '=', 'contrat'),
                ('state', '=', 'nouvelle'),
            ])
            if not existing:
                self.env['it.alerte'].create({
                    'name': f'Contrat expirant - {ct.name}',
                    'type_alerte': 'contrat',
                    'contrat_id': ct.id,
                    'date_expiration': ct.date_fin,
                    'jours_restants': ct.jours_restants,
                    'message': f'Le contrat {ct.name} '
                               f'expire le {ct.date_fin}',
                })

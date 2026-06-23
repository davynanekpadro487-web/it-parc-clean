from odoo import models, fields, api

class WizardScanAlertes(models.TransientModel):
    _name = 'wizard.scan.alertes'
    _description = 'Wizard scan des alertes'

    delai_jours = fields.Integer(
        string='Délai d\'alerte (jours)',
        default=30,
        help='Générer des alertes pour les garanties '
             'et contrats expirant dans ce délai'
    )
    nb_alertes_creees = fields.Integer(
        string='Alertes créées', readonly=True
    )
    rapport = fields.Text(
        string='Rapport', readonly=True
    )

    def action_scanner(self):
        from datetime import date, timedelta
        today = date.today()
        limite = today + timedelta(days=self.delai_jours)
        nb = 0
        rapport_lines = []

        # Scanner les garanties
        equipements = self.env['it.equipement'].search([
            ('date_garantie', '!=', False),
            ('date_garantie', '<=', str(limite)),
            ('date_garantie', '>=', str(today)),
            ('state', '!=', 'retire'),
        ])
        for eq in equipements:
            # Vérifier si alerte déjà existante
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
                nb += 1
                rapport_lines.append(
                    f'✓ Garantie: {eq.name} - '
                    f'{eq.jours_garantie_restants} jours'
                )

        # Scanner les contrats
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
                nb += 1
                rapport_lines.append(
                    f'✓ Contrat: {ct.name} - '
                    f'{ct.jours_restants} jours'
                )

        self.nb_alertes_creees = nb
        self.rapport = '\n'.join(rapport_lines) if rapport_lines \
            else 'Aucune nouvelle alerte à générer.'
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.scan.alertes',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

class WizardRenouvellementContrat(models.TransientModel):
    _name = 'wizard.renouvellement.contrat'
    _description = 'Wizard renouvellement contrat'

    contrat_id = fields.Many2one(
        'it.contrat', string='Contrat',
        required=True
    )
    ancienne_date_fin = fields.Date(
        string='Ancienne date fin', readonly=True
    )
    nouvelle_date_debut = fields.Date(
        string='Nouvelle date début',
        default=fields.Date.today
    )
    duree_mois = fields.Integer(
        string='Durée (mois)', default=12
    )
    nouvelle_date_fin = fields.Date(
        string='Nouvelle date fin',
        compute='_compute_nouvelle_date_fin',
        store=True
    )
    nouveau_montant = fields.Float(
        string='Nouveau montant (FCFA)'
    )

    @api.onchange('contrat_id')
    def _onchange_contrat(self):
        if self.contrat_id:
            self.ancienne_date_fin = (
                self.contrat_id.date_fin
            )
            self.nouveau_montant = self.contrat_id.montant

    @api.depends('nouvelle_date_debut', 'duree_mois')
    def _compute_nouvelle_date_fin(self):
        for rec in self:
            if rec.nouvelle_date_debut and rec.duree_mois:
                rec.nouvelle_date_fin = (
                    rec.nouvelle_date_debut +
                    relativedelta(months=rec.duree_mois)
                )
            else:
                rec.nouvelle_date_fin = False

    def action_renouveler(self):
        self.contrat_id.write({
            'date_debut': self.nouvelle_date_debut,
            'date_fin': self.nouvelle_date_fin,
            'montant': self.nouveau_montant,
            'state': 'renouvele',
        })
        return {'type': 'ir.actions.act_window_close'}

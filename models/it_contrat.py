from odoo import models, fields, api

class ItContrat(models.Model):
    _name = 'it.contrat'
    _description = 'Contrat fournisseur'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Nom du contrat', required=True
    )
    fournisseur_id = fields.Many2one(
        'res.partner', string='Fournisseur',
        required=True
    )
    type_contrat = fields.Selection([
        ('maintenance', 'Maintenance'),
        ('licence', 'Licence'),
        ('support', 'Support'),
    ], string='Type', required=True)
    
    date_debut = fields.Date(
        string='Date début', required=True
    )
    date_fin = fields.Date(
        string='Date fin', required=True
    )
    montant = fields.Float(string='Montant (FCFA)')
    equipement_ids = fields.Many2many(
        'it.equipement', string='Équipements couverts'
    )
    
    jours_restants = fields.Integer(
        string='Jours restants',
        compute='_compute_jours_restants', store=True
    )
    state = fields.Selection([
        ('actif', 'Actif'),
        ('expire', 'Expiré'),
        ('renouvele', 'Renouvelé'),
    ], string='État', default='actif', tracking=True)

    @api.depends('date_fin')
    def _compute_jours_restants(self):
        from datetime import date
        for rec in self:
            if rec.date_fin:
                delta = rec.date_fin - date.today()
                rec.jours_restants = delta.days
            else:
                rec.jours_restants = 0

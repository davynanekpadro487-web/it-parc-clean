from odoo import models, fields

class ItAlerte(models.Model):
    _name = 'it.alerte'
    _description = 'Alerte garantie ou contrat'
    _order = 'date_alerte desc'

    name = fields.Char(string='Titre', required=True)
    type_alerte = fields.Selection([
        ('garantie', 'Fin de garantie'),
        ('contrat', 'Expiration contrat'),
    ], string='Type', required=True)
    
    equipement_id = fields.Many2one(
        'it.equipement', string='Équipement'
    )
    contrat_id = fields.Many2one(
        'it.contrat', string='Contrat'
    )
    date_alerte = fields.Date(
        string="Date d'alerte",
        default=fields.Date.today
    )
    date_expiration = fields.Date(
        string='Date expiration'
    )
    jours_restants = fields.Integer(
        string='Jours restants'
    )
    state = fields.Selection([
        ('nouvelle', 'Nouvelle'),
        ('traitee', 'Traitée'),
        ('ignoree', 'Ignorée'),
    ], default='nouvelle', string='État')
    message = fields.Text(string='Message')

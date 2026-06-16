from odoo import models, fields

class ItAffectation(models.Model):
    _name = 'it.affectation'
    _description = 'Historique des affectations'
    _order = 'date_affectation desc'

    equipement_id = fields.Many2one(
        'it.equipement', string='Équipement',
        required=True, ondelete='cascade'
    )
    employee_id = fields.Many2one(
        'hr.employee', string='Employé',
        required=True
    )
    department_id = fields.Many2one(
        'hr.department', string='Département'
    )
    date_affectation = fields.Date(
        string="Date d'affectation",
        default=fields.Date.today
    )
    date_retour = fields.Date(string='Date de retour')
    motif = fields.Text(string='Motif')
    actif = fields.Boolean(
        string='Affectation active', default=True
    )

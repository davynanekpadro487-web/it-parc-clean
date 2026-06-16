from odoo import models, fields, api

class WizardReaffectation(models.TransientModel):
    _name = 'wizard.reaffectation'
    _description = 'Wizard de réaffectation équipement'

    equipement_id = fields.Many2one(
        'it.equipement', string='Équipement',
        required=True
    )
    ancien_employee_id = fields.Many2one(
        'hr.employee', string='Ancien employé',
        readonly=True
    )
    nouvel_employee_id = fields.Many2one(
        'hr.employee', string='Nouvel employé',
        required=True
    )
    nouveau_department_id = fields.Many2one(
        'hr.department', string='Nouveau département'
    )
    motif = fields.Text(
        string='Motif de réaffectation', required=True
    )
    date_reaffectation = fields.Date(
        string='Date de réaffectation',
        default=fields.Date.today
    )

    @api.onchange('equipement_id')
    def _onchange_equipement(self):
        if self.equipement_id:
            self.ancien_employee_id = (
                self.equipement_id.employee_id
            )

    def action_confirmer(self):
        equipement = self.equipement_id
        
        # Clôturer l'ancienne affectation
        ancienne = self.env['it.affectation'].search([
            ('equipement_id', '=', equipement.id),
            ('actif', '=', True)
        ], limit=1)
        if ancienne:
            ancienne.write({
                'actif': False,
                'date_retour': self.date_reaffectation
            })
        
        # Créer la nouvelle affectation
        self.env['it.affectation'].create({
            'equipement_id': equipement.id,
            'employee_id': self.nouvel_employee_id.id,
            'department_id': self.nouveau_department_id.id,
            'date_affectation': self.date_reaffectation,
            'motif': self.motif,
            'actif': True,
        })
        
        # Mettre à jour l'équipement
        equipement.write({
            'employee_id': self.nouvel_employee_id.id,
            'department_id': self.nouveau_department_id.id,
            'state': 'affecte',
        })
        
        return {'type': 'ir.actions.act_window_close'}

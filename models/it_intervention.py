from odoo import models, fields, api

class ItIntervention(models.Model):
    _name = 'it.intervention'
    _description = 'Intervention de maintenance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_debut desc'

    name = fields.Char(
        string='Référence', readonly=True,
        default='Nouveau'
    )
    equipement_id = fields.Many2one(
        'it.equipement', string='Équipement',
        required=True
    )
    type_intervention = fields.Selection([
        ('corrective', 'Corrective'),
        ('preventive', 'Préventive'),
    ], string='Type', required=True,
       default='corrective')
    
    technicien_id = fields.Many2one(
        'hr.employee', string='Technicien'
    )
    date_debut = fields.Datetime(
        string='Date début', required=True,
        default=fields.Datetime.now
    )
    date_fin = fields.Datetime(string='Date fin')
    duree = fields.Float(
        string='Durée (heures)',
        compute='_compute_duree', store=True
    )
    cout = fields.Float(string='Coût (FCFA)')
    description = fields.Text(
        string='Description du problème'
    )
    rapport = fields.Text(
        string="Rapport d'intervention"
    )
    state = fields.Selection([
        ('planifie', 'Planifiée'),
        ('en_cours', 'En cours'),
        ('termine', 'Terminée'),
    ], default='planifie', string='État',
       tracking=True)

    @api.depends('date_debut', 'date_fin')
    def _compute_duree(self):
        for rec in self:
            if rec.date_debut and rec.date_fin:
                delta = rec.date_fin - rec.date_debut
                rec.duree = delta.total_seconds() / 3600
            else:
                rec.duree = 0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nouveau') == 'Nouveau':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'it.intervention'
                ) or 'Nouveau'
        return super().create(vals_list)

    def action_en_cours(self):
        self.write({'state': 'en_cours'})

    def action_termine(self):
        self.write({'state': 'termine'})


class ReportHistoriqueMaintenance(models.AbstractModel):
    _name = 'report.it_parc.report_historique_maintenance_document'
    _description = "Rapport historique des maintenances"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['it.intervention'].browse(docids)
        if not docs:
            docs = self.env['it.intervention'].search([])
        return {
            'doc_ids': docids,
            'doc_model': 'it.intervention',
            'docs': docs,
        }

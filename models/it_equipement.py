from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ItEquipement(models.Model):
    _name = 'it.equipement'
    _description = 'Équipement Informatique'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Nom', required=True, tracking=True
    )
    reference = fields.Char(
        string='Référence', readonly=True,
        default='Nouveau'
    )
    categorie = fields.Selection([
        ('poste_travail', 'Poste de travail'),
        ('serveur', 'Serveur'),
        ('imprimante', 'Imprimante'),
        ('reseau', 'Équipement réseau'),
        ('telephone', 'Téléphone IP'),
        ('autre', 'Autre'),
    ], string='Catégorie', required=True, tracking=True)
    
    numero_serie = fields.Char(
        string='Numéro de série', tracking=True
    )
    marque = fields.Char(string='Marque')
    modele = fields.Char(string='Modèle')
    valeur_achat = fields.Float(
        string="Valeur d'achat (FCFA)"
    )
    date_achat = fields.Date(string="Date d'achat")
    date_garantie = fields.Date(
        string='Fin de garantie', tracking=True
    )
    
    state = fields.Selection([
        ('brouillon', 'Brouillon'),
        ('affecte', 'Affecté'),
        ('maintenance', 'En maintenance'),
        ('retire', 'Retiré'),
    ], string='État', default='brouillon', 
       tracking=True)
    
    employee_id = fields.Many2one(
        'hr.employee', string='Employé affecté',
        tracking=True
    )
    department_id = fields.Many2one(
        'hr.department', string='Département',
        tracking=True
    )
    localisation = fields.Char(string='Localisation')
    
    intervention_ids = fields.One2many(
        'it.intervention', 'equipement_id',
        string='Interventions'
    )
    affectation_ids = fields.One2many(
        'it.affectation', 'equipement_id',
        string='Historique affectations'
    )
    
    nb_interventions = fields.Integer(
        string='Nb interventions',
        compute='_compute_nb_interventions'
    )
    cout_total_maintenance = fields.Float(
        string='Coût total maintenance',
        compute='_compute_cout_total'
    )
    jours_garantie_restants = fields.Integer(
        string='Jours garantie restants',
        compute='_compute_jours_garantie',
        search='_search_jours_garantie_restants'
    )

    @api.depends('intervention_ids')
    def _compute_nb_interventions(self):
        for rec in self:
            rec.nb_interventions = len(rec.intervention_ids)

    @api.depends('intervention_ids.cout')
    def _compute_cout_total(self):
        for rec in self:
            rec.cout_total_maintenance = sum(
                rec.intervention_ids.mapped('cout')
            )

    @api.depends('date_garantie')
    def _compute_jours_garantie(self):
        from datetime import date
        for rec in self:
            if rec.date_garantie:
                delta = rec.date_garantie - date.today()
                rec.jours_garantie_restants = delta.days
            else:
                rec.jours_garantie_restants = 0

    def _search_jours_garantie_restants(self, operator, value):
        from datetime import date, timedelta
        today = date.today()
        if operator in ('=', '!=', '<', '<=', '>', '>='):
            target_date = today + timedelta(days=value)
            # warranty_days = date_garantie - today
            # warranty_days operator value  =>  date_garantie - today operator value => date_garantie operator today + value
            return [('date_garantie', operator, target_date)]
        return []

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('reference', 'Nouveau') == 'Nouveau':
                vals['reference'] = self.env['ir.sequence'].next_by_code(
                    'it.equipement'
                ) or 'Nouveau'
        return super().create(vals_list)

    def action_affecter(self):
        self.state = 'affecte'

    def action_maintenance(self):
        self.state = 'maintenance'

    def action_retirer(self):
        self.state = 'retire'

    def action_brouillon(self):
        self.state = 'brouillon'

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ItContrat(models.Model):
    _name = 'it.contrat'
    _description = 'Contrat fournisseur'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    _ALLOWED_STATE_TRANSITIONS = {
        'active': {'expired'},
        'expired': {'renewed'},
        'renewed': set(),
    }

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
        ('active', 'Actif'),
        ('expired', 'Expiré'),
        ('renewed', 'Renouvelé'),
    ], string='État', default='active', tracking=True, copy=False)

    def action_expire(self):
        self.write({'state': 'expired'})
        return True

    def action_renew(self):
        self.write({'state': 'renewed'})
        return True

    def _get_state_label(self, state):
        return dict(self._fields['state'].selection).get(state, state)

    def _validate_state_transition(self, new_state):
        self.ensure_one()
        if self.state == new_state:
            return
        allowed_states = self._ALLOWED_STATE_TRANSITIONS.get(self.state, set())
        if new_state not in allowed_states:
            raise UserError(
                _("Vous ne pouvez pas passer de l'état « %s » à « %s ».")
                % (
                    self._get_state_label(self.state),
                    self._get_state_label(new_state),
                )
            )

    def _prepare_state_transition_vals(self, vals):
        self.ensure_one()
        new_state = vals.get('state')
        if not new_state or self.state == new_state:
            return vals

        self._validate_state_transition(new_state)

        vals = dict(vals)
        if (
            new_state == 'renewed'
            and self.state == 'expired'
            and self.date_fin
            and 'date_fin' not in vals
        ):
            vals['date_fin'] = self.date_fin + relativedelta(years=1)
        return vals

    def _log_state_change(self, new_state):
        self.ensure_one()
        self.message_post(
            body=_("Statut du contrat modifié vers « %s ».")
            % self._get_state_label(new_state)
        )

    def write(self, vals):
        if 'state' not in vals:
            return super().write(vals)

        old_states = {rec.id: rec.state for rec in self}
        new_state = vals['state']

        if len(self) == 1:
            vals = self._prepare_state_transition_vals(vals)
            result = super().write(vals)
            if old_states[self.id] != new_state:
                self._log_state_change(new_state)
            return result

        for rec in self:
            rec_vals = rec._prepare_state_transition_vals(dict(vals))
            super(ItContrat, rec).write(rec_vals)
            if old_states[rec.id] != new_state:
                rec._log_state_change(new_state)
        return True

    @api.depends('date_fin')
    def _compute_jours_restants(self):
        from datetime import date
        for rec in self:
            if rec.date_fin:
                delta = rec.date_fin - date.today()
                rec.jours_restants = delta.days
            else:
                rec.jours_restants = 0

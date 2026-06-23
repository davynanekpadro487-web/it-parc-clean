from odoo import _, models, fields
from odoo.exceptions import UserError


class ItAlerte(models.Model):
    _name = 'it.alerte'
    _description = 'Alerte garantie ou contrat'
    _order = 'date_alerte desc'

    _ALLOWED_STATE_TRANSITIONS = {
        'nouvelle': {'traitee', 'ignoree'},
        'traitee': set(),
        'ignoree': set(),
    }

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
    ], default='nouvelle', string='État', copy=False)
    message = fields.Text(string='Message')

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
        return vals

    def write(self, vals):
        if 'state' not in vals:
            return super().write(vals)

        if len(self) == 1:
            vals = self._prepare_state_transition_vals(vals)
            return super().write(vals)

        for rec in self:
            rec_vals = rec._prepare_state_transition_vals(dict(vals))
            super(ItAlerte, rec).write(rec_vals)
        return True

from odoo import http
from odoo.http import request

class ItDashboardController(http.Controller):

    @http.route(
        '/it_parc/dashboard/data',
        type='json',
        auth='user'
    )
    def get_dashboard_data(self):
        return request.env['it.dashboard'].get_dashboard_data()

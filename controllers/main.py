from odoo import http
from odoo.http import request


class MainController(http.Controller):

    @http.route('/get_compass_data', methods=["POST"], type="json", auth="user", lover="json")
    def get_compass_data(self, **kwargs):
        params = request.dispatcher.jsonrequest
        return request.env['smk.compass'].prepare_data(params)
#!/usr/bin/python
# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
# import odoo.addons.decimal_precision as dp
from odoo import fields, models, tools
from odoo.osv import osv
from odoo import exceptions
# _logger = logging.getLogger(__name__)


class IctCrm(models.Model):
    _name = 'ict.crm'
    _rec_name = 'model_id'

    apartment_id = fields.Many2one('ict.apartment', string='Căn hộ/ Chung cư')

    model_id = fields.Many2one('ict.infrastructure.model', string='OLT / IP SW')

    ict_department_id = fields.Many2one('ict.department', string='Phòng/Ban')
    port = fields.Integer(default=1, string='Port')

    pon_id_port = fields.Char(string='PON ID port-x')

    cpe_type = fields.Char(string='CPE Type')
    cpe_sn_xx = fields.Char(string='CPE SN-xx')

    state = fields.Selection([
        ('draft', 'Dự thảo'),
        ('confirm', 'Xác nhận')], default='draft', string=u'Trạng thái')

    @api.multi
    def confirm(self):
        for r in self:
            r.state = 'confirm'

    @api.onchange('model_id')
    def onchange_model_(self):
        if self.model_id:
            port_number = self.model_id.port
            model_search = self.search([('model_id', '=', self.model_id.id), ('state', '=', 'confirm')])
            port_use = sum([x.port for x in model_search])
            if port_number <= port_use:
                raise exceptions.UserError("Port number limit")

    @api.constrains('model_id')
    def api_contrains(self):
        if self.model_id:
            port_number = self.model_id.port
            model_search = self.search([('model_id', '=', self.model_id.id), ('state', '=', 'confirm')])
            port_use = sum([x.port for x in model_search])
            if port_number <= port_use:
                raise exceptions.UserError("Port number limit")


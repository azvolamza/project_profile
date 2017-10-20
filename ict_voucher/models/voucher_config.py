# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


class IctVoucherConfig(models.Model):
    _name = 'ict.voucher.config'
    _inherit = 'res.config.settings'
    _order = 'create_date desc'

    x_balance = fields.Float(string="Số đư đầu kỳ",
                                       required=True,
                                       default_model='ict.voucher.config')

    @api.one
    @api.constrains('x_balance')
    def constrain_x_balance(self):
        if self.x_balance < 1:
            raise ValidationError('You cannot choose months < 1!')

    @api.model
    def get_default_values(self, fields):
        self.env.cr.execute(
            'select * from ict_voucher_config order by id desc limit 1')
        _config = self.env.cr.dictfetchall()
        if len(_config) > 0 and 'x_balance' in _config[0]:
            return {
                'x_balance': _config[0]['x_balance'],
            }
        else:
            return {
                'x_balance': '',
            }

    @api.one
    def set_pr_values(self):
        self.env.cr.execute(
            'select * from ict_voucher_config order by id desc limit 1')
        _config = self.env.cr.dictfetchall()
        if len(_config) > 0 and 'x_balance' in _config[0]:
            _config[0]['x_balance'] = self.x_balance


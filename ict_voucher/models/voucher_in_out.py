#!/usr/bin/python
# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
# import odoo.addons.decimal_precision as dp
from odoo import fields, models, tools
from odoo.exceptions import AccessDenied, UserError
# _logger = logging.getLogger(__name__)


class VoucherKanban(models.Model):
    _name = 'voucher.kanban'
    _rec_name = 'name'

    @api.multi
    def attachment_tree_view(self):
        self.ensure_one()
        domain = [x.id for x in self.env['ict.voucher'].search([('kanban_id', '=', self.id)])]
        tree = self.env.ref('ict_voucher.ict_voucher_view_tree', False)
        form = self.env.ref('ict_voucher.ict_voucher_view_form', False)

        self.ensure_one()
        return {
            'name': 'Title',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'ict.voucher',
            'view_id': self.env.ref('ict_voucher.ict_voucher_view_tree').id,
            'target': 'current',
            'domain': [('id', 'in', domain)]
            }

    def _compute_attached_docs_count(self):
        for r in self:
            amount_obj = self.env['ict.voucher'].search([('kanban_id', '=', r.id)])
            if amount_obj:
                r.doc_count = sum([x.amount for x in amount_obj])
            else:
                r.doc_count = 0

    doc_count = fields.Integer(compute=_compute_attached_docs_count, string="Number of documents attached")
    name = fields.Char()

class IctVoucher(models.Model):
    _name = 'ict.voucher'
    _descreption = "Thu chi"
    _rec_name = 'name'

    @api.multi
    def confirm(self):
        rate = self.env.user.company_id.currency_id.rate
        for r in self:
            r.state = 'confirm'
            r.amount = (r.amount_in * rate) - (self.amount_out * rate)


    @api.multi
    def default_currency(self):
        # default currency follow currency in company
        if self.env.user.company_id:
            if self.env.user.company_id.currency_id:
                return self.env.user.company_id.currency_id.id

    @api.multi
    def default_week(self):
        import sys
        reload(sys)
        sys.setdefaultencoding('utf8')
        return unicode('Tuần') + ' ' + unicode(datetime.datetime.today().date().isocalendar()[1])

    @api.onchange('date_submit')
    def onchange_week(self):
        for r in self:
            if r.date_submit:
                import sys
                reload(sys)
                sys.setdefaultencoding('utf8')
                r.week = unicode('Tuần') + ' ' +  unicode(datetime.datetime.strptime(r.date_submit, '%Y-%m-%d').date().isocalendar()[1])

    @api.multi
    def default_kanban_ids(self):
        today = str((datetime.datetime.today().date()).year)
        search_kanban = self.env['voucher.kanban'].search([('name', '=', today)])
        if search_kanban:
            return search_kanban[0]
        else:
            create = self.env['voucher.kanban'].create({'name': today})
            return create

    @api.onchange('date_submit')
    def onchange_date_submit(self):
        date = self.date_submit[0:4]
        search_kanban = self.env['voucher.kanban'].search([('name', '=', date)])
        if search_kanban:
            self.kanban_id = search_kanban[0]
        else:
            create = self.env['voucher.kanban'].create({'name': date})
            self.kanban_id = create

    # @api.onchange('amount_in', 'amount_out')
    # def onchange_amount(self):
    #     self.amount = self.amount_in - self.amount_out

    @api.model
    def create(self, vals):
        return super(IctVoucher, self).create(vals)

    kanban_id = fields.Many2one('voucher.kanban', default=default_kanban_ids)
    name = fields.Char(string=u'Diễn giải')
    partner_id = fields.Many2one('res.partner', string=u'Đối tượng thanh toán')
    week = fields.Char(string=u'Tuần dự kiến', default=default_week)
    date_submit = fields.Date(default=fields.Date.today, string=u'Ngày dự kiến')

    amount_in = fields.Float(string=u'Giá trị thu')
    amount_out = fields.Float(string=u'Giá trị chi')
    amount = fields.Float(string='Dư')
    currency_id = fields.Many2one('res.currency', string=u'Loại tiền', default=default_currency)
    type = fields.Selection([
        ('thu', 'Thu'),
        ('chi', 'Chi')], default='thu', string=u'Dự kiến')

    date_confirm = fields.Date(string=u'KTT duyệt chi (Ngày phải chi)')
    state = fields.Selection([
        ('draft', 'Dự thảo'),
        ('confirm', 'Xác nhận')], default='draft', string=u'Trạng thái')
    notes = fields.Text(string=u'Ghi chú')


class ReportIctVoucher(models.Model):
    _name = "report.ict.voucher"
    _description = "Report Voucher"
    _order = 'name asc'
    _auto = False

    name = fields.Char(string=u'Đối tượng/Khách hàng/Nhà cung cấp')
    partner_id = fields.Many2one('res.partner', string=u'Đối tượng thanh toán')
    week = fields.Char(string=u'Tuần dự kiến')
    date_submit = fields.Date(default=fields.Date.today, string=u'Ngày dự kiến')

    amount_in = fields.Float(string=u'Giá trị thu thu')
    amount_out = fields.Float(string=u'Giá trị thu chi')
    amount = fields.Float(string=u'Dư')
    currency_id = fields.Many2one('res.currency', string=u'Loại tiền')
    type = fields.Selection([
        ('thu', 'Thu'),
        ('chi', 'Chi')], default='thu', string=u'Dự kiến')

    date_confirm = fields.Date(string=u'KTT duyệt chi (Ngày phải chi)', default=fields.Date.today)
    state = fields.Boolean(default=False, string=u'Tình trạng')
    notes = fields.Text(string=u'Ghi chú')

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
            CREATE view %s as
              SELECT name, partner_id, week, date_submit, amount_in, amount_out, amount, currency_id, type, date_confirm, state, notes
              FROM ict_voucher
              WHERE state = 'confirm'
        """ % (self._table))
        a = 1

#!/usr/bin/python
# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
# import odoo.addons.decimal_precision as dp
from odoo import fields, models, tools
from odoo.exceptions import AccessDenied, UserError
# _logger = logging.getLogger(__name__)


class IctApartment(models.Model):
    _name = 'ict.apartment'
    _rec_name = 'code'

    code = fields.Char(string=u"Mã căn hộ/ chung cư")
    name = fields.Char(string=u"Căn hộ/ Chung cư")


class IctDepartment(models.Model):
    _name = 'ict.department'
    _inherit = 'hr.department'

    apartment_id = fields.Many2one('ict.apartment', required=True, string='Căn hộ/ Chung cư')


class IctDeviceModel(models.Model):
    _name = 'ict.device.model'
    _descreption = "Quản lý hãng thiết bị"
    _rec_name = 'name'

    name = fields.Char()
    image = fields.Binary("Logo", attachment=True,
                          help="This field holds the image used as logo for the device, limited to 1024x1024px.")
    image_medium = fields.Binary("Medium-sized image", attachment=True,
                                 help="Medium-sized logo of the device. It is automatically "
                                      "resized as a 128x128px image, with aspect ratio preserved. "
                                      "Use this field in form views or some kanban views.")
    image_small = fields.Binary("Small-sized image", attachment=True,
                                help="Small-sized logo of the device. It is automatically "
                                     "resized as a 64x64px image, with aspect ratio preserved. "
                                     "Use this field anywhere a small image is required.")

    @api.model
    def create(self, vals):
        tools.image_resize_images(vals)
        return super(IctDeviceModel, self).create(vals)

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals)
        return super(IctDeviceModel, self).write(vals)


class IctInfrastructureModel(models.Model):
    _name = 'ict.infrastructure.model'
    _description = 'Infrastructure'
    _order = 'name asc'

    name = fields.Char('Model name', required=True)
    brand_id = fields.Many2one('ict.device.model', 'Make', required=True)
    vendors = fields.Many2many('res.partner', 'ict_model', 'model_id', 'partner_id', string='Nhà cung cấp')
    image = fields.Binary(related='brand_id.image', string="Logo")
    image_medium = fields.Binary(related='brand_id.image_medium', string="Logo (medium)")
    image_small = fields.Binary(related='brand_id.image_small', string="Logo (small)")

    port = fields.Integer(string='Port')

    @api.multi
    @api.depends('name', 'brand_id')
    def name_get(self):
        res = []
        for record in self:
            name = record.name
            if record.brand_id.name:
                name = record.brand_id.name + '/' + name
            res.append((record.id, name))
        return res

    @api.onchange('brand_id')
    def _onchange_brand(self):
        if self.brand_id:
            self.image_medium = self.brand_id.image
        else:
            self.image_medium = False


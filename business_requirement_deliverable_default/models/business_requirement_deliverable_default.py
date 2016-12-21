# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class BusinessRequirementDeliverable(models.Model):
    _inherit = "business.requirement.deliverable"

    @api.multi
    def _prepare_resource_lines(self):
        if self.product_id.resource_lines:
            rl = []
            for resource_line in self.product_id.resource_lines:
                rl.extend(resource_line.copy_data())
            return rl
        else:
            return []

    @api.onchange('product_id')
    def product_id_change(self):
        super(BusinessRequirementDeliverable, self).product_id_change()
        product = self.product_id
        if product:
            rl_data = self._prepare_resource_lines()
            br_resource_obj = self.env['business.requirement.resource']
            for item in rl_data:
                br_resource_obj += br_resource_obj.new(item)
            self.resource_ids = br_resource_obj


class ProductTemplate(models.Model):
    _inherit = "product.template"

    resource_lines = fields.One2many(
        comodel_name='business.requirement.resource',
        inverse_name='product_template_id',
        string='Business Requirement Resources',
        copy=True,
    )


class BusinessRequirementResource(models.Model):
    _inherit = "business.requirement.resource"

    product_template_id = fields.Many2one(
        comodel_name='product.template',
        string='Product',
        ondelete='set null',
        copy=False
    )
    business_requirement_deliverable_id = fields.Many2one(
        comodel_name='business.requirement.deliverable',
        copy=False
    )

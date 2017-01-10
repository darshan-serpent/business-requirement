# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError


class CrmLead(models.Model):
    _inherit = "crm.lead"

    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Project',
        ondelete='set null',
    )
    resource_cost_total = fields.Float(
        compute='_compute_resource_cost_total',
        string='Total Revenue from BR'
    )

    @api.depends('project_id', 'project_id.br_ids', 'project_id.br_ids.state')
    def _compute_resource_cost_total(self):
        self.resource_cost_total = sum(
            [br.total_revenue for br in
                self.project_id and self.project_id.br_ids
                if br.state not in ('drop', 'cancel')])

    @api.onchange('project_id')
    def project_id_change(self):
        if self.project_id:
            self.partner_id = self.project_id.partner_id.id

    @api.multi
    def make_orderline(self):
        sale_obj = self.env['sale.order']
        new_ids = []
        for case in self:
            partner = case.partner_id
            pricelist = partner.property_product_pricelist.id
            fpos = partner.property_account_position_id\
                and partner.property_account_position_id.id or False
            payment_term = partner.property_payment_term_id\
                and partner.property_payment_term_id.id or False
            invoice = partner.address_get(['invoice'])['invoice']
            delivery = partner.address_get(['delivery'])['delivery']
            vals = {
                'origin': _('Opportunity: %s') % str(case.id),
                'team_id': case.team_id and case.team_id.id or False,
                'tag_ids': [(6, 0, [tag_id.id for tag_id in case.tag_ids])],
                'partner_id': partner.id,
                'pricelist_id': pricelist,
                'partner_invoice_id': invoice,
                'partner_shipping_id': delivery,
                'date_order': datetime.now(),
                'fiscal_position': fpos,
                'payment_term': payment_term,
                'note': case.description,
            }
            if partner.id:
                vals['user_id'] =\
                    partner.user_id and partner.user_id.id or self._uid
            new_id = sale_obj.create(vals)
            new_ids.append(new_id.id)
            if new_id:
                order_lines = case.prepare_sale_order_line(new_id)
                case.create_sale_order_line(order_lines)
        return {
            'name': _('Quotation'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'view_id': False,
            'res_model': 'sale.order',
            'res_id': new_ids and new_ids[0],
            'domain': str([('id', 'in', new_ids)]),
            'type': 'ir.actions.act_window',
        }

    @api.multi
    def prepare_sale_order_line(self, order_id):
        lines = []
        linked_brs = self.project_id and self.project_id.br_ids or []
        if not linked_brs:
            raise UserError(_("There is no available business"
                              "requirement to make sale order!"))
        for line in self:
            for br in linked_brs:
                if br.state in ('drop', 'cancel'):
                    continue
                for br_line in br.deliverable_lines:
                    taxes = br_line.product_id.taxes_id
                    fp = line.partner_id.property_account_position_id
                    if fp:
                        taxes = fp.map_tax(taxes)
                    taxes = taxes.filtered(
                        lambda x: x.company_id == br.company_id)
                    vals = {
                        'order_id': order_id.id,
                        'product_id': br_line.product_id.id,
                        'name': br_line.name,
                        'product_uom_qty': br_line.qty,
                        'product_uom': br_line.uom_id.id,
                        'price_unit': br_line.unit_price,
                        'tax_id': [(6, 0, taxes.ids)],
                    }
                    lines.append(vals)
        return lines

    @api.multi
    def create_sale_order_line(self, order_lines):
        saleorder_line_obj = self.env['sale.order.line']
        for line in order_lines:
            saleorder_line_obj.create(line)

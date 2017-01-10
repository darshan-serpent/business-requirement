# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.tests import common


@common.at_install(False)
@common.post_install(True)
class BusinessRequirementTestCase(common.TransactionCase):
    def setUp(self):
        super(BusinessRequirementTestCase, self).setUp()
        self.ProjectObj = self.env['project.project']
        self.AnalyticAccountObject = self.env['account.analytic.account']
        self.UomObj = self.env['product.uom']
        self.CrmleadObj = self.env['crm.lead']
        self.ProductObj = self.env['product.product']

        self.categ_wtime = self.ref('product.uom_categ_wtime')
        self.partner = self.env.ref("base.res_partner_1")

        self.AnalyticAccount = self.AnalyticAccountObject.create(
            {'name': 'AnalyticAccount for Test'})
        self.projectA = self.ProjectObj.create(
            {'name': 'Test Project A', 'partner_id': self.partner.id,
             'analytic_account_id': self.AnalyticAccount.id})

        self.uom_hours = self.UomObj.create({
            'name': 'Test-Hours',
            'category_id': self.categ_wtime,
            'factor': 8,
            'uom_type': 'smaller'})

        self.productA = self.ProductObj.create(
            {'name': 'Product A', 'uom_id': self.uom_hours.id,
                'uom_po_id': self.uom_hours.id,
                'standard_price': 450})
        self.productB = self.ProductObj.create(
            {'name': 'Product B', 'uom_id': self.uom_hours.id,
                'uom_po_id': self.uom_hours.id,
                'standard_price': 550})

        vals = {
            'description': 'tests',
            'project_id': self.projectA.id,
            'deliverable_lines': [
                (0, 0, {'name': 'deliverable lines1', 'qty': 1.0,
                        'unit_price': 900, 'uom_id': 1,
                        'product_id': self.productA.id,
                        'resource_ids': [
                            (0, 0, {
                                'name': 'Resource Lines1',
                                'product_id': self.productB.id,
                                'qty': 100,
                                'uom_id': self.uom_hours.id,
                                'resource_type': 'task',
                            }),
                        ]
                        }),
            ],
        }

        self.brA = self.env['business.requirement'].create(vals)

        self.lead = self.CrmleadObj.create({
            'type': "lead",
            'name': "Test lead new",
            'partner_id': self.partner.id,
            'description': "This is the description of the new lead.",
            'team_id': self.env.ref("sales_team.team_sales_department").id,
            'project_id': self.projectA.id
        })

    def test_crm(self):
        self.lead.make_orderline()
        origin = "Opportunity: " + str(self.lead.id)
        self.saleorder = self.env['sale.order'].\
            search([('partner_id', '=', self.lead.partner_id.id),
                    ('origin', '=', origin)])
        for line in self.saleorder.order_line:
            self.assertEqual(line.product_id.id,
                             self.brA.deliverable_lines.product_id.id)
            self.assertEqual(len(line), len(self.brA.deliverable_lines))

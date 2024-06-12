from odoo import models


class Project(models.Model):
    _inherit = "project.project"

    def _fetch_sale_order_item_ids(
        self, domain_per_model=None, limit=None, offset=None
    ):
        # Override to flush the ORM cache to the database prior to running the query
        # Temporary fix until Odoo fixes this method (PR #160067 submitted for this)
        self.env.flush_all()
        return super()._fetch_sale_order_item_ids(domain_per_model, limit, offset)

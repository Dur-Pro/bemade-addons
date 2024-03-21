# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons.website.models import ir_http
import logging

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _tag_property(self):
        return self.env.ref('bemade_sethy_configuration.partner_tag_property', raise_if_not_found=False)

    @api.model
    def _tag_owner(self):
        return self.env.ref('bemade_sethy_configuration.partner_tag_owner', raise_if_not_found=False)

    @api.model
    def _relation_owner_property(self):
        return self.env.ref('bemade_sethy_configuration.partner_relation_property', raise_if_not_found=False)

    # Add new fields to the res.partner model for property management
    surface = fields.Float(string='Surface (ha)')
    lot_number = fields.Text(string='Lot Number')

    # Add new fields to the res.partner model for owner/member management
    ref_project = fields.Text(string='Project No')
    intent_signing = fields.Boolean(string='Intent to sign')
    cyberimpact = fields.Boolean(string='Cyberimpact')
    specification_date = fields.Date(string='Specification date')
    crm_stage_activity = fields.Text(string='Activity Stage')
    company_use = fields.Text(string='Company related')

    # Add new fields to the res.partner model for member management
    sethy_first_date = fields.Date(string='First membership date')  # member
    sethy_last_date = fields.Date(string='Last membership date')  # member
    sethy_renew_date = fields.Date(string='Next renew date date')  # member
    sethy_certification_date = fields.Date(string='Certification date date')  # member
    sethy_payment_type = fields.Text(string='Payment Type')  # member
    sethy_amount = fields.Float(string='Payment amount')  # Member

    is_property = fields.Boolean(
        string='Is Property',
        compute='_compute_is_property',
        inverse='_inverse_is_property',
        store=True
    )  # True if property, False if not

    interest_level = fields.Selection(
        selection=[
            ('1', 'None'),
            ('2', 'Low'),
            ('3', 'Average'),
            ('4', 'High')],
        string='Interest Level')  # proprio

    # Filtered fields relation_all_ids for owner
    relation_owner_ids = fields.One2many(
        "res.partner.relation.all",
        compute="_compute_relation_property_owner",
        string="Owner ids",
        compute_sudo=True,
    )

    # Filtered fields relation_all_ids for property
    relation_property_ids = fields.One2many(
        "res.partner.relation.all",
        compute="_compute_relation_property_owner",
        string="Property ids",
        compute_sudo=True,
    )

    # Add new fields to the res.partner model for owner management
    property_count = fields.Integer(
        string='Property count',
        compute='_compute_property_count',
        store=True,
        compute_sudo=True
    )

    is_owner = fields.Boolean(
        string='Is Owner',
        compute='_compute_owner',
        store=True,
        compute_sudo=True,
    )

    @api.depends('relation_all_ids')
    def _compute_owner(self):
        #owner_tag = self._tag_owner()
        owner_tag = self.env.ref('bemade_sethy_configuration.partner_tag_owner', raise_if_not_found=False)
        for record in self:
            record.is_owner = record.relation_count > 0
            if record.is_owner:
                record.category_id |= owner_tag
            else:
                record.category_id -= owner_tag

    # this is an hugly fix because @api depends doesn't work on new function so hacking it here
    @api.depends("relation_all_ids")
    def _compute_relation_count(self):
        super()._compute_relation_count()
        #owner_tag = self._tag_owner()
        owner_tag = self.env.ref('bemade_sethy_configuration.partner_tag_owner', raise_if_not_found=False)
        for record in self:
            for line in record.relation_all_ids:
                if line.active and line.type_id == owner_tag:
                    record.relation_count += 1
            record.is_owner = record.relation_count > 0 and not record.is_property
            if record.is_owner:
                record.category_id |= owner_tag
            else:
                record.category_id -= owner_tag

    @api.depends('category_id')
    def _compute_is_property(self):
        default_is_property = self._context.get('default_is_property', None)
        #property_tag = self._tag_property()
        property_tag = self.env.ref('bemade_sethy_configuration.partner_tag_property', raise_if_not_found=False)
        for partner in self:
            # Check if the property tag exists.  If it doesn't, set is_property to False.
            # Because module installation order is not guaranteed, the tag may not exist yet when this method is called.
            # This is due to store=True on the is_property field.
            if default_is_property is not None and not self.id:
                partner.is_property = default_is_property
            else:
                if property_tag is None:
                    partner.is_property = False
                else:
                    partner.is_property = property_tag and property_tag in partner.category_id


    def _inverse_is_property(self):
        #property_tag = self._tag_property()
        property_tag = self.env.ref('bemade_sethy_configuration.partner_tag_property', raise_if_not_found=False)
        if property_tag is not None:
            for partner in self:
                if partner.is_property and property_tag not in partner.category_id and property_tag:
                    partner.category_id |= property_tag
                elif not partner.is_property and property_tag in partner.category_id:
                    partner.category_id -= property_tag

    @api.depends("relation_all_ids")
    def _compute_property_count(self):
        for record in self:
            #owner_tag = self._tag_owner()
            owner_tag = self.env.ref('bemade_sethy_configuration.partner_tag_owner', raise_if_not_found=False)
            record.property_count = len(record._get_owners())
            record.is_owner = record.property_count > 0
            if owner_tag is not None:
                if record.is_owner:
                    record.category_id |= owner_tag
                else:
                    record.category_id -= owner_tag

    @api.depends(
        'relation_all_ids',
        'relation_all_ids.type_id',
        'relation_all_ids.date_end',
        'relation_all_ids.this_partner_id',
        'relation_all_ids.other_partner_id',
        'relation_all_ids.is_inverse'
    )
    def _compute_relation_property_owner(self):
        for record in self:
            # relations = self.env['res.partner.relation.all']
            # for line in record.relation_all_ids:
            #     if active and is_property and is_inverse:
            #         relations |= line
            # record.relation_property_ids = relations
            record.relation_property_ids = record._get_properties()
            record.relation_owner_ids = record._get_owners()
            # Just for debugging below this line
            type_property = self._relation_owner_property()
            #type_property = self.env.ref('bemade_sethy_configuration.partner_relation_property')
            for line in record.relation_all_ids:
                active = line.active
                is_property = line.type_id == type_property
                is_inverse = line.is_inverse
                _logger.info(f"This partner: {line.this_partner_id.name}")
                _logger.info(f"Other partner: {line.other_partner_id.name}")
                _logger.info(f"Active: {active}, Property: {is_property}, Inverse: {is_inverse}, Type: {line.type_id.name}")

    def _get_properties(self):
        self.ensure_one()
        #type_property = self._relation_owner_property()
        type_property = self.env.ref('bemade_sethy_configuration.partner_relation_property')
        return self.relation_all_ids.filtered(
            lambda line: (line.type_id.id == type_property.id and line.is_inverse and line.active)
        )

    def _get_owners(self):
        self.ensure_one()
        #type_property = self._relation_owner_property()
        type_property = self.env.ref('bemade_sethy_configuration.partner_relation_property', raise_if_not_found=False)
        return self.relation_all_ids.filtered(
            lambda line: (line.type_id.id == type_property.id and not line.is_inverse and line.active)
        )

    @api.onchange('lot_number')
    def _onchange_lot_number(self):
        for lot in self:
            if lot.lot_number:
                lot.name = "Lot " + str(lot.lot_number)

    @api.model_create_multi
    def create(self, vals_list):
        # Create Partner records using the super function
        records = super().create(vals_list)
        user_company = self.env.user.company_id

        # Update the records where 'state_id' or 'country_id' isn't provided
        for record in records:
            if not record.state_id or not record.country_id:
                if not record.state_id and user_company.state_id:
                    record.write({
                        'state_id': user_company.state_id.id,
                    })
                if not record.country_id and user_company.country_id:
                    record.write({
                        'country_id': user_company.country_id.id
                    })
            if record.name.startswith("Lot "):
                record.lot_number = record.name[4:]
            record._inverse_is_property()
        return records

    @api.onchange('name')
    def _onchange_name(self):
        for record in self:
            if record.name and record.name.startswith("Lot "):
                record.lot_number = record.name[4:]

    def write(self, vals):
        result = super(ResPartner, self).write(vals)
        self._inverse_is_property()
        return result

    @api.onchange('category_id')
    def _onchange_category_id(self):
        self._compute_is_property()
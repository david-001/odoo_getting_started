# from odoo import fields, models, api
# from dateutil.relativedelta import relativedelta
# from odoo.exceptions import ValidationError, UserError
# from odoo.tools.float_utils import float_compare
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare


class PropertyOffer(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------
    _name = "estate.property.offer"  # name of table
    _description = "Estate Property Offer"
    _order = "price desc"
    _sql_constraints = [('check_price', 'CHECK(price>0)', 'Price should be (strictly) positive.')]


    # --------------------------------------- Fields Declaration ----------------------------------
    # Basic
    price = fields.Float(string="Price")
    validity = fields.Integer(string="Validity (days)", default=7)
    status = fields.Selection(
        string="Status",
        selection=[('accepted', 'Accepted'), ('refused', 'Refused')],
        copy=False,
        default=False,
    )

    # Relational
    partner_id = fields.Many2one('res.partner', string="Buyer", required=True, index=True)
    property_id = fields.Many2one('estate.property', string="Property", required=True, index=True)

    # For stat button:
    property_type_id = fields.Many2one(
        "estate.property.type", related="property_id.property_type_id", string="Property Type", store=True
    )

    # Computed
    date_deadline = fields.Date(string="Deadline", compute="_compute_deadline", inverse="_inverse_compute_deadline")


    # ------------------------------------------ CRUD Methods -------------------------------------
    @api.model
    def create(self, vals):
        if vals.get("property_id") and vals.get("price"):
            prop = self.env["estate.property"].browse(vals["property_id"])
            # We check if the offer is higher than the existing offers
            if prop.offer_ids:
                max_offer = max(prop.mapped("offer_ids.price"))
                if float_compare(vals["price"], max_offer, precision_rounding=0.01) <= 0:
                    raise UserError("The offer must be higher than %.2f" % max_offer)
            prop.state = "offer_received"
        return super().create(vals)


    # ---------------------------------------- Compute methods ------------------------------------
    # Comes into effect after you make changes. Don't have to change.
    @api.depends('validity','property_id.create_date')
    def _compute_deadline(self):
        for record in self:
            # record.date_deadline = add(record.property_id.create_date,days=record.validity)
            date = record.create_date.date() if record.create_date else fields.Date.today()
            record.date_deadline = date + relativedelta(days=record.validity)

    # Comes into effect after you save.
    @api.depends('property_id.create_date','date_deadline')
    def _inverse_compute_deadline(self):
        for record in self:
            # start_date = fields.Date.from_string(record.property_id.create_date)
            # end_date = fields.Date.from_string(record.date_deadline)
            # delta = relativedelta(end_date,start_date)
            # record.validity = (delta.years*365) + (delta.months*30) + delta.days
            date = record.create_date.date() if record.create_date else fields.Date.today()
            record.validity = (record.date_deadline - date).days


    # ---------------------------------------- Action Methods -------------------------------------
    def action_accepted(self):
        if self.status == "accepted":
            raise UserError("An offer as already been accepted.")
        else:
            self.status = 'accepted'
            self.property_id.state = 'offer_accepted'
            self.property_id.selling_price = self.price
            self.property_id.partner_id = self.partner_id

    def action_refused(self):
        self.status = 'refused'


    # @api.constrains('property_id.selling_price','property_id.expected_price')
    # def check_selling_price(self):
    #     if self.property_id.selling_price < 0.9*self.property_id.expected_price:
    #         raise ValidationError('Selling price cannot be lower than 90% of the expected price')
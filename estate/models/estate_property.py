# from odoo import fields, models, api
# from odoo.exceptions import UserError, ValidationError
# from dateutil.relativedelta import relativedelta
# from datetime import datetime, timedelta, date


from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
from odoo.tools import float_compare, float_is_zero


class Property(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------
    _name = "estate.property"  # name of table
    _description = "Estate Property"
    _order = "id desc"
    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price>=0)', 'Expected price should be (strictly) positive.'),
        ('check_selling_price', 'CHECK(selling_price>=0)', 'Selling price should be (strictly) positive.')
    ]


    # ---------------------------------------- Default Methods ------------------------------------
    def _default_date_availability(self):
        return fields.Date.context_today(self) + relativedelta(months=3)


    # --------------------------------------- Fields Declaration ----------------------------------

    # Basic
    name = fields.Char(string="Title", required=True)
    description = fields.Text(string="Description")
    postcode = fields.Char(string="Postcode")
    # date_availability = fields.Date(string="Available From", copy=False,
    #                                 default=lambda self: (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d'))

    # prevent copying of the availability date
    date_availability = fields.Date("Available From", default=lambda self: self._default_date_availability(), copy=False)
    expected_price = fields.Float(string="Expected Price", required=True)
    selling_price = fields.Float(string="Selling Price", readonly=True, copy=False)
    bedrooms = fields.Integer(string="Bedrooms", default=2)
    living_area = fields.Integer(string="Living Area (sqm)")
    facades = fields.Integer(string="Facades")
    garage = fields.Boolean(string="Garage")
    garden = fields.Boolean(string="Garden")
    garden_area = fields.Integer(string="Garden Area (sqm)")
    garden_orientation = fields.Selection(
        string='Garden Orientation',
        selection=[('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')],
        default='north'
    )

    # Special
    active = fields.Boolean(string="Active", default=True)
    state = fields.Selection(
        string='Status',
        selection=[('new', 'New'), ('offer_received', 'Offer Received'), ('offer_accepted', 'Offer Accepted'),
                   ('sold', 'Sold'), ('canceled', 'Canceled')],
        required=True,
        copy=False,
        default='new',
        readonly=True
    )

    # Relational
    # A estate property can have one estate type, but the same estate type can be assigned to many estate properties
    property_type_id = fields.Many2one('estate.property.type', string="Property Type")

    user_id = fields.Many2one("res.users", string="Salesman", default=lambda self: self.env.user)
    partner_id = fields.Many2one("res.partner", string="Buyer", readonly=True, copy=False)

    # A property can have many tags and a tag can be assigned to many properties.
    tag_ids = fields.Many2many("estate.property.tag", string="Tags")

    # An offer applies to one property, but the same property can have many offers.
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")

    # Computed
    total_area = fields.Integer(string="Total Area (sqm)", compute="_compute_total_area")

    best_price = fields.Float(string="Best Offer", compute="_compute_best_price")

    # create_date = fields.Date(string="Creation Date", copy=False, default=date.today())


    # ---------------------------------------- Compute methods ------------------------------------
    @api.depends('living_area','garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends('offer_ids.price')
    def _compute_best_price(self):
        for record in self:
            if record.offer_ids:
                record.best_price = max(record.offer_ids.mapped('price'))
            else:
                record.best_price = 0
            # OR
            # for offer in record.offer_ids:
            #     if offer.price > max_price:
            #         max_price = offer.price
            #         record.best_price = max_price


    # ----------------------------------- Constrains and Onchanges --------------------------------
    @api.constrains('selling_price', 'expected_price')
    def _check_price_difference(self):
        for record in self:
            if (
                    not float_is_zero(record.selling_price, precision_rounding=0.01)
                    and float_compare(record.selling_price, record.expected_price * 90.0 / 100.0,
                                      precision_rounding=0.01) < 0
            ):
                raise ValidationError(
                    "The selling price must be at least 90% of the expected price! "
                    + "You must reduce the expected price if you want to accept this offer."
                )

        # if (self.selling_price < 0.9 * self.expected_price) and self.expected_price != 0 and self.selling_price != 0:
        #     raise ValidationError('Selling price cannot be lower than 90% of the expected price')

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = False


    # ---------------------------------------- Action Methods -------------------------------------
    def action_sold(self):
        # if "canceled" in self.mapped("state"):
        #     raise UserError("Canceled properties cannot be sold.")
        # return self.write({"state": "sold"})
        if self.state != 'canceled':
            self.state = 'sold'
        else:
            raise UserError("Canceled properties cannot be sold.")

    def action_cancel(self):
        if self.state != 'sold':
            self.state = 'canceled'
        else:
            raise UserError("Sold properties cannot be canceled.")


    # ------------------------------------------ CRUD Methods -------------------------------------
    @api.ondelete(at_uninstall=False)
    def _unlink_except_state_new_or_canceled(self):
        if not set(self.mapped("state")) <= {"new", "canceled"}:
            raise UserError("Only new and canceled properties can be deleted.")
        # if self.state != "new" or self.state != "canceled":
        #     raise UserError("Only new and canceled properties can be deleted.")

    # def unlink(self):
        # if not set(self.mapped("state")) <= {"new", "canceled"}:
        #     raise UserError("Only new and canceled properties can be deleted.")
        # return super().unlink()
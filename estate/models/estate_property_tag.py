from odoo import fields, models

class PropertyTag(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------
    _name = "estate.property.tag"  # name of table
    _description = "Estate Property tag"
    _order = "name"
    _sql_constraints = [('check_name', 'UNIQUE(name)', 'Property tags should have a unique name.')]


    # --------------------------------------- Fields Declaration ----------------------------------
    # Basic
    name = fields.Char(string="Tag", required=True)
    color = fields.Integer("Color Index")


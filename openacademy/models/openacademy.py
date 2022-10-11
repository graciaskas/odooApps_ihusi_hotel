# -*- coding: utf-8 -*-


from odoo import models, fields, api


class Course(models.Model):
    _name = 'openacademy.course'
    _description = "Open academy course"

    name = fields.Char(string='Course name', required=True,
                       help='Course name here')
    description = fields.Text(string='Description',
                              help='Course description here')

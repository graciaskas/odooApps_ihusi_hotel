# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class HotelFolio(models.Model):
    _inherit = 'hotel.folio'

    birth_date = fields.Date(
        string="Date de naissance  ", help='Date de naissance')
    birth_place = fields.Char(
        string="Lieu de naissance  ", help='Lieu de naissance')

    marital_state = fields.Selection([
        ('CB', 'Célibataire'),
        ('MA', 'Marié(e)'),
        ('DV', 'Divorcé(e)'),
        ('Autre', 'Autre')],
        default="Autre",
        string="Etat civil  ",
        help='Etat civil'
    )

    nationality = fields.Many2one(
        'res.country', string='Nationalité',  help='Nationalité')

    house_permenant = fields.Char(
        string="Domicile permenant  ", help='Domicile permenant')

    document_type = fields.Selection([
        ('CE', 'Carte d\'electeur'),
        ('Visa', 'Visa'),
        ('Passeport', 'Passeport'),
        ('Permis', 'Permis de conduire'),
        ('Autre', 'Autre')],
        default="Autre",
        required=True,
        string="Nature de pièce",
        help='Nature de pièce'
    )

    place_of_document = fields.Char(
        string='Lieu d\'émission',
        help='Lieu d\'émission'
    )

    type_of_visa = fields.Char(
        string='Genre de visa',
        help='Genre de visa'
    )

    job = fields.Char(
        string='Profession',
        help='Profession'
    )

    datetype_o = fields.Char(
        string='Date et numéro de la pièce',
        help='Date et numéro de la pièce'
    )

    residence_co = fields.Char(
        string='Residence au congo',
        help='Residence au congo'
    )

    residence_fo = fields.Char(
        string='Residence à l\'étranger',
        help='Residence à l\'étranger'
    )

    comming_from = fields.Char(
        string='Lieu de provenance',
        help='Lieu de provenance'
    )

    destination = fields.Char(
        string='Destination',
        help='Destination'
    )


# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)

class IBASCustomer(models.Model):
    _inherit = 'res.partner'

    

    civil_status = fields.Selection([
        ('Single', 'Single'),
        ('Married', 'Married'),
        ('Widowed', 'Widowed'),
        ('Separated', 'Separated or Divorced'),
    ], string='Civil Status')

    sex = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], string='Sex')

    citizenship = fields.Char(string='Citizenship')
    birthdate = fields.Date(string='Date of Birth')

    duration_stay = fields.Date(string='Duration of Stay')
    home_ownership = fields.Selection([
        ('owned', 'Owned'),
        ('rented', 'Rented'),
        ('relatives', 'Living with Relatives'),
    ], string='Current Home Ownership')

    occupation = fields.Char(string='Occupation')   

    employer_name = fields.Char(string='Employer or Business Name')
    monthly_income = fields.Selection([
        ('50k', 'Below 50k'),
        ('100k', '50k-100k'),
        ('200k', '100k-200k'),
        ('201k', 'Above 200k'),
    ], string='Monthly Income')

    is_ofw = fields.Boolean(string='Is an OFW')

    buying_reason = fields.Selection([
        ('upgrade', 'Upgrade'),
        ('relocation', 'Relocate'),
        ('vh', 'Vacation Home'),
        ('gift', 'Gift to Children'),
        ('ret', 'Retirement Home'),
        ('inv', 'Investment - 2nd or 3rd Acquisition'),
        ('inv2', 'Investment - Rent'),
    ], string='Reason for Buying')

    source_awareness = fields.Selection([
        ('wi', 'Walk In'),
        ('fb', 'Facebook'),
        ('agent', 'Agent / Broker'),
        ('ia', 'Internet Ads'),
        ('news', 'Newspaper'),
        ('leaf', 'Leaflet'),
        ('web', 'Website'),
    ], string='Source of Awareness')

    # Spouse info

    spouse_name = fields.Char(string='Spouse')
    spouse_citizenship = fields.Char(string='Spouse Citizenship')
    spouse_birthday = fields.Date(string='Spouse Birthday')
    spouse_mobile = fields.Char(string='Spouse Mobile Number')
    spouse_occupation = fields.Char(string='Spouse Occupation')
    spouse_employer = fields.Char(string='Spouse Employer')
    spouse_designation = fields.Char(string='Spouse Designation')
    spouse_contact = fields.Char(string='Spouse Contact Number')
    spouse_office_address = fields.Text(string='Spouse Office Address')
    spouse_tin = fields.Char(string='Spouse TIN')
    spouse_monthly_income = fields.Selection([
        ('50k', 'Below 50k'),
        ('100k', '50k-100k'),
        ('200k', '100k-200k'),
        ('201k', 'Above 200k'),
    ], string='Spouse Monthly Income')

    # SPA

    spa_name = fields.Char(string='SPA')
    spa_citizenship = fields.Char(string='SPA Citizenship')
    spa_birthday = fields.Date(string='SPA Birthday')
    spa_mobile = fields.Char(string='SPA Mobile Number')
    spa_contact = fields.Char(string='SPA Contact Number')
    spa_relationship = fields.Char(string='Relationship to Buyer')






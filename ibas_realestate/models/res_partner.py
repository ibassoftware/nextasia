
# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class IBASCustomer(models.Model):
    _inherit = 'res.partner'

    phone = fields.Char(string='Residence Landline No.')
    mobile = fields.Char(string='Mobile No.')

    # Principal Buyer
    age = fields.Char('Age')
    place_of_birth = fields.Char('Place of Birth')
    education_attain = fields.Selection([
        ('High School Graduate', 'High School Graduate'),
        ('College Graduate', 'College Graduate'),
        ('Post Graduate', 'Post Graduate'),
    ], string="Educational Attainment")
    office_landline = fields.Char('Office Landline No.')
    have_co_buyer = fields.Boolean('Does he/she have a Co-buyer?')

    sss_no = fields.Char('SSS No.')
    pag_ibig_no = fields.Char('Pag-ibig No.')
    tin_no = fields.Char('Tin No.')
    employer_name = fields.Char(string='Employer/Business Name')
    company_address = fields.Char('Company Address')
    nature_business = fields.Char('Nature of Business')
    date_employed_established = fields.Date('Date Employed/Established')
    monthly_gross_salary = fields.Monetary('Monthly Gross Salary')
    allowances = fields.Monetary('Allowances')
    commisions = fields.Monetary('Commisions')
    total_earnings = fields.Monetary(
        compute="_compute_earnings", string='Total')

    monthly_income = fields.Selection([
        ('50k', 'Below 50k'),
        ('100k', '50k-100k'),
        ('200k', '100k-200k'),
        ('201k', 'Above 200k'),
    ], string='Monthly Income')

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

    # Co-Buyer
    co_buyer_id = fields.Many2one('res.partner', string="Co-Buyer")
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

    # Financial References
    loan_name = fields.Char('Name of Institution')
    loan_type = fields.Char('Type of Loan')
    loan_paid_granted = fields.Date('Date Paid/Granted')
    loan_outstanding_balance = fields.Monetary('Outstanding Balance')
    loan_month_amortization = fields.Monetary('Monthly Amortization')

    credit_card_issuer = fields.Char('Card Issuer')
    credit_card_number = fields.Char('Credit Card Number')
    credit_limit = fields.Monetary('Credit Limit')
    credit_card_name = fields.Char('Name of Card')

    # Sales & Purchase

    broker = fields.Many2one('hr.employee', string="Broker")
    agent = fields.Many2one('hr.employee', string="Agent")
    sales_manager = fields.Many2one('hr.employee', string="Sales Manager")
    nali_coordinator = fields.Many2one(
        'hr.employee', string="NALI Coordinator")

    @api.depends('monthly_gross_salary', 'allowances', 'commisions')
    def _compute_earnings(self):
        self.total_earnings = self.monthly_gross_salary + \
            self.allowances + self.commisions

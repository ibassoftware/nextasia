
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

    home_ownership = fields.Selection([
        ('owned', 'Owned'),
        ('rented', 'Rented'),
        ('relatives', 'Living with Relatives'),
    ], string='Current Home Ownership')

    occupation = fields.Char(string='Occupation')

    is_ofw = fields.Boolean(string='Is an OFW')
    duration_stay_from = fields.Date(string='From')
    duration_stay_to = fields.Date(string='To')

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
    # Left
    cb_lastname = fields.Char('Last Name')
    cb_firstname = fields.Char('First Name')
    cb_middlename = fields.Char('Middle Name')
    cb_suffix = fields.Char('Suffix')
    cb_street = fields.Char('Street')
    cb_street2 = fields.Char('Street2')
    cb_city = fields.Char('City')
    cb_state_id = fields.Many2one(
        'res.country.state', string="State", domain="[('country_id','=', country_id)]")
    cb_zip = fields.Char('Zip')
    cb_country_id = fields.Many2one('res.country', string="Country")

    cb_duration_stay_from = fields.Date(string='From')
    cb_duration_stay_to = fields.Date(string='To')
    cb_home_ownership = fields.Selection([
        ('owned', 'Owned'),
        ('rented', 'Rented'),
        ('relatives', 'Living with Relatives'),
    ], string='Current Home Ownership')

    cb_civil_status = fields.Selection([
        ('Single', 'Single'),
        ('Married', 'Married'),
        ('Widowed', 'Widowed'),
        ('Separated', 'Separated or Divorced'),
    ], string='Civil Status')

    cb_sex = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], string='Gender')

    cb_citizenship = fields.Char(string='Citizenship')

    cb_age = fields.Char('Age')
    cb_place_of_birth = fields.Char('Place of Birth')
    cb_date_of_birth = fields.Char('Place of Birth')
    # Right
    cb_sss_no = fields.Char('SSS No.')
    cb_pag_ibig_no = fields.Char('Pag-ibig No.')
    cb_tin_no = fields.Char('Tin No.')
    cb_email = fields.Char('Email Address')
    cb_residence_landline = fields.Char('Residence Landline No.')
    cb_mobile_no = fields.Char('Mobile No.')
    cb_office_landline = fields.Char('Office Landline No.')

    cb_company_name = fields.Char(string='Company/Business Name')
    cb_company_address = fields.Char('Company Address')
    cb_nature_business = fields.Char('Nature of Business')
    cb_designation = fields.Char('Designation')
    cb_date_employed_established = fields.Date('Date Employed/Established')
    cb_monthly_gross_salary = fields.Monetary('Monthly Gross Salary')
    cb_allowances = fields.Monetary('Allowances')
    cb_commisions = fields.Monetary('Commisions')
    cb_total_earnings = fields.Monetary(
        compute="_compute_cb_earnings", string='Total')

    # Spouse info

    spouse_street = fields.Char('Street')
    spouse_street2 = fields.Char('Street2')
    spouse_city = fields.Char('City')
    spouse_state_id = fields.Many2one(
        'res.country.state', string="State", domain="[('country_id','=', country_id)]")
    spouse_zip = fields.Char('Zip')
    spouse_country_id = fields.Many2one('res.country', string="Country")

    spouse_name = fields.Char(string='Name of Spouse')
    spouse_citizenship = fields.Char(string='Spouse Citizenship')
    spouse_birthday = fields.Date(string='Date of Birth')
    spouse_mobile = fields.Char(string='Mobile No.')
    spouse_monthly_income = fields.Selection([
        ('50k', 'Below 50k'),
        ('100k', '50k-100k'),
        ('200k', '100k-200k'),
        ('201k', 'Above 200k'),
    ], string='Monthly Income')

    spouse_age = fields.Char('Age')
    spouse_place_of_birth = fields.Char('Place of Birth')

    spouse_sex = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], string='Sex')

    spouse_sss_no = fields.Char('SSS No.')
    spouse_pag_ibig_no = fields.Char('Pag-ibig No.')
    spouse_tin_no = fields.Char('Tin No.')
    spouse_email = fields.Char('Email')
    spouse_residence_landline = fields.Char('Residence Landline No.')
    spouse_office_landline = fields.Char('Office Landline No.')
    spouse_employer_name = fields.Char(string='Company/Business Name')
    spouse_company_address = fields.Char('Company Address')
    spouse_nature_business = fields.Char('Nature of Business')
    spouse_date_employed_established = fields.Date('Date Employed/Established')
    spouse_monthly_gross_salary = fields.Monetary('Monthly Gross Salary')
    spouse_allowances = fields.Monetary('Allowances')
    spouse_commisions = fields.Monetary('Commisions')
    spouse_total_earnings = fields.Monetary(
        compute="_compute_spouse_earnings", string='Total')

    # SPA
    # Left

    spa_street = fields.Char('Street')
    spa_street2 = fields.Char('Street2')
    spa_city = fields.Char('City')
    spa_state_id = fields.Many2one(
        'res.country.state', string="State", domain="[('country_id','=', country_id)]")
    spa_zip = fields.Char('Zip')
    spa_country_id = fields.Many2one('res.country', string="Country")

    spa_name = fields.Char(string='SPA Name')
    spa_citizenship = fields.Char(string='SPA Citizenship')
    spa_birthday = fields.Date(string='SPA Birthday')
    spa_mobile = fields.Char(string='SPA Mobile Number')
    spa_contact = fields.Char(string='SPA Contact Number')
    spa_relationship = fields.Char(string='Relationship to Buyer')

    spa_age = fields.Char('Age')
    spa_place_of_birth = fields.Char('Place of Birth')
    spa_civil_status = fields.Selection([
        ('Single', 'Single'),
        ('Married', 'Married'),
        ('Widowed', 'Widowed'),
        ('Separated', 'Separated or Divorced'),
    ], string='Civil Status')

    spa_sex = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], string='Gender')
    # Right
    spa_email = fields.Char('Email Address')
    spa_office_landline = fields.Char('Office Landline No.')
    spa_sss_no = fields.Char('SSS No.')
    spa_tin_no = fields.Char('Tin No.')
    spa_company_name = fields.Char(string='Company/Business Name')
    spa_company_address = fields.Char('Company Address')
    spa_nature_business = fields.Char('Nature of Business')
    spa_designation = fields.Char('Designation')
    spa_date_employed_established = fields.Date('Date Employed/Established')

    # Financial References
    loan_name = fields.Char('Name of Institution')
    loan_type = fields.Char('Type of Loan')
    loan_paid_granted = fields.Date('Date Paid/Granted')
    loan_outstanding_balance = fields.Monetary('Outstanding Balance')
    loan_month_amortization = fields.Monetary('Monthly Amortization')

    credit_card_issuer = fields.Char('Card Issuer')
    credit_card_number = fields.Char('Credit Card Number')
    credit_limit = fields.Monetary('Credit Limit')
    credit_card_name = fields.Char('Name on Card')

    # Personal References
    per_name = fields.Char('Name')
    per_relation_buyer = fields.Char('Relation to Buyer')
    per_residence_address = fields.Char('Residenece to Buyer')
    per_office_address = fields.Char('Office Address')
    per_contact_number = fields.Char('Contact Number')

    # Sales & Purchase

    broker = fields.Many2one('hr.employee', string="Broker")
    agent = fields.Many2one('hr.employee', string="Agent")
    sales_manager = fields.Many2one('hr.employee', string="Sales Manager")
    nali_coordinator = fields.Many2one(
        'hr.employee', string="NALI Coordinator")

    # Requirements
    reservation_ids = fields.One2many(
        'ibas_realestate.requirement_reservation_line', 'parent_id', string="reservation")
    booked_sale_ids = fields.One2many(
        'ibas_realestate.requirement_booked_sale_line', 'parent_id', string="booked sale")
    contracted_sale_ids = fields.One2many(
        'ibas_realestate.requirement_contracted_sale_line', 'parent_id', string="contracted sale")

    @api.depends('monthly_gross_salary', 'allowances', 'commisions')
    def _compute_earnings(self):
        self.total_earnings = self.monthly_gross_salary + \
            self.allowances + self.commisions

    @api.depends('spouse_monthly_gross_salary', 'spouse_allowances', 'spouse_commisions')
    def _compute_spouse_earnings(self):
        self.spouse_total_earnings = self.spouse_monthly_gross_salary + \
            self.spouse_allowances + self.spouse_commisions

    @api.depends('cb_monthly_gross_salary', 'cb_allowances', 'cb_commisions')
    def _compute_cb_earnings(self):
        self.cb_total_earnings = self.cb_monthly_gross_salary + \
            self.cb_allowances + self.cb_commisions

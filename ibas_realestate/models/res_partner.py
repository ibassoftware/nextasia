
# -*- coding: utf-8 -*-

import logging
from openerp.exceptions import ValidationError
from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class IBASCustomer(models.Model):
    _inherit = 'res.partner'

    last_name = fields.Char('Last Name')
    first_name = fields.Char('First Name')
    middle_name = fields.Char('Middle Name')
    suffix = fields.Char('Suffix')

    phone = fields.Char(string='Residence Landline No.')
    mobile = fields.Char(string='Mobile No.', required=True)

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
    have_spa = fields.Boolean('Does he/she have an SPA?')

    sss_no = fields.Char('SSS No.')
    pag_ibig_no = fields.Char('Pag-ibig No.')
    tin_no = fields.Char('Tin No.')
    employer_name = fields.Char(string='Employer/Business Name')
    company_address = fields.Char('Company Address')
    nature_business = fields.Char('Nature of Business')
    date_employed_established = fields.Date('Date Employed/Established')
    monthly_gross_salary = fields.Monetary('Monthly Gross Salary')

    @api.constrains('monthly_gross_salary')
    def _require_monthly_gross_salary(self):
        for record in self:
            if record.monthly_gross_salary <= 0:
                raise ValidationError(
                    "Monthly Salary must not less than or equal %s" % record.monthly_gross_salary)

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
    birthday = fields.Date(string='Date of Birth')

    home_ownership = fields.Selection([
        ('owned', 'Owned'),
        ('rented', 'Rented'),
        ('relatives', 'Living with Relatives'),
    ], string='Current Home Ownership')

    occupation = fields.Char(string='Occupation')

    is_ofw = fields.Boolean(string='Is an OFW')
    duration_stay_from = fields.Char(string='From') #change to char
    duration_stay_to = fields.Char(string='To') #change to char

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
    cb_contact_id = fields.Many2one('res.partner', string='Co-Buyer Name')
    cb_lastname = fields.Char(
        related='cb_contact_id.last_name', string='Co-Buyer Last Name')
    cb_firstname = fields.Char(
        related='cb_contact_id.first_name', string='Co-Buyer First Name')
    cb_middlename = fields.Char(
        related='cb_contact_id.middle_name', string='Co-Buyer Middle Name')
    cb_suffix = fields.Char(
        related='cb_contact_id.suffix', string='Co-Buyer Suffix')
    cb_street = fields.Char(
        related='cb_contact_id.street', string='Co-Buyer Street')
    cb_street2 = fields.Char(
        related='cb_contact_id.street2', string='Co-Buyer Street2')
    cb_city = fields.Char(related='cb_contact_id.city', string='Co-Buyer City')
    cb_state_id = fields.Many2one(
        'res.country.state', string="Co-Buyer State", domain="[('country_id','=', country_id)]", related='cb_contact_id.state_id')
    cb_zip = fields.Char(related='cb_contact_id.zip', string='Co-Buyer Zip')
    cb_country_id = fields.Many2one(
        'res.country', string="Co-Buyer Country", related='cb_contact_id.country_id')

    cb_duration_stay_from = fields.Date(string='Co-Buyer From')
    cb_duration_stay_to = fields.Date(string='Co-Buyer To')
    cb_home_ownership = fields.Selection([
        ('owned', 'Owned'),
        ('rented', 'Rented'),
        ('relatives', 'Living with Relatives'),
    ], string='Co-Buyer Current Home Ownership', related='cb_contact_id.home_ownership')

    cb_civil_status = fields.Selection([
        ('Single', 'Single'),
        ('Married', 'Married'),
        ('Widowed', 'Widowed'),
        ('Separated', 'Separated or Divorced'),
    ], string='Co-Buyer Civil Status', related='cb_contact_id.civil_status')

    cb_sex = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], string='Co-Buyer Gender', related='cb_contact_id.sex')

    cb_citizenship = fields.Char(
        string='Co-Buyer Citizenship', related='cb_contact_id.citizenship')

    cb_age = fields.Char(related='cb_contact_id.age', string='Co-Buyer Age')
    cb_place_of_birth = fields.Char(
        related='cb_contact_id.place_of_birth', string='Co-Buyer Place of Birth')
    cb_date_of_birth = fields.Date(
        related='cb_contact_id.birthday', string='Co-Buyer Date of Birth')
    # Right
    cb_sss_no = fields.Char(
        related='cb_contact_id.sss_no', string='Co-Buyer SSS No.')
    cb_pag_ibig_no = fields.Char(
        related='cb_contact_id.pag_ibig_no', string='Co-Buyer Pag-ibig No.')
    cb_tin_no = fields.Char(
        related='cb_contact_id.tin_no', string='Co-Buyer Tin No.')
    cb_email = fields.Char(related='cb_contact_id.email',
                           string='Co-Buyer Email Address')
    cb_residence_landline = fields.Char(
        related='cb_contact_id.phone', string='Co-Buyer Residence Landline No.')
    cb_mobile_no = fields.Char(
        related='cb_contact_id.mobile', string='Co-Buyer Mobile No.')
    cb_office_landline = fields.Char(
        related='cb_contact_id.office_landline', string='Co-Buyer Office Landline No.')

    cb_company_name = fields.Char(
        related='cb_contact_id.employer_name', string='Co-Buyer Company/Business Name')
    cb_company_address = fields.Char(
        related='cb_contact_id.company_address', string='Co-Buyer Company Address')
    cb_designation = fields.Char(string='Co-Buyer Designation')
    cb_nature_business = fields.Char(
        related='cb_contact_id.nature_business', string='Co-Buyer Nature of Business')
    cb_date_employed_established = fields.Date(
        related='cb_contact_id.date_employed_established', string='Co-Buyer Date Employed/Established')
    cb_monthly_gross_salary = fields.Monetary(
        related='cb_contact_id.monthly_gross_salary', string='Co-Buyer Monthly Gross Salary')
    cb_allowances = fields.Monetary(
        related='cb_contact_id.allowances', string='Co-Buyer Allowances')
    cb_commisions = fields.Monetary(
        related='cb_contact_id.commisions', string='Co-Buyer Commisions')
    cb_total_earnings = fields.Monetary(
        compute="_compute_cb_earnings", string='Co-Buyer Total')

    # Spouse info

    spouse_contact_id = fields.Many2one('res.partner', string='Spouse Name')
    spouse_lastname = fields.Char(
        related='spouse_contact_id.last_name', string='Spouse Last Name')
    spouse_firstname = fields.Char(
        related='spouse_contact_id.first_name', string='Spouse First Name')
    spouse_middlename = fields.Char(
        related='spouse_contact_id.middle_name', string='Spouse Middle Name')
    spouse_suffix = fields.Char(
        related='spouse_contact_id.suffix', string='Spouse Suffix')
    spouse_street = fields.Char(
        related='spouse_contact_id.street', string='Spouse Street')
    spouse_street2 = fields.Char(
        related='spouse_contact_id.street2', string='Spouse Street2')
    spouse_city = fields.Char(
        related='spouse_contact_id.city', string='Spouse City')
    spouse_state_id = fields.Many2one('res.country.state', string="Spouse State",
                                      domain="[('country_id','=', country_id)]", related='spouse_contact_id.state_id')
    spouse_zip = fields.Char(
        related='spouse_contact_id.zip', string='Spouse  Zip')
    spouse_country_id = fields.Many2one(
        'res.country', string="Spouse Country", related='spouse_contact_id.country_id')

    spouse_citizenship = fields.Char(
        related='spouse_contact_id.citizenship', string='Spouse Citizenship')
    spouse_birthday = fields.Date(
        related='spouse_contact_id.birthday', string='Spouse Date of Birth')
    spouse_mobile = fields.Char(
        related='spouse_contact_id.mobile', string='Spouse Mobile No.')
    spouse_monthly_income = fields.Selection([
        ('50k', 'Below 50k'),
        ('100k', '50k-100k'),
        ('200k', '100k-200k'),
        ('201k', 'Above 200k'),
    ], string='Spouse Monthly Income')

    spouse_age = fields.Char(
        related='spouse_contact_id.age', string='Spouse Age')
    spouse_place_of_birth = fields.Char(
        related='spouse_contact_id.place_of_birth', string='Spouse Place of Birth')

    spouse_sex = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], string='Spouse Sex', related='spouse_contact_id.sex')

    spouse_sss_no = fields.Char(
        related='spouse_contact_id.sss_no', string='Spouse SSS No.')
    spouse_pag_ibig_no = fields.Char(
        related='spouse_contact_id.pag_ibig_no', string='Spouse Pag-ibig No.')
    spouse_tin_no = fields.Char(
        related='spouse_contact_id.tin_no', string='Spouse Tin No.')
    spouse_email = fields.Char(
        related='spouse_contact_id.email', string='Spouse Email')
    spouse_residence_landline = fields.Char(
        related='spouse_contact_id.phone', string='Spouse Residence Landline No.')
    spouse_office_landline = fields.Char(
        related='spouse_contact_id.office_landline', string='Spouse Office Landline No.')
    spouse_employer_name = fields.Char(
        related='spouse_contact_id.employer_name', string='Spouse Company/Business Name')
    spouse_company_address = fields.Char(
        related='spouse_contact_id.company_address', string='Spouse Company Address')
    spouse_nature_business = fields.Char(
        related='spouse_contact_id.nature_business', string='Spouse Nature of Business')
    spouse_date_employed_established = fields.Date(
        related='spouse_contact_id.date_employed_established', string='Spouse Date Employed/Established')
    spouse_monthly_gross_salary = fields.Monetary(
        related='spouse_contact_id.monthly_gross_salary', string='Spouse Monthly Gross Salary')
    spouse_allowances = fields.Monetary(
        related='spouse_contact_id.allowances', string='Spouse Allowances')
    spouse_commisions = fields.Monetary(
        related='spouse_contact_id.commisions', string='Spouse Commisions')
    spouse_total_earnings = fields.Monetary(
        compute="_compute_spouse_earnings", string='Spouse Total')

    # SPA
    # Left
    spa_contact_id = fields.Many2one('res.partner', string='Spa Name')
    spa_lastname = fields.Char(
        related='spa_contact_id.last_name', string='SPA Last Name')
    spa_firstname = fields.Char(
        related='spa_contact_id.first_name', string='SPA First Name')
    spa_middlename = fields.Char(
        related='spa_contact_id.middle_name', string='SPA Middle Name')
    spa_suffix = fields.Char(
        related='spa_contact_id.suffix', string='SPA Suffix')
    spa_street = fields.Char(
        related='spa_contact_id.street', string='SPA Street')
    spa_street2 = fields.Char(
        related='spa_contact_id.street2', string='SPA Street2')
    spa_city = fields.Char(related='spa_contact_id.city', string='SPA City')
    spa_state_id = fields.Many2one(
        'res.country.state', string="SPA State", domain="[('country_id','=', country_id)]", related='spa_contact_id.state_id')
    spa_zip = fields.Char(related='spa_contact_id.zip', string='Spa zip')
    spa_country_id = fields.Many2one(
        'res.country', string="SPA Country", related='spa_contact_id.country_id')

    spa_citizenship = fields.Char(
        related='spa_contact_id.citizenship', string='SPA Citizenship')
    spa_birthday = fields.Date(
        related='spa_contact_id.birthday', string='SPA Date of Birth')
    spa_mobile = fields.Char(
        related='spa_contact_id.mobile', string='SPA Mobile Number')
    spa_contact = fields.Char(
        related='spa_contact_id.phone', string='SPA Residence Landline No.')
    spa_relationship = fields.Char(string='Relationship to Buyer')

    spa_age = fields.Char(related='spa_contact_id.age', string='SPA Age')
    spa_place_of_birth = fields.Char(
        related='spa_contact_id.place_of_birth', string='SPA Place of Birth')
    spa_civil_status = fields.Selection([
        ('Single', 'Single'),
        ('Married', 'Married'),
        ('Widowed', 'Widowed'),
        ('Separated', 'Separated or Divorced'),
    ], string='SPA Civil Status', related='spa_contact_id.civil_status')

    spa_sex = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], string='SPA Gender', related='spa_contact_id.sex')
    # Right
    spa_email = fields.Char(
        related='spa_contact_id.email', string='SPA Email Address')
    spa_office_landline = fields.Char(
        related='spa_contact_id.office_landline', string='SPA Office Landline No.')
    spa_sss_no = fields.Char(
        related='spa_contact_id.sss_no', string='SPA SSS No.')
    spa_pag_ibig_no = fields.Char(
        related='spa_contact_id.pag_ibig_no', string='SPA Pag-IBIG No.')
    spa_tin_no = fields.Char(
        related='spa_contact_id.tin_no', string='SPA Tin No.')
    spa_company_name = fields.Char(
        related='spa_contact_id.employer_name', string='SPA Company/Business Name')
    spa_company_address = fields.Char(
        related='spa_contact_id.company_address', string='SPA Company Address')
    spa_nature_business = fields.Char(
        related='spa_contact_id.nature_business', string='SPA Nature of Business')
    spa_designation = fields.Char(string='SPA Designation')
    spa_date_employed_established = fields.Date(
        related='spa_contact_id.date_employed_established', string='SPA Date Employed/Established')

    # Financial References

    loan_ids = fields.One2many(
        'ibas_realestate.financial_references_loan', 'parent_id', string="Loan")
    credit_cards_ids = fields.One2many(
        'ibas_realestate.financial_references_credit_cards', 'parent_id', string="Credit Cards")

    #loan_name = fields.Char('Name of Institution')
    #loan_type = fields.Char('Type of Loan')
    #loan_paid_granted = fields.Date('Date Paid/Granted')
    #loan_outstanding_balance = fields.Monetary('Outstanding Balance')
    #loan_month_amortization = fields.Monetary('Monthly Amortization')

    #credit_card_issuer = fields.Char('Card Issuer')
    #credit_card_number = fields.Char('Credit Card Number')
    #credit_limit = fields.Monetary('Credit Limit')
    #credit_card_name = fields.Char('Name on Card')

    # Personal References
    personal_ref_ids = fields.One2many(
        'ibas_realestate.contact_personal_references', 'parent_id', string="Personal References")
    #per_name = fields.Char('Name')
    #per_relation_buyer = fields.Char('Relation to Buyer')
    #per_residence_address = fields.Char('Residenece to Buyer')
    #per_office_address = fields.Char('Office Address')
    #per_contact_number = fields.Char('Contact Number')

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

    @api.onchange('last_name', 'first_name', 'middle_name', 'suffix')
    def customer_name_change(self):
        vals = {}
        if self.company_type:
            name = ''
            if self.last_name:
                name += self.last_name + ', '
            if self.first_name:
                name += self.first_name + ' '
            if self.suffix:
                name += self.suffix + ' '
            if self.middle_name:
                name += self.middle_name

            vals.update({'name': name})
        self.update(vals)

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


class IBASContactPersonalReferences(models.Model):
    _name = 'ibas_realestate.contact_personal_references'
    _description = 'Contact Personal References'

    # Personal References
    parent_id = fields.Many2one('res.partner', string="Customer")
    per_name = fields.Char('Name')
    per_relation_buyer = fields.Char('Relation to Buyer')
    per_residence_address = fields.Char('Residence Address')
    per_office_address = fields.Char('Office Address')
    per_contact_number = fields.Char('Contact Number')


class IBASContactFinancialReferencesLoan(models.Model):
    _name = 'ibas_realestate.financial_references_loan'
    _description = 'Contact Financial References Loan'

    parent_id = fields.Many2one('res.partner', string="Customer")
    loan_name = fields.Char('Name of Institution')
    loan_type = fields.Char('Type of Loan')
    loan_paid_granted = fields.Date('Date Paid/Granted')
    loan_outstanding_balance = fields.Float('Outstanding Balance')
    loan_month_amortization = fields.Float('Monthly Amortization')


class IBASContactFinancialReferencesCreditCard(models.Model):
    _name = 'ibas_realestate.financial_references_credit_cards'
    _description = 'Contact Financial References Credit Cards'

    parent_id = fields.Many2one('res.partner', string="Customer")
    credit_card_issuer = fields.Char('Card Issuer')
    credit_card_number = fields.Char('Credit Card Number')
    credit_limit = fields.Float('Credit Limit')
    credit_card_name = fields.Char('Name on Card')

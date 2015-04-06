# -*- coding: utf-8 -*-

from openerp import models, fields, api

class ebics_config(models.Model):
    _name = 'l10n_fr_ebics.ebics_config'
    name = fields.Char()
    bank_host = fields.Char()
    bank_port = fields.Integer()
    bank_root = fields.Text()
    bank_host_id = fields.Char()
     
    partner_id = fields.Char()
    user_id = fields.Char() #should be a many2one

    ebics_profile = fields.Selection([('t', 'EBICS T'), ('ts', 'EBICS TS')])
    ebics_country = fields.Selection([('fr', 'France')])
    ebics_version = fields.Selection([('h003', 'H003')])
    ebics_revision = fields.Selection([('1', '1')])
    ebics_specification = fields.Selection([('25', 'v2.5')])

    bank_auth_key_certificate = fields.Text()
    bank_auth_key_certificate_hash = fields.Char() #should'nt be stored, just checked and forget after HPB
    bank_auth_key_modulus = fields.Text()
    bank_auth_key_public_exponent = fields.Text()
    bank_auth_key_version = fields.Char()

    bank_encrypt_key_certificate = fields.Text()
    bank_encrypt_key_certificate_hash = fields.Char() #should'nt be stored, just checked and forget after HPB
    bank_encrypt_key_modulus = fields.Text()
    bank_encrypt_key_public_exponent = fields.Text()
    bank_encrypt_key_version = fields.Char()
     
    partner_auth_key_certificate = fields.Text()
    partner_auth_key_certificate_hash = fields.Char() #should'nt be stored, just checked and forget after HPB
    partner_auth_key_modulus = fields.Text()
    partner_auth_key_public_exponent = fields.Text()
    partner_auth_key_private_exponent = fields.Text()
    partner_auth_key_version = fields.Char()

    partner_encrypt_key_certificate = fields.Text()
    partner_encrypt_key_certificate_hash = fields.Char() #should'nt be stored, just checked and forget after HPB
    partner_encrypt_key_modulus = fields.Text()
    partner_encrypt_key_public_exponent = fields.Text()
    partner_encrypt_key_private_exponent = fields.Text()
    partner_encrypt_key_version = fields.Char()

    partner_sign_key_certificate = fields.Text()
    partner_sign_key_certificate_hash = fields.Char() #should'nt be stored, just checked and forget after HPB
    partner_sign_key_modulus = fields.Text()
    partner_sign_key_public_exponent = fields.Text()
    partner_sign_key_private_exponent = fields.Text()
    partner_sign_key_version = fields.Char()

    ca_key_pem = fields.Text()
    ca_cert_crt = fields.Text()
    ca_serial_srl = fields.Text()

    ini_letter = fields.Binary()
    hia_letter = fields.Binary()

    ebics_log_ids = fields.One2many('l10n_fr_ebics.ebics_log', 'ebics_config_id')



class ebics_log(models.Model):
    _name = 'l10n_fr_ebics.ebics_log'
    name = fields.Char()
    ebics_config_id = fields.Many2one('l10n_fr_ebics.ebics_config')
    date = fields.Datetime()
    content = fields.Text()

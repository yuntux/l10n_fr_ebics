# -*- coding: utf-8 -*-

from openerp import models, fields, api
from ebicspy import *


class ScreenLogger :
    def write(self, title, string):
        print title, string


class ebics_config(models.Model):

    ###################################################
    ################# LOGGER API STUB #################
    ###################################################
#    def write(self, title, string):
#        print title, string

    ###################################################
    ################# STORAGE API STUB ################
    ###################################################
    def saveBankKeys(self, bankName, auth_certificate, auth_modulus, auth_exponent, auth_version, encrypt_certificate, encrypt_modulus, encrypt_exponent, encrypt_version):
        self.write({'bank_auth_key_certificate': auth_certificate,
                    'bank_auth_key_modulus': auth_modulus,
                    'bank_auth_key_public_exponent': auth_exponent,
                    'bank_auth_key_version': auth_version,
                    'bank_encrypt_key_certificate': encrypt_certificate,
                    'bank_encrypt_key_modulus': encrypt_modulus,
                    'bank_encrypt_key_public_exponent': encrypt_exponent,
                    'bank_encrypt_key_version': encrypt_version})

    def partner_keys_already_exists(self, partnerName):
        res = False
        if self.partner_encrypt_key_modulus != False:
            res = True
        return res

    def bank_keys_already_exists(self, bankName, auth_version):
        res = False
        if self.bank_encrypt_key_modulus != False:
            res = True
        return res

    def getBankAuthKeyHash(self):
        return self.bank_auth_key_certificate_hash

    def getBankEncryptKeyHash(self):
        return self.bank_encrypt_key_certificate_hash

    def saveLetter(self, letter, letterType, partnerName, bankName):
        self.write({letterType+"_letter" : letter.encode('base64')})

    def loadCertificate(self, certificateType, partnerName):
        # TODO : check if the return value is correct, text field may no be splited in lines
        targetField = 'partner_'+certificateType+'_key_certificate'
        f = self.read([targetField])[0][targetField]
        certificate = ""
        for line in f :
            certificate += line.strip()
        certificate = certificate.replace('-----BEGIN CERTIFICATE-----', '').replace('-----END CERTIFICATE-----', '')
        return certificate

    def getPartnerKey(self, partnerName, keyType, keyLevel):
        # TODO : while the pertenr key is stored in PEM, modulus is empty
        targetField = 'partner_'+keyType+'_key_'+keyLevel+'_exponent'
        res = self.read([targetField])[0][targetField]
        return res

    def getBankKeyComponent(self, bankName, keyComponent, keyVersion):
        if keyVersion == "E002" :
            keyType = "encrypt"
        elif keyVersion == "X002" :
            keyType = "auth"
        targetField = 'bank_'+keyType+'_key_'+keyComponent
        res = self.read([targetField])[0][targetField]
        return res

    def saveCertificate(self, certificateType, partnerName, content, cert_req):
        self.write({"partner_"+certificateType+"_key_certificate" : content})
        #TODO : is it really usefull to keep the certification request .csr ?
        #self.write({"partner_"+certificateType+"_key_certificate_CASignRequest" : cert_req})

    def saveKey(self, keyType, owner, keyLevel, key) :
        # TODO : while the pertenr key is stored in PEM, modulus is empty
        self.write({"partner_"+keyType+"_key_"+keyLevel+"_exponent" : key})

    def saveCA(self, function, owner, cert, ca_key, ca_cert, ca_serial):
        #TODO : was is cert (4th argument ?)
        #In the final version, the three partner keys (expet sign for TS profils) will be sign with the save CA
        self.write({"ca_key_pem" : ca_key, "ca_cert_crt": ca_cert, "ca_serial_srl" : ca_serial})

    ###################################################
    ############### ODOO OBJECT FUNCTIONS #############
    ###################################################
    @api.one
    def init_connexion(self):
        print "%%%%%%%%%%%%%%%%%%%% init connexion %%%%%%%%%%%%%%%%%%%%"
        #logger = self
        #TODO : remane Logger.write en Logger.log in ebicsPy and replace ScreenLogger by self
        logger = ScreenLogger()
        storage = self
        bank = Bank(storage, 'testBankOdoo', self.bank_host, self.bank_port, self.bank_root, self.bank_host_id)
        partner = Partner(storage, 'testPartnerOdoo', self.partner_id, self.user_id, logger)
        partner.init(bank)
        return partner, bank

    @api.one
    def send_file(self):
        print "%%%%%%%%%%%%%%%%%%%% send file %%%%%%%%%%%%%%%%%%%%"
        partner, bank = self.init_connexion()
        #fileUpload_from_fileSystem(partner, bank, "/home/yuntux/HelloWorld","pain.xxx.cfonb160.dct", "t")  

    @api.one
    def get_file(self):
        print "%%%%%%%%%%%%%%%%%%%% get file %%%%%%%%%%%%%%%%%%%%"
#        self.saveLetter("test avec write", "ini", "a", "b")
        partner, bank = self.init_connexion()
        #fileDownload_to_fileSystem(partner, bank, "/home/yuntux/")

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

# vim:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

# -*- coding: utf-8 -*-

from openerp import models, fields, api
from ebicspy import *
import binascii


class ebics_config(models.Model):

    ###################################################
    ################# LOGGER API STUB #################
    ###################################################
    def logMessage(self, title, string):
        print title, string[:1500]
        self.env['l10n_fr_ebics.ebics_log'].create({'name':title, 'content':string, 'ebics_config_id':self.id})

    ###################################################
    ################# STORAGE API STUB ################
    ###################################################
    def getStatus(self, partnerName, bankName):
        res = self.read(["status"])[0]["status"]
        return res

    def getBankAuthKeyHash(self):
        return str(self.bank_auth_key_certificate_hash)

    def getBankEncryptKeyHash(self):
        return str(self.bank_encrypt_key_certificate_hash)

    def saveLetter(self, letter, letterType, partnerName, bankName):
        if letterType == "INI_letter_A005":
            letterType = "ini_letter_sign"
        if letterType == "HIA_letter_E002":
            letterType = "hia_letter_encrypt"
        if letterType == "HIA_letter_X002":
            letterType = "hia_letter_auth"
        self.write({letterType : letter.encode('base64')})


    def saveBankKeys(self, bankName, auth_certificate, auth_modulus, auth_exponent, auth_version, encrypt_certificate, encrypt_modulus, encrypt_exponent, encrypt_version):
        self.write({'bank_auth_key_certificate': auth_certificate,
                    'bank_auth_key_modulus': str(long(binascii.hexlify(auth_modulus), 16)),
                    'bank_auth_key_public_exponent': str(int(auth_exponent, 16)),
                    'bank_auth_key_version': auth_version,
                    'bank_encrypt_key_certificate': encrypt_certificate,
                    'bank_encrypt_key_modulus': str(long(binascii.hexlify(encrypt_modulus), 16)),
                    'bank_encrypt_key_public_exponent': str(int(encrypt_exponent, 16)),
                    'bank_encrypt_key_version': encrypt_version})
 
    def saveKey(self, keyType, owner, modulus, private_exponent, public_exponent) :
        #TODO : found the keyVersion with an other method
        if keyType == "encrypt" :
            keyVersion = "E002"
        elif keyType == "auth" :
            keyVersion = "X002"
        elif keyType == "sign":
            keyVersion = "A005"

        self.write({'partner_'+keyType+'_key_modulus': str(modulus),
                    'partner_'+keyType+'_key_public_exponent': str(public_exponent),
                    'partner_'+keyType+'_key_private_exponent': str(private_exponent),
                    'partner_'+keyType+'_key_version': keyVersion})
    
    def getPartnerKeyComponent(self, partnerName, keyComponent, keyType):
        targetField = 'partner_'+keyType+'_key_'+keyComponent
        res = self.read([targetField])[0][targetField]
        return long(res)

    def getBankKeyComponent(self, bankName, keyComponent, keyVersion):
        if keyVersion == "E002" :
            keyType = "encrypt"
        elif keyVersion == "X002" :
            keyType = "auth"
        targetField = 'bank_'+keyType+'_key_'+keyComponent
        res = self.read([targetField])[0][targetField]
        return long(res)

    def saveCertificate(self, certificateType, partnerName, content):
        self.write({"partner_"+certificateType+"_key_certificate" : content})

    def loadCertificate(self, certificateType, partnerName):
        # TODO : check if the return value is correct, text field may no be splited in lines
        targetField = 'partner_'+certificateType+'_key_certificate'
        f = str(self.read([targetField])[0][targetField])
        certificate = ""
        for line in f :
            certificate += line.strip()
        certificate = str(certificate).replace('-----BEGINCERTIFICATE-----', '').replace('-----ENDCERTIFICATE-----', '')
        return certificate
                   

    ###################################################
    ############### ODOO OBJECT FUNCTIONS #############
    ###################################################
    def init_connexion(self):
        bank = Bank(self, str(self.bank_name), str(self.bank_host), str(self.bank_port), str(self.bank_root), str(self.bank_host_id))
        partner = Partner(self, str(self.company_id.name), str(self.partner_id), str(self.user_id), self)
        partner.loadPartnerKeys()
        partner.loadBankKeys(bank, str(self.bank_encrypt_key_version), str(self.bank_encrypt_key_version))
        print "========== PARTNER KEYS AND CERTIFICATES LOADED =========="
        print "========== BANK KEYS AND CERTIFICATES LOADED =========="
        return partner,bank

    @api.one
    def send_file(self):
        partner,bank = self.init_connexion()
        fileUpload_from_fileSystem(partner, bank, "/home/yuntux/helloWorld.mp3","pain.xxx.cfonb160.dct", "fileName", True)  

    @api.one
    def get_file(self):
        partner,bank = self.init_connexion()
        fileDownload_to_fileSystem(partner, bank, "/home/yuntux/")

    @api.one
    def send_partner_keys(self):
        bank = Bank(self, str(self.bank_name), str(self.bank_host), str(self.bank_port), str(self.bank_root), str(self.bank_host_id))
        partner = Partner(self, str(self.company_id.name), str(self.partner_id), str(self.user_id), self)
        partner.createPartnerKeys()
        print "========== PARTNER KEY GENERATION OK =========="
        partner.handle_ini_exchange(bank)
        print "========== INI MESSAGE SENT =========="
        print "========== WE HAVE NOW TO SEND THE HIA MESSAGE =========="
        partner.handle_hia_exchange(bank)
        print "========== HIA MESSAGE SENT =========="
        print "===>>> YOU HAVE TO SEND INITIATION LETTERS TO YOUR BANK BEFORE DOWNLOADING THE BANK KEYS"
        self.status = "bank_init"

    @api.one
    def get_bank_keys(self):
        bank = Bank(self, str(self.bank_name), str(self.bank_host), str(self.bank_port), str(self.bank_root), str(self.bank_host_id))
        partner = Partner(self, str(self.company_id.name), str(self.partner_id), str(self.user_id), self)
        partner.loadPartnerKeys()
        bank_auth_key_hash = partner.storageService.getBankAuthKeyHash()
        bank_encrypt_key_hash = partner.storageService.getBankEncryptKeyHash()
        hpb_exchange(partner, bank, bank_auth_key_hash, bank_encrypt_key_hash)
        self.status = "ready"

    _name = 'l10n_fr_ebics.ebics_config'
    name = fields.Char()
    status = fields.Selection([('partner_init','Partner init'),('bank_init', 'Bank init'),('ready', 'Ready'), ('suspended', 'Suspended')],
                            required=True,
                            default="partner_init")
    company_id = fields.Many2one("res.company", string="Partner company", required=True)

    bank_name = fields.Char(required=True)
    bank_host = fields.Char(required=True)
    bank_port = fields.Integer(required=True)
    bank_root = fields.Text(required=True)
    bank_host_id = fields.Char(required=True)
     
    partner_id = fields.Char(required=True)
    user_id = fields.Char(required=True) #should be a many2one

    ebics_profile = fields.Selection([('t', 'EBICS T'), ('ts', 'EBICS TS')])
    ebics_country = fields.Selection([('fr', 'France')])
    ebics_version = fields.Selection([('h003', 'H003')])
    ebics_revision = fields.Selection([('1', '1')])
    ebics_specification = fields.Selection([('25', 'v2.5')])

    bank_auth_key_certificate = fields.Text()
    bank_auth_key_certificate_hash = fields.Char(required=True) #should'nt be stored, just checked and forget after HPB
    bank_auth_key_modulus = fields.Text()
    bank_auth_key_public_exponent = fields.Text()
    bank_auth_key_version = fields.Char()

    bank_encrypt_key_certificate = fields.Text()
    bank_encrypt_key_certificate_hash = fields.Char(required=True) #should'nt be stored, just checked and forget after HPB
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

    ini_letter_sign = fields.Binary()
    hia_letter_encrypt = fields.Binary()
    hia_letter_auth = fields.Binary()

    ebics_log_ids = fields.One2many('l10n_fr_ebics.ebics_log', 'ebics_config_id')



class ebics_log(models.Model):
    _name = 'l10n_fr_ebics.ebics_log'
    name = fields.Char()
    ebics_config_id = fields.Many2one('l10n_fr_ebics.ebics_config', "EBICS Configuration", required=True)
    content = fields.Text(required=True)

# vim:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

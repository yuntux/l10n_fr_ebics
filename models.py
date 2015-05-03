# -*- coding: utf-8 -*-

from openerp import models, fields, api
from ebicspy import *
import binascii


class ebics_config(models.Model):

    ###################################################
    ################# LOGGER API STUB #################
    ###################################################
    def logMessage(self, level, title, string):
        print level, title, string[:1500]
        self.env['l10n_fr_ebics.ebics_log'].create({'name':title, 'level':level, 'content':string, 'ebics_config_id':self.id})

    ###################################################
    ################# STORAGE API STUB ################
    ###################################################
    def getStatus(self):
        res = self.read(["status"])[0]["status"]
        return res

    def setStatus(self, status):
        self.write({'status' : status})

    def getBankAuthKeyHash(self):
        return str(self.bank_auth_key_certificate_hash)

    def getBankEncryptKeyHash(self):
        return str(self.bank_encrypt_key_certificate_hash)

    def saveLetter(self, letter, letterType):
        self.write({letterType : letter.encode('base64')})

    def saveBankKey(self, keyType, keyVersion, modulus, public_exponent, certificate) :
        self.write({'bank_'+keyType+'_key_certificate': certificate,
                    'bank_'+keyType+'_key_modulus': str(long(binascii.hexlify(modulus), 16)),
                    'bank_'+keyType+'_key_public_exponent': str(int(public_exponent, 16)),
                    'bank_'+keyType+'_key_version': keyVersion})

    def savePartnerKey(self, keyType, keyVersion, modulus, private_exponent, public_exponent, certificate) :
        self.write({"partner_"+keyType+"_key_certificate" : certificate,
					'partner_'+keyType+'_key_modulus': str(modulus),
                    'partner_'+keyType+'_key_public_exponent': str(public_exponent),
                    'partner_'+keyType+'_key_private_exponent': str(private_exponent),
                    'partner_'+keyType+'_key_version': keyVersion})
    
    def getPartnerKeyComponent(self, keyComponent, keyType):
        targetField = 'partner_'+keyType+'_key_'+keyComponent
        res = self.read([targetField])[0][targetField]
        return long(res)

    def getBankKeyComponent(self, keyComponent, keyType):
        targetField = 'bank_'+keyType+'_key_'+keyComponent
        res = self.read([targetField])[0][targetField]
        return long(res)

    def getPartnerCertificate(self, certificateType):
        targetField = 'partner_'+certificateType+'_key_certificate'
        return str(self.read([targetField])[0][targetField])

    ###################################################
    ############### ODOO OBJECT FUNCTIONS #############
    ###################################################
    def init_connexion(self):
        bank = Bank(self, str(self.bank_name), str(self.bank_host), str(self.bank_port), str(self.bank_root), str(self.bank_host_id))
        partner = Partner(self, str(self.company_id.name), str(self.partner_id), str(self.user_id), self)
        partner.loadPartnerKeys()
        partner.loadBankKeys(bank)
        print "========== PARTNER KEYS AND CERTIFICATES LOADED =========="
        print "========== BANK KEYS AND CERTIFICATES LOADED =========="
        return partner,bank

    def hook_pre_send_file(self, partner, bank, dic):
        #fileUpload_from_fileSystem(partner, bank, "/home/yuntux/helloWorld.mp3","pain.xxx.cfonb160.dct", "fileName", True)  
        fileUpload_from_fileSystem(partner, bank, "/home/yuntux/helloWorld.txt","pain.xxx.cfonb160.dct", "fileName", True)  

    def hook_post_get_file(self, partner, bank, dic):
        fileDownload_to_fileSystem(partner, bank, "/home/yuntux/")

    @api.one
    def send_file(self):
        partner,bank = self.init_connexion()
        self.hook_pre_send_file(partner, bank, None)

    @api.one
    def get_file(self):
        partner,bank = self.init_connexion()
        self.hook_post_get_file(partner, bank, None)

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
        self.setStatus("bank_init")

    @api.one
    def get_bank_keys(self):
        bank = Bank(self, str(self.bank_name), str(self.bank_host), str(self.bank_port), str(self.bank_root), str(self.bank_host_id))
        partner = Partner(self, str(self.company_id.name), str(self.partner_id), str(self.user_id), self)
        partner.loadPartnerKeys()
        bank_auth_key_hash = partner.storageService.getBankAuthKeyHash()
        bank_encrypt_key_hash = partner.storageService.getBankEncryptKeyHash()
        hpb_exchange(partner, bank, bank_auth_key_hash, bank_encrypt_key_hash)
        self.setStatus("ready")

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
    ebics_config_id = fields.Many2one('l10n_fr_ebics.ebics_config', "EBICS Configuration", required=True, ondelete='cascade')
    content = fields.Text(required=True)
    level = fields.Text(required=True)

# vim:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

from .views import MailingListSignup, QuickMailingListSignup, MailingListMerci

class MailingListSignupM(MailingListSignup):
    template_name = 'mailing_list/signup_m.html'
    merci_template = 'mailing_list/merci_m.html'

class QuickMailingListSignupM(QuickMailingListSignup):
    template_name = 'mailing_list/quick_signup_m.html'
    merci_template = 'mailing_list/merci_m.html'

class MailingListMerciM(MailingListMerci):
    template_name = 'mailing_list/merci_m.html'

import imaplib
from BeautifulSoup import BeautifulSoup
import error

#this function fetch emails from gmail and look for validation link
def fetch_activation_link(username, password, mailalias = None):

    #username is name of the user to login to gmail account, password is real password, mailalias is alias name for account

    print("Fetching email from gmail server")

    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    if (mailalias is None):
        mailalias = username
    mail.login(username, password)
    mail.select("inbox")

    result, data = mail.search(None,'(TO "%s" SUBJECT "Portal user email activation")' % (mailalias))
    ids = data[0] # data is a list.
    id_list = ids.split() # ids is a space separated string
    latest_email_id = id_list[-1] # get the latest

    if (1):
        result, data = mail.fetch(latest_email_id, "(RFC822)") # fetch the email body (RFC822) for the given ID
        mail.store(latest_email_id, '+FLAGS', '\\Deleted') # delete this email
        soup  = BeautifulSoup(data[0][1])
        for link in soup.findAll('a'):
            l = link.get('href')
            if ('email_activation' in l):
                return l
    return None

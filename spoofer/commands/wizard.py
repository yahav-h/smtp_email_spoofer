from colorama import Fore
from getpass import getpass
from ..utils import logger as cout, appdescription
from ..utils.userinput import prompt, get_required, get_optional, get_yes_no
from ..utils.config import Config
from ..models.smtpconnection import SMTPConnection


def run(args):
    appdescription.print_description()

    host = get_required('SMTP host: ')
    port = None

    while not port:
        try:
            port = int(get_required('SMTP port: '))
            if port < 0 or port > 65535:
                cout.error('SMTP port is out-of-range (0-65535)')
                port = None
        except ValueError:
            cout.error('SMTP port must be a number')
            port = None

    # Connect to SMTP over TLS
    connection = SMTPConnection(host, str(port))

    # Attempt login
    if not get_yes_no("Disable authentication (Y/N)?: ", 'n'):
        success = False
        while not success:
            success = connection.login(
                get_required('Username: '),
                getpass()
            )
        cout.success('Authentication successful')

    sender = get_required('Sender address: ')
    sender_name = get_required('Sender name: ')

    recipients = [get_required('Recipient address: ')]
    if get_yes_no('Enter additional recipients (Y/N)?: ', 'n'):
        while recipients:
            recipient = get_optional('Recipient address: ', None)
            if recipient:
                recipients.append(recipient)
            else:
                break

    subject = get_required('Subject line: ')

    html = ''
    if get_yes_no('Load message body from file (Y/N)?: ', 'n'):
        filename = get_required('Filename: ')
        with open(f'{Config.get_templates()}/{filename}') as f:
            html = f.read()
    else:
        cout.info('Enter HTML line by line')
        cout.info('To finish, press CTRL+D (*nix) or CTRL-Z (win) on an *empty* line')
        while True:
            try:
                line = prompt('>| ', Fore.LIGHTBLACK_EX)
                html += line + '\n'
            except EOFError:
                cout.success('Captured HTML body')
                break

    if get_yes_no('Load message HEADERS (Y/N)?: ', 'n'):
        message_headers = get_optional('Message HEADERS: ', None)
    else:
        cout.info('Message HEADERS not laded')
        message_headers = None

    if get_yes_no('Load message Attachment (Y/N)?: ',  'n'):
        attachments = [get_optional('Message Attachments:', None)]
    else:
        cout.info('Message Attachments not loaded')
        attachments = None

    # Compose MIME message
    message = connection.compose_message(
        sender,
        sender_name,
        recipients,
        subject,
        html,
        message_headers,
        attachments
    )

    if get_yes_no('Send message (Y/N)?: ', None):
        connection.send_mail(message)

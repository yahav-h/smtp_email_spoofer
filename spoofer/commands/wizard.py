from colorama import Fore
from getpass import getpass
from ..utils import logger as cout, appdescription
from ..utils.userinput import prompt, get_required, get_optional, get_yes_no
from ..utils.config import Config
from ..utils.lambdas import clearConsole
from ..models.smtpconnection import SMTPConnection
from concurrent.futures import FIRST_EXCEPTION, wait, ThreadPoolExecutor


def run(args):
    clearConsole()
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
                cout.info(f'Recipient[s] are {recipients}')
                break

    subject = get_required('Subject line: ')

    # Add Unique UUID to Subject
    unique_uuid = False
    if get_yes_no('Add UUID to Subject (Y/N)?: ',  'n'):
        unique_uuid = True

    isCC = False
    if get_yes_no('Split to CC (Y/N)?: ', 'n'):
        isCC = True

    html = ''
    if get_yes_no('Load message body template (Y/N)?: ', 'n'):
        filename = get_required('Body template: ')
        with open(f'{Config.get_templates()}/{filename}') as f:
            html = f.read().replace('{{userName}}', recipients[0])

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
        cout.info('Message HEADERS not loaded')
        message_headers = None

    if get_yes_no('Load message Attachment (Y/N)?: ',  'n'):
        attachments = [get_optional('Message Attachments: ', None)]
        if get_yes_no('Load another attachment to message (Y/N)?: ', 'n'):
            while attachments:
                attachment = get_optional('Load Message Attachments: ', None)
                if attachment:
                    attachments.append(attachment)
                else:
                    break
        else:
            cout.info(f'Attachment[s] are {attachments}')
    else:
        attachments = [None]

    # Compose MIME message
    message = connection.compose_message(
        sender,
        sender_name,
        recipients,
        subject,
        html,
        message_headers,
        attachments,
        withUUID=unique_uuid,
        isCC=isCC
    )

    if get_yes_no("Mass Send (Y/N)?: ", 'n'):
        mass_send = int(get_required("Mass Send Number: "))
    else:
        mass_send = 1

    if get_yes_no('Send message (Y/N)?: ', None):
        for i in range(0, mass_send):
            message['Subject'] = message['Subject'] + f" {i + 1}"
            connection.send_mail(message)
            cout.info(f"expect: {message['Subject']}")
        cout.success("Done!")

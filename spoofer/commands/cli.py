from spoofer.utils import logger, appdescription
from ..models.smtpconnection import SMTPConnection
from ..utils.userinput import get_yes_no
from ..utils.config import Config


def run(args):
    appdescription.print_description()

    args.uuid = True if args.uuid == 1 else False

    # Connect to SMTP over TLS
    connection = SMTPConnection(args.host, str(args.port))

    # Attempt login
    if not args.noauth:
        success = connection.login(args.username, args.password)
        if success:
            logger.success('Authentication successful')
        else:
            exit(1)

    try:
        with open(f'{Config.get_templates()}/{args.filename}') as f:
            data = f.read()
            if '{{userName}}' in data:
                email = args.recipients[0]
                data = data.replace('{{userName}}', email)
            message_body = data
    except FileNotFoundError:
        logger.error("No such file: " + args.filename)
        exit(1)

    if not args.headers:
        message_headers = None
    else:
        message_headers = args.headers

    if not args.attachments:
        attachments = [None]
    else:
        attachments = [args.attachments]

    # Compose MIME message
    message = connection.compose_message(
        args.sender,
        args.name,
        args.recipients,
        args.subject,
        message_body,
        message_headers,
        attachments,
        withUUID=args.uuid
    )

    if get_yes_no('Send message (Y/N)?: ', None):
        connection.send_mail(message)


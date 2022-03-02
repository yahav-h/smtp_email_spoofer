import smtplib
import time
import datetime
from socket import gaierror
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from spoofer.utils import logger as cout
from os.path import basename
from ..utils.config import Config
from ..utils.lambdas import getUUID


class SMTPConnection:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = str(host) + ':' + str(port)
        self.server = None
        self.sender = None
        self.to = None
        self.cc = None
        self.bcc = None
        self.attachments = None
        self.username = None

        self.__connect()
        self.__start_tls()
        self.__eval_server_features()

    def __ehlo(self):
        try:
            self.server.ehlo()
            if not self.server.does_esmtp:
                cout.error('The server does not support ESMTP')
                exit(1)
        except smtplib.SMTPHeloError as e:
            cout.error('The server did not reply properly to the EHLO/HELO greeting.')
            cout.error(':Error Cause:')
            cout.error(f'{e.with_traceback(e.__traceback__)}')
            exit(1)

    def __connect(self):
        try:
            cout.info('Connecting to SMTP socket (' + self.socket + ')...')
            self.server = smtplib.SMTP(self.host, self.port)
        except (gaierror, OSError) as e:
            cout.error('Unable to establish connection to SMTP socket.')
            cout.error(':Error Cause:')
            cout.error(f'{e.with_traceback(e.__traceback__)}')
            exit(1)

    def __start_tls(self):
        self.__ehlo()
        if not self.server.has_extn('starttls'):
            cout.error('SMTP server does not support TLS.')
            exit(1)
        else:
            try:
                cout.info('Starting TLS session...')
                self.server.starttls()
            except RuntimeError as e:
                cout.error('SSL/TLS support is not available to your Python interpreter.')
                cout.error(':Error Cause:')
                cout.error(f'{e.with_traceback(e.__traceback__)}')
                exit(1)

    def __eval_server_features(self):
        self.__ehlo()

        if not self.server.has_extn('auth'):
            cout.error('No AUTH types detected.')
            exit(1)

        server_auth_features = self.server.esmtp_features.get('auth').strip().split()
        supported_auth_features = {auth_type for auth_type in {'PLAIN', 'LOGIN'} if auth_type in server_auth_features}

        if not supported_auth_features:
            cout.error('SMTP server does not support AUTH PLAIN or AUTH LOGIN.')
            exit(1)

    def login(self, username, password):
        try:
            self.username = username
            return self.server.login(self.username, password)
        except smtplib.SMTPAuthenticationError as e:
            cout.error('The server did not accept the username/password combination.')
            cout.error(':Error Cause:')
            cout.error(f'{e.with_traceback(e.__traceback__)}')
            return False
        except smtplib.SMTPNotSupportedError as e:
            cout.error('The AUTH command is not supported by the server.')
            cout.error(':Error Cause:')
            cout.error(f'{e.with_traceback(e.__traceback__)}')
            exit(1)
        except smtplib.SMTPException as e:
            cout.error('Encountered an error during authentication.')
            cout.error(':Error Cause:')
            cout.error(f'{e.with_traceback(e.__traceback__)}')
            exit(1)

    def compose_message(self, sender, name, to, cc, bcc, subject, html, headers, attachments, withUUID, type='html'):
        self.sender = sender
        self.to = to
        self.cc = cc
        self.bcc = bcc
        # print("List : %s" % self.recipients)
        self.attachments = attachments
        assert isinstance(self.to, list)
        assert isinstance(self.cc, list)
        assert isinstance(self.bcc, list)
        assert isinstance(self.attachments, list)
        uuid = getUUID()
        message = MIMEMultipart('alternative')
        message.set_charset("utf-8")
        message['From'] = f'{name} <{self.sender}>'
        message['Subject'] = f"{uuid.hex} - {subject}" if withUUID else f"{subject}"
        message['Date'] = formatdate(localtime=True, usegmt=True, timeval=0.750)
        recipientsTo = ','.join(self.to)
        message['To'] = recipientsTo
        recipientsCc = ','.join(self.cc)
        message['Cc'] = recipientsCc
        message['Message-ID'] = uuid.hex
        message['timestamp'] = str(time.time())
        message['Date'] = datetime.datetime.utcnow().isoformat()
        message.add_header('Reply-To', self.sender)

        if not headers:
            pass
        else:
            for key, value in headers.items():
                message.add_header(_name=key, _value=value)

        body = MIMEText(html, type)
        message.attach(body)
        if None in self.attachments:
            pass
        else:
            for attch in self.attachments:
                fil = open(f'{Config.get_attachments()}/{attch}', "rb")
                part = MIMEApplication(fil.read(), Name=basename(attch))
                # After the file is closed
                part['Content-Disposition'] = 'attachment; filename="%s"' % basename(attch)
                message.attach(part)
        # cout.info(f":: Message generated ::\n{message}")
        return message

    def send_mail(self, message):
        try:
            cout.info('Sending spoofed message...')
            self.server.sendmail(self.sender, self.to + self.cc + self.bcc, message.as_string())
            cout.success('Message sent!')
        except smtplib.SMTPException as e:
            cout.error('Unable to send message. Check sender, recipients and message body')
            cout.error(':Error Cause:')
            cout.error(f'{e.with_traceback(e.__traceback__)}')
            exit(1)

    def quit(self):
        try:
            self.server.quit()
        except Exception as e:
            cout.error(e)
            exit(1)
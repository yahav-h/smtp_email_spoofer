import smtplib
from socket import gaierror
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from spoofer.utils import logger as cout
from uuid import NAMESPACE_X500, uuid5
from time import time

stamp = lambda: time().__str__()[:10]


class SMTPConnection:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = host + ':' + port
        self.server = None
        self.sender = None
        self.recipients = None
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
        except smtplib.SMTPHeloError:
            cout.error('The server did not reply properly to the EHLO/HELO greeting.')
            exit(1)

    def __connect(self):
        try:
            cout.info('Connecting to SMTP socket (' + self.socket + ')...')
            self.server = smtplib.SMTP(self.host, self.port)
        except (gaierror, OSError):
            cout.error('Unable to establish connection to SMTP socket.')
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
            except RuntimeError:
                cout.error('SSL/TLS support is not available to your Python interpreter.')
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
        except smtplib.SMTPAuthenticationError:
            cout.error('The server did not accept the username/password combination.')
            return False
        except smtplib.SMTPNotSupportedError:
            cout.error('The AUTH command is not supported by the server.')
            exit(1)
        except smtplib.SMTPException:
            cout.error('Encountered an error during authentication.')
            exit(1)

    def compose_message(self, sender, name, recipients, subject, html, headers):
        self.sender = sender
        self.recipients = recipients

        message = MIMEMultipart('alternative')
        message.set_charset("utf-8")
        message["From"] = f'{name} <{self.sender}>'
        message['Subject'] = f"{uuid5(NAMESPACE_X500, stamp())} - {subject}"
        message["To"] = ', '.join(self.recipients)

        if not headers:
            pass
        else:
            headers_list = headers.replace("{", "").replace("}", "").replace('"', "").split(":")
            key, value = None, None
            for i in range(0, len(headers_list)):
                key = headers_list[i]
                value = headers_list[i]
                break
            cout.info(f'Key = {key}')
            cout.info(f'Value = {value}')
            message.add_header(_name=key, _value=value)
        body = MIMEText(html, 'html')
        message.attach(body)
        cout.info(f"Message generated : {message}")
        cout.info(f"Original Sender : {self.username}")
        cout.info(f"Spoofed Sender : {message['From']}")
        cout.info(f"Recipient[s] : {message['To']}")
        cout.info(f"Subject : {message['Subject']}")
        cout.info(f"Headers : {headers}")
        cout.info(f"Attachments : {message.get_filename()}")
        cout.info(f"HTML : {html}")
        return message

    def send_mail(self, message):
        try:
            cout.info('Sending spoofed message...')
            self.server.sendmail(self.sender, self.recipients, message.as_string())
            cout.success('Message sent!')
        except smtplib.SMTPException:
            cout.error('Unable to send message. Check sender, recipients and message body')
            exit(1)

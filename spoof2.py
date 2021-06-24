from spoofer.utils.config import Config
from spoofer.models.smtpconnection import SMTPConnection, cout
import json


global sender, counter, collected_ids
sender = {}
counter = 0
collected_ids = []
SUBJECT = "Yahav mail "


def main():
    global collected_ids, sender
    data = Data()

    with open(f"{Config.get_templates()}/{data.body}", "r") as fin:
        html = fin.read()
        html = html.replace("{{userName}}", ", ".join(data.recipients))

    for s in data.senders:
        cout.info(f"sender is {s['inbox']} . . . ")
        sender = s
        try:
            for i in range(data.max):
                send(data, html)
        except:
            continue


def send(data, html):
    global collected_ids
    conn: SMTPConnection = SMTPConnection(data.host, data.port)
    email, pwd = sender['inbox'], sender['pwd']
    conn.login(email, pwd)
    msg = conn.compose_message(
        sender=email,
        name=email.split('@')[0],
        recipients=data.recipients,
        subject=SUBJECT,
        html=html,
        headers='',
        attachments=data.attachments,
        withUUID=0,
        isCC=0
    )
    hex_id = msg['Message-ID']
    msg['Subject'] = msg['Subject'] + str(hex_id)
    conn.send_mail(msg)
    cout.info(f"Sent from {email} to {msg['To']}")
    conn.quit()
    collected_ids.append(hex_id)


class Data(object):
    def __init__(self):
        self.__load()

    @classmethod
    def __load(cls):
        with open(Config.get_templates() + "/config.json", 'r') as fin:
            data = json.load(fin)
        for k, v in data.items():
            setattr(cls, k, v)
        return cls

    def __repr__(self):
        return '<Data %r>' % self.__dict__


if __name__ == '__main__':
    import pprint
    main()
    pprint.pprint(collected_ids)

from spoofer.utils.config import Config
from spoofer.models.smtpconnection import SMTPConnection, cout
from concurrent.futures import ThreadPoolExecutor, FIRST_EXCEPTION, wait
from dataclasses import dataclass, field, asdict
import json
import datetime

global collected_ids
collected_ids = []


@dataclass
class Data(object):
    def __init__(self):
        self.__load()

    @classmethod
    def __load(cls):
        with open(Config.get_config_file(), 'r') as fin:
            data = json.load(fin)
        for k, v in data.items():
            setattr(cls, k, v)
        return cls

    def __repr__(self): return '<Data %r>' % asdict(self)


@dataclass
class Sender(object):
    email: str = field(init=True)
    pwd: str = field(init=True)


def threaded_main():
    global collected_ids
    data = Data()
    all_senders = data.senders
    senders = []
    for s in all_senders:
        senders.append(Sender(email=s['inbox'], pwd=s['pwd']))

    def thread(sender, data):
        try:
            global collected_ids
            counter = 0
            with open(f'{Config.get_templates()}/{data.body}', 'r') as fin:
                html = fin.read()
                if html.__contains__('{{userName}}'):
                    html = html.replace('{{userName}}', data.to[0])
            subjects = []
            while counter < data.max:
                conn = SMTPConnection(data.host, data.port, data.tls)
                if data.tls:
                    conn.login(sender.email, sender.pwd)
                msg = conn.compose_message(
                    sender=sender.email,
                    name=sender.email.split('@')[0],
                    to=data.to,
                    cc=data.cc,
                    bcc=data.bcc,
                    subject=data.subject,
                    html=html,
                    headers=data.headers,
                    attachments=data.attachments,
                    withUUID=data.add_msgid_to_subject,
                    msg_type=data.msg_type
                )
                hex_id = msg['Message-ID']
                subjects.append(msg['Subject'])
                conn.send_mail(msg)
                cout.success(f'Sender {sender.email} sent message {hex_id} to {", ".join(data.to)}')
                conn.quit()
                collected_ids.append(hex_id)
                counter += 1
            return True, subjects
        except Exception as e:
            return False, None

    with ThreadPoolExecutor(max_workers=len(senders)) as execs:
        fs = []
        futures = []
        results = []
        for sender in senders:
            fs.append(execs.submit(thread, sender, data))
        states = []
        for f in fs:
            states.append(wait(fs=[f], timeout=666, return_when=FIRST_EXCEPTION))
        if all([state.done for state in states]):
            futures = [s.done.pop() for s in states]
            if all([f._state == 'FINISHED' for f in futures]):
                results = [f.result() for f in futures]
                cout.success(results)
            cout.success("Done sending emails")
        else:
            cout.error("not Done")
    from pprint import pprint
    pprint(collected_ids)


if __name__ == '__main__':
    threaded_main()

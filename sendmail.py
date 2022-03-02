#!/usr/bin/env python3
import datetime
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_EXCEPTION
import subprocess
import shlex
import random
import uuid


def build_eml(to, subject, msgid, eml):
    with open(eml, 'r') as fout:
        data = fout.read()
        data = data.replace('{{to}}', to).replace('{{subject}}', subject + ' ' + msgid).replace('{{msgid}}', msgid)
        with open(f'./templates/{msgid}.eml', 'w') as fin:
            fin.write(data)
            fin.close()
        fout.close()
    return msgid


def sendmail_proc(subj, msgid):
    cmd = 'echo -e "Subject:'+str(subj)+' '+str(msgid)+'" | /usr/sbin/sendmail -vt < ./templates/'+str(msgid)+'.eml'
    cmd = shlex.split(cmd)
    try:
        proc = subprocess.Popen(
            cmd,
            start_new_session=True,
            shell=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE
        )
        proc.communicate()
        return True
    except:
        return False


if __name__ == '__main__':
    import sys
    args = sys.argv[1:]
    ttl = int(args[0])
    subj = args[1]
    recip = args[2]
    eml = args[3]
    eml_type = eml.split('/').pop().split('.')[0]
    with ThreadPoolExecutor(max_workers=ttl) as executor:
        fs = []
        for i in range(0, ttl):
            subject = subj + ' ' + datetime.datetime.now().isoformat() + ' ' + eml_type
            msgid = build_eml(recip, subject, uuid.uuid5(uuid.NAMESPACE_DNS, random.random().hex()).hex, eml)
            fs.append(executor.submit(sendmail_proc, subject, msgid))

        states = []
        for f in fs:
            states.append(wait(fs=[f], timeout=666, return_when=FIRST_EXCEPTION))
        if all([state.done for state in states]):
            futures = [s.done.pop() for s in states]
            if all([f._state == 'FINISHED' for f in futures]):
                results = [f.result() for f in futures]
                print(results)
            print("Done sending emails")
        else:
            print("not Done")

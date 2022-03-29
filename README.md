# smtp_email_spoofer
Python 3.x based email spoofer 

> *For educational purposes only. Do not send to or from addresses that you do not own.* 

> Email spoofing is often used for spam campaigns and phishing attacks. If you use this tool inappropriately, you could violate of the [CAN-SPAM Act of 2003](https://en.wikipedia.org/wiki/CAN-SPAM_Act_of_2003) and/or the [Computer Fraud and Abuse Act](https://en.wikipedia.org/wiki/Computer_Fraud_and_Abuse_Act). You'd also be committing [wire fraud](https://en.wikipedia.org/wiki/Mail_and_wire_fraud#Wire). **Use your head**.

----

## Table of Contents

- [Getting Started](#getting-started)
- [Commands](#commands)
  - [Wizard](#wizard)
  - [CLI](#cli)

## <a id="getting-started">Getting Started</a>

1. `$ git clone https://github.com/yahav-h/smtp_email_spoofer.git`
3. Activate `virtualenv`
2. `$ pip install -r requirements.txt`
3. `$ python spoof.py`

## <a id="commands">Commands</a>

`smtp-email-spoofer-py` offers two global commands: [`wizard`](#wizard) and [`cli`](#cli):

```bash
$ py spoof.py -h
usage: spoof.py [-h] {wizard,cli} ...

Python 3.x based email spoofer

optional arguments:
  -h, --help    show this help message and exit

commands:
  {wizard,cli}  Allowed commands
    wizard      Use the step-by-step wizard
    cli         Pass arguments directly
```    

----

### <a id="wizard">Wizard</a>

Issue the `wizard` command to use the step-by-step wizard:

```
$ py spoof.py wizard
```

1. Enter the SMTP server information to establish a connection over TLS - you'll need to enter the HOST and PORT

2. Optionally provide credentials to login to the SMTP server - use email credentials

3. Compose the forged message - either select a template like `exmaple.html` / `phishing_ex.html` or create your own from the shell.

> Load the HTML message body from a file, or compose it within the shell

4. Send the message

----

### <a id="cli">CLI - based on arguments</a>

Issue the `cli -h` command to view the help:

```bash
$ py spoof.py cli -h
usage: spoof.py cli [-h] (--noauth | --username USERNAME)
                    [--password PASSWORD] --host HOST --port PORT --sender
                    SENDER --name NAME --recipients RECIPIENTS
                    [RECIPIENTS ...] --subject SUBJECT --filename FILENAME

optional arguments:
  -h, --help            show this help message and exit
  --noauth              Disable authentication check
  --username USERNAME   SMTP username
  --password PASSWORD   SMTP password (required with --username)

required arguments:
  --host HOST           SMTP hostname
  --port PORT           SMTP port number
  --sender SENDER       Sender address (e.g. spoofed@domain.com)
  --name NAME           Sender name (e.g. John Smith)
  --recipients RECIPIENTS [RECIPIENTS ...]
                        Recipient addresses (e.g. victim@domain.com ...)
  --subject SUBJECT     Subject line
  --filename FILENAME   Message body filename (e.g. example.html)
  --headers HEADERS     Message headers (e.g. '{"MY-HEADER : MY-VALUE"}')
```

1. Issue the `cli` command along with the appropriate arguments:

> If `--noauth` is not specified, `--username` and `--password` are required.

---

### <a id="cli">CLI - based on configuration file</a>

Let's walk through the `config.json` file : 

```json
{
  "senders": [
    {"inbox": "", "pwd": ""}
  ],
  "to": [],
  "cc":  [],
  "bcc": [],
  "msg_type": "html",
  "subject": "",
  "body": "",
  "max": 1,
  "attachments": [],
  "host": "smtp.gmail.com",
  "port": 587,
  "tls": true,
  "add_msgid_to_subject": false,
  "message_charset": "utf-8",
  "multipart_type": "alternative",
  "headers": {},
  "email": null,
  "pwd": null
}
```
---
+ `"senders"` key represents a list of credential of Mailboxes stored in an object. 
+ The `"senders"` list open a thread per object by which then used to connect and send traffic through.
---
+ `"to"` key represents a list of Mailboxes we want to attach into the `"To:"` message header. 
+ there is no limitation for Mailboxes to send.
---
+ `"cc"` key represents a list of Mailboxes we want to attach into the `"Cc:"` message header.
+ there is no limitation for Mailboxes to send.
---
+ `"bcc"` key represents a list of Mailboxes we want to combine to the following recipients. 
+ there is no limitation for Mailboxes to send.
---
+ `"msg_type"` key represents the MIME-TYPE representation of the message being sent.
+ `"msg_type": "html"` for HTML representation
+ `"msg_type": "xml"` for XML representation
+ `"msg_type": "plain"` for TEXT representation
+ `"msg_type": "eml"` for EML representation
---
+ `"subject"` key represents the attached `"Subject:"` message header
---
+ `"body"` key refers to which type of custom template from `templates/` folder to load into the message body.
+ `"body": "phishing_ex_it.html"` for as example , will load a `Gmail Alert` Phishing Template.
---
+ `"max"` key represents the total messages to send per `"sender"` object.
+ assuming `"max": 5` and we have 5 `"senders"`, the total sum of messages distribution will be 25.
---
+ `"attachments"` key represents a list of `MIMEMultipart` attachments that will add to the message payload from the `attachments/` folder. 
+ `"attachments": ["scpt.\u200Fdat"]` for example will attach malicious applescript into the message as payload.  
---
+ `"host"` key represents the mail provider SMTP Server host CNAME.
+ `"host": "smtp.gmail.com"` for Google/Gsuite/Gmail Mail Provider.
+ `"host": "smtp.office365.com"` for MS / Outlook Mail Provider.
---
+ `"port"` key represents the mail provider SMTP Server serving port.
+ `"port": 587` for services such as MS / Google (this may change from provider to provider)
---
+ `"tls"` key represents the process of authentication between out SMTP Client and SMTP Server and my change according to the provider protocol.
+ keep `"tls": true` if an authentication is required.
---
+ `"add_msgid_to_subject"` key will tell the program to concatenate the `"Message-ID"` message header to the `"Subject:"` message header.
+ set `"add_msgid_to_subject": true` if we want to create a unique subject per sent message.
+ set `"add_msgid_to_subject": false` if we want only your subject.
---
+ `"message_charset"` key will override the message charset with different encoding. 
+ commonly `"message_charset": "utf-8"` should be used, you can explore what kind of behavior the SMTP Server will have with different message encoding (try `"gbk"` or `"iso-8859-1"`).
---
+ `"multipart_type"` key represents the `MIMEMultipart` type by which the SMTP Client send a set of data combination in the messages body. 
+ commonly `"multipart_type": "alternative"` should be used, but feel free to explore ([Protocols rfc1341 7.2 Multipart](https://www.w3.org/Protocols/rfc1341/7_2_Multipart.html)).
---
+ `"headers"` key represents a mapping of custom headers we want to apply to the message. 
+ we can use this approach for impersonation.
```commandline
"headers": {
    "Reply-To": "j-hops@microsoft.com", 
    "Sender": "James Hopkins <j-hops@microsoft.com>"
}
```
+ or for bypassing mail protection using fake DMARC and SPF for mail authenticity 
```commandline
"headers": {
    "feedback-type": "abuse", 
    "user-agent": "SomeGenerator/1.0", 
    "from": "somespammer@demo.dmacanalyzer.com"
    "subject": "Earn Money", 
    "mime-version" "1.0",
    "version": "1",
    "content-type": "text/plain"
    "original-mail-from": "<somespammer@demo.dmacanalyzer.com>",
    "original-recp-to": "<user@example.com>",
    "arrival-date": "Thu, 8 Mar 2022 14:00:00 EDT",
    "reporting-mta": "dns; mail.example.com",
    "source-ip": "192.0.2.15",
    "authentication-results": "mail.example.com\n\r\rspf=pass p=none smtp.mail=somespammer@demo.dmacanalyzer.com",
    "reported-domain": "demo.dmarcanalyzer.com",
    "reported-uri": "http://example.net/earn_money.html\n\r\rmailto:user@example.com",
    "received": "from mailserver.demo.dmarcanalyzser.com (mailserver.demo.dmarcanalyzser.com\n\r\r[192.0.2.15]) by example.com with ESMTP id M63d4137594e46;\n\r\rMon, 04 Feb 2021 00:00:00 GMT",

 }
```
---
+ `"email"` key should kept as `null` 
+ `"pwd"` key should kept as `null`
---
Now , 

simply fill the relevant metadata by which you 
meet spoofing goal and use the following command:
```shell
$ py spoof2.py
# OR 
$ python3 spoof2.py
```

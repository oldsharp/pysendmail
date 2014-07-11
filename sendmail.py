#!/usr/bin/env python

import os.path
import smtplib

from email import encoders
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

COMMASPACE = ', '

SMTP_HOST = '10.177.9.96'
SMTP_USER = 'username'
SMTP_PASS = 'password'

DATE = formatdate(localtime=True)

FROM = 'Rui.Chen@sandisk.com'

TO = ['oldsharp@163.com', 'oldsharp@gmail.com',]

CC = ['cc1@example.com', 'cc2@example.com',]

BCC = ['bcc1@example.com', 'bcc2@example.com',]

SUBJECT = 'subject'

BODY = '/home/ray/sendmail/mailbody'

ATTACH_FILES = ['/path/to/attach1', '/path/to/attach2']


def sendmail():
    """ """
    msg = MIMEMultipart()

    msg['From'] = FROM

    if TO:
        msg['To'] = COMMASPACE.join(TO)
    if CC:
        msg['Cc'] = COMMASPACE.join(CC)
    if BCC:
        msg['Bcc'] = COMMASPACE.join(BCC)

    msg['Date'] = DATE
    msg['Subject'] = SUBJECT

    fp = open(BODY, 'rb')
    msg.attach(MIMEText(fp.read()))
    fp.close()

    for f in ATTACH_FILES:
        attach_file = MIMEBase('application', 'octet-stream')
        fp = open(f, 'rb')
        attach_file.set_payload(fp.read())
        fp.close()
        encoders.encode_base64(attach_file)
        attach_file.add_header('Content-Disposition', 'attachment',
                               filename=os.path.basename(f))
        msg.attach(attach_file)

    s = smtplib.SMTP(host=SMTP_HOST)
    #s.login(user=SMTP_USER, password=SMTP_PASS)
    s.sendmail(FROM, TO+CC+BCC, msg.as_string())
    s.quit()


if __name__ == '__main__':
    sendmail()

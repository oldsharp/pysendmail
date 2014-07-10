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
SMTP_USER = 'raychen'
SMTP_PASS = 'xxxxxx'

FROM = 'Rui.Chen@sandisk.com'
TO = ['oldsharp@163.com', 'oldsharp@gmail.com']
# TODO: add cc/bcc line ?
DATE = formatdate(localtime=True)

SUBJECT = 'subject'
BODY = '/home/ray/sendmail/mailbody'
ATTACH_FILES = ['/home/ray/sendmail/attach_sample', '/home/ray/sendmail/sendmail.py']


def sendmail():
    """ """
    msg = MIMEMultipart()

    msg['From'] = FROM
    msg['To'] = COMMASPACE.join(TO)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = SUBJECT

    # Open a plain text file for reading.  For this example, assume that
    # the text file contains only ASCII characters.
    fp = open(BODY, 'rb')
    # Add a text/plain message
    msg.attach(MIMEText(fp.read()))
    fp.close()

    msg.attach(MIMEText(BODY))

    for f in ATTACH_FILES:
        part = MIMEBase('application', 'octet-stream')
        fp = open(f, 'rb')
        part.set_payload(fp.read())
        fp.close()
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment',
                        filename=os.path.basename(f))
        msg.attach(part)

    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP(host=SMTP_HOST)
    #s.login(user='raychen', password='xxx')
    s.sendmail(FROM, TO, msg.as_string())
    s.quit()


if __name__ == '__main__':
    sendmail()

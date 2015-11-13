#!/usr/bin/python2
# -*- coding: utf-8 -*-
#
# Author: Ray Chen <oldsharp@gmail.com>
#
# This program has been placed in the public domain.


"""Send the contents specified by command-line args as a MIME message."""


import argparse
import codecs
import os.path
import smtplib
from email import encoders
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate


COMMASPACE = ", "


def check_non_ascii(raw):
    """Return True if contain non-ascii char."""
    chars = raw.decode(encoding="utf-8") if isinstance(raw, str) else raw
    return not all(ord(ch) < 128 for ch in chars)


def parse():
    """Parse args specified by command-line."""
    parser = argparse.ArgumentParser(
        description=(
            "Send the contents specified by "
            "command-line args as a MIME message."))

    parser.add_argument("-H", "--host", type=str, action="store",
                        metavar="HOST", required=True,
                        help="""SMTP server hostname or IP address.
                        Required.""")
    parser.add_argument("-P", "--port", type=int, action="store",
                        metavar="PORT", default=25,
                        help="""SMTP server host port number.
                        Default to 25.""")
    parser.add_argument("-A", "--auth", action="store_true",
                        help="""If this arg is set, sendmail.py will try to
                        login remote SMTP server using username and password
                        given by -u and -p.""")
    parser.add_argument("-S", "--starttls", action="store_true",
                        help="""If this arg is set, will put the SMTP
                        connection in TLS (Transport Layer Security) mode.""")
    parser.add_argument("-u", "--username", type=str, action="store",
                        metavar="USERNAME", default="anonymous",
                        help="""Specify username to login SMTP server.
                        Note this arg only take affect with -A is set.
                        Default to "anonymous".""")
    parser.add_argument("-p", "--password", type=str, action="store",
                        metavar="PASSWORD", default="",
                        help="""Specify password to login SMTP server.
                        Note this arg only take affect with -A is set.
                        Default to empty string.""")
    parser.add_argument("-f", "--from", type=str, action="store",
                        metavar="SENDER", required=True, dest="sender",
                        help="""The value of the From: header. Required.""")
    parser.add_argument("-t", "--to", type=str, action="append",
                        metavar="RECIPIENT", default=[], dest="recipients",
                        help="""A To: header value. Could be specified
                        multiple times.""")
    parser.add_argument("-c", "--cc", type=str, action="append",
                        metavar="CC_RECIPIENT", default=[],
                        dest="cc_recipients",
                        help="""Carbon Copy recipient. Could be specified
                        multiple times.""")
    parser.add_argument("-b", "--bcc", type=str, action="append",
                        metavar="BCC_RECIPIENT", default=[],
                        dest="bcc_recipients",
                        help="""Blind Carbon Copy recipient. Could be specified
                        multiple times.""")
    parser.add_argument("-s", "--subject", type=str, action="store",
                        metavar="SUBJECT", default="",
                        help="""The value of the Subject: header.""")
    parser.add_argument("-M", "--mailbody", type=str, action="store",
                        metavar="MAILBODY", default=None,
                        help="""Mail contents in plain text.""")
    parser.add_argument("-F", "--mailfile", type=str, action="store",
                        metavar="MAILFILE", default="",
                        help="""Mail contents will read from given file path.
                        Note this only take affect when -M is not set.""")
    parser.add_argument("-E", "--encoding", type=str, action="store",
                        metavar="ENCODING", default="utf-8",
                        help="""Mail file encoding.  Default to utf-8.""")
    parser.add_argument("-a", "--attach", type=str, action="append",
                        metavar="ATTACHMENT", default=[], dest="attachs",
                        help="""Attachment file path. Could be specified
                        multiple times.""")

    return parser.parse_args()


def sendmail(args):
    """Assemble MIME message and send to SMTP server."""
    if not args.attachs:
        if args.mailbody is not None:
            if check_non_ascii(args.mailbody):
                msg = MIMEText(args.mailbody, "plain", "utf-8")
            else:
                msg = MIMEText(args.mailbody, "plain", "us-ascii")
        else:
            with codecs.open(args.mailfile, "r", encoding=args.encoding) as fp:
                # FIXME: load all context into mem is not a good idea
                mailbody = fp.read()
                if check_non_ascii(mailbody):
                    msg = MIMEText(mailbody, "plain", "utf-8")
                else:
                    msg = MIMEText(mailbody, "plain", "us-ascii")
    else:
        msg = MIMEMultipart()
        if args.mailbody is not None:
            if check_non_ascii(args.mailbody):
                msg.attach(MIMEText(args.mailbody, "plain", "utf-8"))
            else:
                msg.attach(MIMEText(args.mailbody, "plain", "us-ascii"))
        else:
            with codecs.open(args.mailfile, "r", encoding=args.encoding) as fp:
                mailbody = fp.read()
                if check_non_ascii(mailbody):
                    msg.attach(MIMEText(mailbody, "plain", "utf-8"))
                else:
                    msg.attach(MIMEText(mailbody, "plain", "us-ascii"))

    # Take care of mail header:
    msg["From"] = args.sender
    if args.recipients:
        msg["To"] = COMMASPACE.join(args.recipients)
    if args.cc_recipients:
        msg["Cc"] = COMMASPACE.join(args.cc_recipients)
    # No need to add "Bcc" header here.
    msg["Date"] = formatdate(localtime=True)
    if check_non_ascii(args.subject):
        msg["Subject"] = Header(args.subject, "utf-8")
    else:
        msg["Subject"] = args.subject

    # Add attachments:
    for f in args.attachs:
        attach_file = MIMEBase("application", "octet-stream")
        with open(f, "rb") as fp:
            attach_file.set_payload(fp.read())
        encoders.encode_base64(attach_file)
        # (CHARSET, LANGUAGE, VALUE)
        # FIXME: By setting filename tuple, gmail can not repr
        # Non-ASCII attach filename.
        filename = os.path.basename(f)
        if check_non_ascii(filename):
            filename_tuple = ("utf-8", None, os.path.basename(f))
            attach_file.add_header("Content-Disposition", "attachment",
                                   filename=filename_tuple)
        else:
            attach_file.add_header("Content-Disposition", "attachment",
                                   filename=filename)
        msg.attach(attach_file)

    # Send mail via smtp:
    s = smtplib.SMTP(host=args.host, port=args.port)
    if args.auth:
        if args.starttls:
            s.ehlo()
            s.starttls()
            s.ehlo()
        s.login(user=args.username, password=args.password)
    s.sendmail(args.sender,
               args.recipients+args.cc_recipients+args.bcc_recipients,
               msg.as_string())
    s.quit()


if __name__ == "__main__":
    args = parse()
    sendmail(args)

#!/usr/bin/env python
"""Time-based One-time Password Tool

CLI tool that generates rfc6238 TOTPs, using the native system keyring service
to store secret keys for accounts protected by two-factor authentication.

requires:
  https://pypi.org/project/onetimepass/
  https://pypi.org/project/keyring/
  https://pypi.org/project/pyperclip/
"""

from argparse import ArgumentParser
import keyring, pyperclip
import onetimepass as otp
import subprocess as sp
import re

# Use try clause to make a prompt fucntion that works with either python 2 or 3
try: prompt = raw_input
except NameError: prompt = input

# Set up argument parser
parser = ArgumentParser(description='Time-based One-time Password Generator')
parser.add_argument('-n', '--new', action='store_true', help='Add a new account rather than generating TOTP.')
parser.add_argument('-d', '--display', action='store_true', help='display token')
parser.add_argument('-c', '--copy', action='store_true', help='copy token')
parser.add_argument('-s', '--service', type=str, default='otp_secret', help='Keyring item name. (Default: otp_secret)')
parser.add_argument('-a', '--account', type=str, default='jumpcloud', help='Account to generate TOTP for. (Default: jumpcloud)')
parser.add_argument('-r', '--role', type=str, help='Account to generate TOTP for.')
parser.add_argument('-l', '--login', action='store_true', help='Login to saml2aws using saved credentials')
parser.add_argument('-u', '--username', type=str, help='saml2aws username')
parser.add_argument('-p', '--password', type=str, help='saml2aws password')
parser.add_argument('-f', '--force', action='store_true', help='Force login')
parser.add_argument('-t', '--test', action='store_true', help='Test commend')
parser.add_argument('--prompt', action='store_true', help='Prompt for username')

args = parser.parse_args()

secret = keyring.get_password(args.service, args.account)

add_secret = False
skip_run = False

if not secret:
    skip_run = True
    q = "Account {0} does not exist in service {1}. Would you like to create one? (Y/N) ".format(args.account, args.service)
    a = prompt(q)
    if a and a[0].lower() != 'y': add_secret = False
    else:
        print('adding new scret.')
        add_secret = True
else:
    if args.new:
        skip_run = True
        q = "Account {0} already has a shared secret. Overwrite? (Y/N) ".format(args.account)
        a = prompt(q)
        if a and a[0].lower() != 'y': add_secret = False
        else:
            print("Overwriting shared secret for account {0}.".format(args.account))
            add_secret = True

if add_secret:
    skip_run = True
    secret = prompt("Enter shared secret key (with or without spaces): ")
    keyring.set_password(args.service, args.account, secret)

if not skip_run:
    token = re.sub(r"\D","",str(otp.get_totp(secret, as_string=True)))
    if args.copy:
    	pyperclip.copy(token)
    if args.login:
        saml2aws = [
            "saml2aws",
            "login",
            "--role="+args.role if args.role else None,
            "--username="+args.username if args.username else None,
            "--password="+args.password if args.password and args.username else None,
            "--force" if args.force else None,
            "--mfa-token="+str(token),
            None if args.prompt else "--skip-prompt"
        ]
        cmd = [a for a in saml2aws if a not in set([None])]
        if (args.test):
            print(cmd)
        else:
            sp.run(cmd)
    if args.display:
    	print(token)

print('Finished.')
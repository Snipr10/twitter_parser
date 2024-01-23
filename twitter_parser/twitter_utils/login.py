import sys
import time

from twitter.constants import RED, RESET, GREEN, BOLD, YELLOW
from twitter.login import init_guest_token, flow_start, flow_instrumentation, flow_username, flow_password, \
    flow_duplication_check
from twitter.util import find_key
from httpx import Client
import imaplib
import email
from email.header import decode_header
import re
import os


def login(email: str, username: str, password: str, proxy_url:str, **kwargs) -> tuple[Client, list]:
    proxies = {"http://": proxy_url, "https://": proxy_url}
    client = Client(
        cookies={
            "email": email,
            "username": username,
            "password": password,
            "guest_token": None,
            "flow_token": None,
        },
        headers={
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'content-type': 'application/json',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
            'x-twitter-active-user': 'yes',
            'x-twitter-client-language': 'en',
        },
        follow_redirects=True, proxies=proxies

    )

    client.protonmail = kwargs.get('protonmail')
    client, errors = execute_login_flow(client)

    if kwargs.get('debug'):
        if not client or client.cookies.get('flow_errors') == 'true':
            print(f'[{RED}error{RESET}] {BOLD}{username}{RESET} login failed')
            errors.append("login failed")
        else:
            print(f'[{GREEN}success{RESET}] {BOLD}{username}{RESET} login success')
            errors.append("login success")
    return client, errors


def update_token(client: Client, key: str, url: str, **kwargs) -> tuple[Client, list]:
    errors = []
    caller_name = sys._getframe(1).f_code.co_name
    try:
        headers = {
            'x-guest-token': client.cookies.get('guest_token', ''),
            'x-csrf-token': client.cookies.get('ct0', ''),
            'x-twitter-auth-type': 'OAuth2Client' if client.cookies.get('auth_token') else '',
        }
        client.headers.update(headers)
        r = client.post(url, **kwargs)
        info = r.json()
        for task in info.get('subtasks', []):
            if task.get('enter_text', {}).get("header", {}).get("primary_text", {}).get("text", "") == 'Check your email':
                print(f"[{YELLOW}warning{RESET}] {' '.join(find_key(task, 'text'))}")
                client.cookies.set('confirm_email', 'true')  # signal that email challenge must be solved

            if task.get('subtask_id') == 'LoginAcid':
                if task['enter_text']['hint_text'].casefold() == 'confirmation code':
                    print(f"[{YELLOW}warning{RESET}] email confirmation code challenge.")
                    client.cookies.set('confirmation_code', 'true')

        client.cookies.set(key, info[key])

    except KeyError as e:
        client.cookies.set('flow_errors', 'true')  # signal that an error occurred somewhere in the flow
        print(f'[{RED}error{RESET}] failed to update token at {BOLD}{caller_name}{RESET}\n{e}')
        errors.append('failed to update token at {BOLD}{caller_name}{RESET}\n{e}')
    return client, errors

def get_email_message(username, password):
    time.sleep(3)
    # account credentials
    # use your email provider's IMAP server, you can look for your provider's IMAP server on Google
    # or check this page: https://www.systoolsgroup.com/imap/
    # for office 365, it's this:
    if "@firstmailler" in username:
        imap_server = "imap.firstmail.ltd"
    elif "@gmx.com" in username:
        imap_server = "imap.gmx.com"
    elif "@rambler"in username:
        imap_server = "imap.rambler.ru"
    elif "maillsk.com" in username:
        imap_server = "imap.firstmail.ltd"
    elif "oonmail.com" in username:
        imap_server = "imap.firstmail.ltd"
    elif "znemail.com" in username:
        imap_server = "imap.firstmail.ltd"
    elif "fmaillerbox" in username:
        imap_server = "imap.firstmail.ltd"
    elif "fmailnex" in username:
        imap_server = "imap.firstmail.ltd"
    elif "fmailler.com" in username:
        imap_server = "imap.firstmail.ltd"
    else:
        imap_server = "imap.firstmail.ltd"

    def clean(text):
        # clean text for creating a folder
        return "".join(c if c.isalnum() else "_" for c in text)

    imap = imaplib.IMAP4_SSL(imap_server)
    # authenticate
    imap.login(username, password)

    status, messages = imap.select("INBOX")
    # number of top emails to fetch
    N = 3
    # total number of emails
    messages = int(messages[0])
    res = ""
    for i in range(messages, messages - N, -1):
        body = []

        # fetch the email message by ID
        try:
            res, msg = imap.fetch(str(i), "(RFC822)")
        except Exception:
            continue
        for response in msg:
            if isinstance(response, tuple):
                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
                # decode the email subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    # if it's a bytes, decode to str
                    subject = subject.decode(encoding)
                # decode email sender
                From, encoding = decode_header(msg.get("From"))[0]
                if isinstance(From, bytes):
                    From = From.decode(encoding)
                print("Subject:", subject)
                print("From:", From)
                # if the email message is multipart
                body.append(subject)
                if msg.is_multipart():
                    # iterate over email parts
                    for part in msg.walk():
                        # extract content type of email
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        try:
                            # get the email body
                            body.append(part.get_payload(decode=True).decode())
                        except:
                            pass
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            # print text/plain emails and skip attachments
                            print(body)
                        elif "attachment" in content_disposition:
                            # download attachment
                            filename = part.get_filename()
                            if filename:
                                folder_name = clean(subject)
                                if not os.path.isdir(folder_name):
                                    # make a folder for this email (named after the subject)
                                    os.mkdir(folder_name)
                                filepath = os.path.join(folder_name, filename)
                                # download attachment and save it
                                open(filepath, "wb").write(part.get_payload(decode=True))
                else:
                    # extract content type of email
                    content_type = msg.get_content_type()
                    # get the email body
                    body.append(msg.get_payload(decode=True).decode())
                    if content_type == "text/plain":
                        # print only text email parts
                        print(body)
                # if content_type == "text/html":
                #     # if it's HTML, create a new HTML file and open it in browser
                #     folder_name = clean(subject)
                #     if not os.path.isdir(folder_name):
                #         # make a folder for this email (named after the subject)
                #         os.mkdir(folder_name)
                #     filename = "index.html"
                    # filepath = os.path.join(folder_name, filename)
                    # write the file
                    # open(filepath, "w").write(body)
                    # open in the default browser
                    # webbrowser.open(filepath)
                print("=" * 100)
        if "Please enter this verification code to get started on Twitter" in str(body) or "Ваш код подтверждения в Твиттере" in str(body):
            res = re.findall(r'\d{6}', str(body))[0]
            break
        elif "We noticed an attempt to log in to" in str(body):
            res = re.findall(r'(?<=code.\\r\\n\\r\\n)(.+?)(?=\\r\\n\\r\\nIf this wasn’)', str(body))[0]
            break
        elif "Ваш код подтверждения в Twitter — " in  str(body) :
            res = re.findall(r'(?<=Ваш код подтверждения в Twitter — )(\w{8})', str(body))[0]
            break
    # close the connection and logout
    try:
        imap.close()
        imap.logout()
    except Exception:
        pass
    return res


def confirm_email(client: Client, m) -> tuple[Client, list]:
    return update_token(client, 'flow_token', 'https://api.twitter.com/1.1/onboarding/task.json', json={
        "flow_token": client.cookies.get('flow_token'),
        "subtask_inputs": [
            {
                "subtask_id": "LoginAcid",
                "enter_text": {
                    "text": m,
                    "link": "next_link"
                }
            }]
    })

def execute_login_flow(client: Client,  **kwargs) -> tuple[Client | None, list]:
    errors = []
    client = init_guest_token(client)
    for fn in [flow_start, flow_instrumentation, flow_username, flow_password, flow_duplication_check]:
        client = fn(client)

    # solve email challenge
    if client.cookies.get('confirm_email') == 'true':
        client, errors = confirm_email_my(client)
    # if client.cookies.get('confirm_email') == 'true':
    #     m = get_email_message(client.protonmail['email'], client.protonmail['password'])
    #     client = confirm_email(client, m)

    # # solve confirmation challenge (Proton Mail only)
    # if client.cookies.get('confirmation_code') == 'true':
    #     if not client.protonmail:
    #         print(f'[{RED}warning{RESET}] Please check your email for a confirmation code'
    #               f' and log in again using the web app. If you wish to automatically solve'
    #               f' email confirmation challenges, add a Proton Mail account in your account settings')
    #         return
    #     time.sleep(10)  # todo: just poll the inbox until it arrives instead of waiting
    #     client = solve_confirmation_challenge(client, *client.protonmail.values())
    if client.cookies.get('confirmation_code') == 'true':
        if not kwargs.get('proton'):
            print(f'[{RED}warning{RESET}] Please check your email for a confirmation code'
                  f' and log in again using the web app. If you wish to automatically solve'
                  f' email confirmation challenges, add a Proton Mail account in your account settings')
            try:
                m = get_email_message(client.protonmail['email'], client.protonmail['password'])
                client, new_errors = confirm_email(client, m)
                time.sleep(3)
                errors.extend(new_errors)
            except Exception as e:
                errors.append(e)
        # client = solve_confirmation_challenge(client, **kwargs)
    return client, errors


def confirm_email_my(client: Client) -> tuple[Client, list]:
    return update_token(client, 'flow_token', 'https://api.twitter.com/1.1/onboarding/task.json', json={
        "flow_token": client.cookies.get('flow_token'),
        "subtask_inputs": [
            {
                "subtask_id": "LoginAcid",
                "enter_text": {
                    "text": client.cookies.get('email'),
                    "link": "next_link"
                }
            }]
    })
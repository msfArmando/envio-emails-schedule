import smtplib
import ssl
from dotenv import load_dotenv
import os

load_dotenv()
APPPASSWORD = os.getenv('APPPASSWORD')

def send(msg, sender_email, debug=False):
    if debug:
        smtp_server = "localhost"
        port = 8025
        with smtplib.SMTP(smtp_server, port) as server:
            server.send_message(msg)
    else:
        smtp_server = "smtp.gmail.com"
        port = 465

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(
            smtp_server, port, context=context
        ) as server:
            server.login(sender_email, APPPASSWORD)
            server.send_message(msg)
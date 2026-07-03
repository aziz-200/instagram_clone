import code
import re
import threading
from twilio.rest import Client
import phonenumbers
from decouple import config
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from rest_framework.exceptions import ValidationError


email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
phone_pattern = re.compile(r"^\+?[\d\s\-\(\)]{7,15}$")
username_regex = re.compile(r"^[a-zA-Z0-9_.-]+$")

def check_email_or_phone(email_or_phone):
    if re.fullmatch(email_pattern, email_or_phone):
        return "email"
    try:
        phone_number = phonenumbers.parse(email_or_phone)
        if phonenumbers.is_valid_number(phone_number):
            return "phone"
    except phonenumbers.NumberParseException:
        pass
    raise ValidationError({"success": False, "error": "Invalid email or phone number"})


# Email jo'natish qilsmi
class EmailThread(threading.Thread): # asinxron email jo'natish uchun kk
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)
    def run(self):
        self.email.send()


class Email:
    @staticmethod
    def  send_email(data):
        email = EmailMessage(
            subject=data["subject"],
            body=data["body"],
            to=[data["to_email"]],
        )
        if data.get('content_type') == 'html':
            email.content_subtype = "html"
        EmailThread(email).start()
def send_email(email, code):
    html_content = render_to_string(
        'email/authentication/activate_account.html',
        {"code": code}
    )
    Email.send_email(
        {
        "subject": "ro'yxatdan o'tish",
        "to_email": email,
        "body": html_content,
        "content_type": "html",
         "code": code
         })

# SMS XABARNOMA JO'NATISH
def send_phone_code(phone, code):
    account_sid = config("TWILIO_ACCOUNT_SID")
    auth_token = config("TWILIO_AUTH_TOKEN")
    client = Client(account_sid, auth_token)
    client.messages.create(
        body=f"Your code number is {code}",
        from_="instagram_clone",
        to=f'{phone}'
    )
# verification of username

def check_username_type(user_input):
    if re.fullmatch(email_pattern, user_input):
        user_input = "email"
    elif re.fullmatch(phone_pattern, user_input):
        user_input = "phone"
    elif re.fullmatch(username_regex, user_input):
        user_input = "username"
    else:
        raise ValidationError({"success": False, "error": "Invalid username"})
    return user_input
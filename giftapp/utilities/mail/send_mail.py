import re
from django.core.mail import EmailMessage, send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_mail_now (content:dict, context:dict):
    """
    Accept email content as well as context to be passed to the template
    """
    check_headers = checkMailHeaders(content)
    if not check_headers:
        subject = content['subject']
        sender = content['sender']
        recipient = content['recipient']
        message = render_to_string(content['template'], context)
        plain_message = strip_tags(message)
        email = send_mail(subject, message=plain_message, from_email=sender, recipient_list=[recipient],
              fail_silently=False, html_message=message)
        # msg = email.send()
        print(email)
        if email == int(1):
            return ('Mail sent successfully', True)
        else:
            return ('Failed', False)

    return check_headers, False


def checkMail(email):
    regex = '(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-.]+$)' 
    if (re.search(regex, email)):
        return email
    else:
        return False

def checkMailHeaders(header:dict):
    error = []
    for n in header:
        if not header[n]:
            error.append(f'{n} cannot be empty')
        elif n == 'recipient' and not checkMail(header[n]):
            error.append(f'{n} failed validation')
    return error

import requests
import markdown
from data import MAILBOX_KEY
headers = {
    'Authorization': MAILBOX_KEY,
    'Content-Type': 'application/json',
}


def send(subject='Wasssup', text='## Bingo'):
    body = markdown.markdown(text)
    data = '{"personalizations": [{"to": [{"email": "vishstar88@gmail.com"}]}], "from": {\
        "email": "sendeexampexample@example.com"}, "subject": "%s", "content": [{"type": "text/html", "value": "%s"}]}'

    print (requests.post('https://api.sendgrid.com/v3/mail/send',
                        headers=headers, data=data % (subject, body)))


# print (send())

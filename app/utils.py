from flask import current_app
import jwt
import datetime
import time
import smtplib

SMTP_SERVER = current_app.config['SMTP_SERVER']
SMTP_PORT = current_app.config['SMTP_SERVER_PORT']
SMTP_SENDER_EMAIL = current_app.config['SMTP_SENDER_EMAIL']

SMTP_USE_SSL = current_app.config['SMTP_USE_SSL']
SMTP_SENDER_PASSWORD = current_app.config['SMTP_SENDER_PASSWORD']

if SMTP_USE_SSL:
    import ssl
    ssl_context = ssl.create_default_context()


def create_jwt(email: str, timediff: datetime.timedelta) -> str:
    current_datetime = datetime.datetime.utcnow()
    expiry_datetime = current_datetime + timediff
    unix_expiry_datetime = time.mktime(expiry_datetime.timetuple())
    payload = {
        'email': email,
        'exp': unix_expiry_datetime
    }
    encoded_jwt = jwt.encode(
        payload=payload,
        key=current_app.config['JWT_SECRET'],
        algorithm=current_app.config['JWT_ALG'])
    return encoded_jwt


def try_get_user_email(request) -> str:
    jwt_token = request.headers.get('Authorization').split()[1].strip('"')
    jwt_payload = jwt.decode(jwt_token,
                             key=current_app.config['JWT_SECRET'],
                             algorithms=[current_app.config['JWT_ALG']])
    email = jwt_payload['email']
    return email


def send_email(subject: str, body: str, recipient: str):
    # This is the formatting required to make the
    # subject show up in the subject box
    message = f"Subject: {subject}\n\n{body}"

    if SMTP_USE_SSL:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=ssl_context) as server:
            server.login(SMTP_SENDER_EMAIL, SMTP_SENDER_PASSWORD)
            server.sendmail(SMTP_SENDER_EMAIL, recipient, message)
    else:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.sendmail(SMTP_SENDER_EMAIL, recipient, message)


def get_base_address() -> str:
    # TODO: this is wrong
    return "localhost:5000"

from flask import current_app
from . import utils
import smtplib

# In test mode, we don't need
# any email utilities at all
if utils.get_flask_env() != utils.FlaskEnv.TEST:
    SMTP_SERVER = current_app.config['SMTP_SERVER']
    SMTP_PORT = current_app.config['SMTP_SERVER_PORT']
    SMTP_SENDER_EMAIL = current_app.config['SMTP_SENDER_EMAIL']

    SMTP_USE_SSL = current_app.config['SMTP_USE_SSL']
    SMTP_SENDER_PASSWORD = current_app.config['SMTP_SENDER_PASSWORD']

    if SMTP_USE_SSL:
        import ssl
        ssl_context = ssl.create_default_context()

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

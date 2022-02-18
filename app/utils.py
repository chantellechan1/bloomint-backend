from flask import current_app
import jwt


def try_get_user_email(request) -> str:
    jwt_token = request.headers.get('Authorization').split()[1].strip('"')
    jwt_payload = jwt.decode(jwt_token,
                             key=current_app.config['JWT_SECRET'],
                             algorithms=[current_app.config['JWT_ALG']])
    email = jwt_payload['email']
    return email

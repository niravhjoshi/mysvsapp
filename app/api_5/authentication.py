from flask import g, jsonify
from flask.ext.httpauth import HTTPBasicAuth
from ..models import SVSuserReg
from . import api_5
from .errors import unauthorized, forbidden

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(email_or_token, password):
    if email_or_token == '':
        return unauthorized('SVSApp Invalid credentials')

    if password == '':
        g.current_user = SVSuserReg.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    user = SVSuserReg.query.filter_by(emid=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)

@auth.error_handler
def auth_error():
    return unauthorized('SVSApp Invalid credentials')


@api_5.before_request
@auth.login_required
def before_request():
    if not g.current_user.is_anonymous and not g.current_user.confirmed:
        return forbidden('SVSApp Unconfirmed account')

@api_5.route('/token')
def get_token():
    if not g.current_user.confirmed  or g.token_used:
        return unauthorized('SVSApp Invalid credentials')
    return jsonify({'token': g.current_user.generate_auth_token(expiration=3600), 'expiration': 3600})



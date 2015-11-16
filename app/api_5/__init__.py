from flask import Blueprint

api_5 = Blueprint('api_5',__name__)

from . import authentication,camprofile,viewcamcap,errors



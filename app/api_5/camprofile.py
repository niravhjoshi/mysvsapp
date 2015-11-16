from flask import jsonify,request,g,abort,url_for
from .. import db
from ..models import SVSIpCamReg,SVSuserReg,current_app
from . import api_5
from .decorators import permission_required
from .errors import forbidden
from cryptography.fernet import Fernet
from flask.ext.login import login_user, logout_user, login_required,current_user

@api_5.route('/viewmycams')
def get_viewcams():
    page = request.args.get('page', 1, type=int)
    email = SVSuserReg.query.filter_by(emid=g.current_user.emid).first()
    pagination = SVSIpCamReg.query.filter_by( u_id = email.id ).order_by(SVSIpCamReg.camregdate.desc()).paginate(page, per_page=current_app.config['SVS_PAGE_PHOTO'],error_out=False)
    regcams = pagination.items
    for cams in regcams:
        camkey = cams.key
        bcamskey = bytes(camkey)
        camurlhash = cams.camurl_hash
        bcamurlhash = bytes(camurlhash)
        f = Fernet(bcamskey)
        finalurl = f.decrypt(bcamurlhash)
        cams.camurl_hash = finalurl
    prev = None
    if pagination.has_prev:
        prev = url_for('api_5.get_viewcams', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api_5.get_viewcams', page=page+1, _external=True)
    return jsonify({
        'posts': [post.to_json() for post in regcams],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


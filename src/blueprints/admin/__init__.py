from flask import Blueprint

from .data import data
from .user import user

admin = Blueprint("admin", __name__, url_prefix="/admin")

admin.register_blueprint(data)
admin.register_blueprint(user)

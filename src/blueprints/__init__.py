from flask import Blueprint, Response, redirect, url_for

from src.view import View

from .admin import admin
from .api import api
from .auth import auth
from .data import data
from .home import home
from .user import user

root = Blueprint("root", __name__)

root.register_blueprint(admin)
root.register_blueprint(api)
root.register_blueprint(auth)
root.register_blueprint(data)
root.register_blueprint(home)
root.register_blueprint(user)

@root.route("/")
@root.route("/index")
def index() -> View:
    return redirect(url_for("root.home.index"))

@root.route("/sw.js")
def service_worker() -> View:
    return Response(status=204)

from os.path import join

from flask import Blueprint, flash, redirect, render_template, request, url_for

from src.user import UserException, users
from src.view import View, login_required

TEMPLATES_DIR = "user"

user = Blueprint("user", __name__, url_prefix="/user")

@user.route("/settings", methods=["GET", "POST"])
@login_required
def settings() -> View:
    if request.method == "POST":
        try:
            users.change_password(request.form)
        except UserException as error:
            flash(error.message)
        else:
            return redirect(url_for("root.home.index"))

    return render_template(join(TEMPLATES_DIR, "settings.html"))

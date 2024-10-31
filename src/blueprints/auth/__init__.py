from os.path import join

from flask import Blueprint, flash, redirect, render_template, request, url_for

from src.user import UserException, current_user, users
from src.view import View

TEMPLATES_DIR = "auth"

auth = Blueprint("auth", __name__, url_prefix="/auth")

@auth.route("/login", methods=["GET", "POST"])
def login() -> View:
    if current_user:
        users.logout()

    if request.method == "POST":
        try:
            users.login(request.form)
        except UserException as error:
            flash(error.message)
        else:
            return redirect(url_for("root.home.index"))

    return render_template(join(TEMPLATES_DIR, "login.html"))

from os.path import join

from flask import Blueprint, flash, redirect, render_template, request, url_for

from src.user import UserException, current_user, users
from src.view import View, admin_required, confirm_required

TEMPLATES_DIR = join("admin", "user")

user = Blueprint("user", __name__, url_prefix="/user")

@user.route("/")
@admin_required
def view() -> View:
    return render_template(join(TEMPLATES_DIR, "view.html"), headers=users.columns, table=users.values)

@user.route("/add", methods=["GET", "POST"])
@admin_required
def add() -> View:
    if request.method == "POST":
        try:
            users.append(request.form)
        except UserException as error:
            flash(error.message)
        else:
            return redirect(url_for(".view"))

    return render_template(join(TEMPLATES_DIR, "add.html"))

@user.route("/edit/<int:idx>", methods=["GET", "POST"])
@admin_required
def edit(idx: int) -> View:
    if request.method == "POST":
        try:
            users.reset_password(idx, request.form)
        except UserException as error:
            flash(error.message)
        else:
            return redirect(url_for(".view"))

    user = users[idx]
    if user == current_user:
        return redirect(url_for(".view"))

    return render_template(join(TEMPLATES_DIR, "edit.html"), idx=idx)

@user.route("/remove/<int:idx>", methods=["GET", "POST"])
@admin_required
@confirm_required
def remove(idx: int) -> View:
    del users[idx]
    return redirect(url_for(".view"))

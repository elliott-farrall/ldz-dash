from os.path import join

from flask import Blueprint, redirect, render_template, request, url_for

from src.data import Data
from src.view import View, confirm_required, login_required

TEMPLATES_DIR = "data"

data = Blueprint("data", __name__, url_prefix="/data")

@data.route("/<category>/<subcategory>", methods=["GET", "POST"])
@login_required
def add(category: str, subcategory: str) -> View:
    if request.method == "POST":
        with Data(category, subcategory) as data:
            data.append(request.form)
        return redirect(url_for(".add", category=category, subcategory=subcategory))

    return render_template(join(TEMPLATES_DIR, category, subcategory + ".html"), category=category, subcategory=subcategory)

@data.route("/<category>/<subcategory>/edit")
@login_required
def edit(category: str, subcategory: str) -> View:
    with Data(category, subcategory) as data:
        return render_template(join(TEMPLATES_DIR, "edit.html"), category=category, subcategory=subcategory, headers=data.columns, table=data.values)

@data.route("/<category>/<subcategory>/remove/<int:idx>", methods=["GET", "POST"])
@login_required
@confirm_required
def remove(category: str, subcategory: str, idx: int) -> View:
    with Data(category, subcategory) as data:
        del data[idx]
    return redirect(url_for(".edit", category=category, subcategory=subcategory))

from datetime import datetime
from os.path import join

from flask import Blueprint, Response, jsonify, render_template, request
from pandas import concat

from src.data import Data
from src.user import users
from src.view import View, admin_required

TEMPLATES_DIR = join("admin", "data")

data = Blueprint("data", __name__, url_prefix="/data")

@data.route("/", methods=["GET", "POST"])
@admin_required
def download() -> View:
    if request.method == "POST":
        date = datetime.strptime(request.form["month"], "%Y-%m")
        category, subcategory = request.form["category:subcategory"].split(":")
        users = request.form.getlist("users")

        table = concat([Data(category, subcategory, user).table for user in users], ignore_index=True)
        if not table.empty:
            table = table.loc[
                (table["Date"].dt.month == date.month) &
                (table["Date"].dt.year == date.year)
            ]
            table.sort_values("Date", ascending=False, inplace=True)

        return Response(table.to_csv(index=False), mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=data.csv"})

    return render_template(join(TEMPLATES_DIR, "download.html"))

@data.route("/dates/<category>/<subcategory>")
@admin_required
def dates(category: str, subcategory: str) -> View:
    dates = dict.fromkeys(users.table["username"])

    for user in dates:
        with Data(category, subcategory, user) as data:
            if not data.empty:
                dates[user] = data[0]["Date"]

    return jsonify(dates)

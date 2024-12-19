from datetime import datetime
from os.path import join
from tempfile import NamedTemporaryFile

from flask import Blueprint, Response, jsonify, render_template, request, redirect, url_for
from pandas import DataFrame, concat, read_csv

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

        table = DataFrame()
        for user in users:
            with Data(category, subcategory, user) as data:
                if not data.empty:
                    user_table = data.table.loc[
                        (data.table["Date"].dt.month == date.month) &
                        (data.table["Date"].dt.year == date.year)
                    ]
                    user_table.insert(0, "User", user)
                    table = concat([table, user_table], ignore_index=True)

        if not table.empty:
            table.sort_values("Date", ascending=False, inplace=True)

        with NamedTemporaryFile(dir=".", suffix=".csv") as tmp:
            table.to_csv(tmp.name, index=False)
            return Response(tmp.read(), mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=data.csv"})

    return render_template(join(TEMPLATES_DIR, "data.html"))

@data.route("/backup", methods=["POST"])
@admin_required
def backup() -> View:
    if request.method == "POST":
        category, subcategory = request.form["category:subcategory"].split(":")

        match request.form["submit"]:
            case "Backup":
                table = DataFrame()
                for user in users.table["username"]:
                    with Data(category, subcategory, user) as data:
                        if not data.empty:
                            user_table = data.table.copy()
                            user_table.insert(0, "User", user)
                            table = concat([table, user_table], ignore_index=True)

                with NamedTemporaryFile(dir=".", suffix=".csv") as tmp:
                    table.to_csv(tmp.name, index=False)
                    return Response(tmp.read(), mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=backup.csv"})
            case "Restore":
                file = request.files["data"]
                with NamedTemporaryFile(dir=".", suffix=".csv") as tmp:
                    file.save(tmp.name)
                    table = read_csv(tmp.name)

                for user in table["User"].unique():
                    user_table = table[table["User"] == user].drop(columns=["User"])
                    data = Data(category, subcategory, user)
                    data._table = user_table
                    data._table.to_csv(data.path, index=False)

    return redirect(url_for(".download"))

@data.route("/dates/<category>/<subcategory>")
@admin_required
def dates(category: str, subcategory: str) -> View:
    dates = dict.fromkeys(users.table["username"])

    for user in dates:
        with Data(category, subcategory, user) as data:
            if not data.empty:
                dates[user] = data[0]["Date"]

    return jsonify(dates)

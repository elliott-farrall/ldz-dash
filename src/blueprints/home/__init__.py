from calendar import month_abbr
from os.path import join

from flask import Blueprint, jsonify, render_template

from src.data import Data
from src.user import users
from src.view import View, login_required

TEMPLATES_DIR = "home"

home = Blueprint("home", __name__, url_prefix="/home")

@home.route("/")
@login_required
def index() -> View:
    return render_template(join(TEMPLATES_DIR, "index.html"))

@home.route("/charts/<category>/<subcategory>/<int:year>")
@login_required
def charts(category: str, subcategory: str, year: int) -> View:
    chart_data = dict.fromkeys(month_abbr[1:], 0)

    for user in users:
        with Data(category, subcategory, username=user.username) as data:
            if data.empty:
                continue
            table_year = data.table[data.table["Date"].dt.year == year]

            for month in chart_data:
                month_table = table_year.loc[table_year["Date"].dt.strftime("%b") == month]
                if category == "embedded":
                    chart_data[month] += int(month_table["Students Arrived"].sum())
                elif category == "regular":
                    chart_data[month] += int(month_table.loc[~month_table["Attendance"].isin(["No Show", "Cancelled"]), "Students"].sum())

    trace = {
        "x": list(chart_data.keys()),
        "y": list(chart_data.values()),
        "type": "scatter",
        "mode": "lines+markers",
    }
    layout = {
        "paper_bgcolor": "transparent",
        "plot_bgcolor": "transparent",
        "showlegend": False,
        "autosize": True,
        "margin": {"l": 10, "r": 10, "t": 40, "b": 40},
        "title": f"{category.capitalize()} - {subcategory.upper()}",
        "xaxis": {
            "tickmode": "linear",
            "tick0": 0,
            "dtick": 1,
        },
        "yaxis": {
            "title": "# Students",
            "range": [0, "auto"],
            "rangemode": "tozero",
            "tickmode": "linear",
            "tick0": 0,
            "dtick": 1,
        },
    }

    return jsonify({"data": [trace], "layout": layout})

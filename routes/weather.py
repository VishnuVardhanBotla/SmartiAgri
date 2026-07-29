from flask import Blueprint, render_template

from routes.auth import login_required

weather_bp = Blueprint("weather", __name__, url_prefix="/weather")


@weather_bp.route("/")
@login_required()
def weather_page():
    return render_template("weather.html")

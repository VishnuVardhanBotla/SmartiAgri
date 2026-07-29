from flask import Flask, flash, redirect, render_template, request, session, url_for

from config import get_db_connection
from database import ensure_database_exists, initialize_database
from language import SUPPORTED_LANGUAGES, get_language, get_language_info, get_language_options, set_language, translate
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.buyer import buyer_bp
from routes.community import community_bp
from routes.farmer import farmer_bp
from routes.machinery import machinery_bp
from routes.market import market_bp
from routes.provider import provider_bp
from routes.schemes import schemes_bp
from routes.technology import technology_bp
from routes.weather import weather_bp
from routes.ai import ai_bp

app = Flask(__name__)
app.config.from_object("config.Config")


@app.before_request
def initialize_app_database():
    ensure_database_exists()
    connection = get_db_connection()
    initialize_database(connection)
    connection.close()


@app.before_request
def apply_language():
    get_language()


@app.context_processor
def inject_language_context():
    current = get_language()
    return {
        "t": translate,
        "current_language": get_language_info(current),
        "language_options": get_language_options(),
    }

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(buyer_bp)
app.register_blueprint(community_bp)
app.register_blueprint(farmer_bp)
app.register_blueprint(machinery_bp)
app.register_blueprint(market_bp)
app.register_blueprint(provider_bp)
app.register_blueprint(schemes_bp)
app.register_blueprint(technology_bp)
app.register_blueprint(weather_bp)
app.register_blueprint(ai_bp)


@app.route("/")
def index():
    if "user_id" in session:
        role = session.get("role")
        if role == "farmer":
            return redirect(url_for("farmer.dashboard"))
        if role == "provider":
            return redirect(url_for("provider.dashboard"))
        if role == "buyer":
            return redirect(url_for("buyer.dashboard"))
        if role == "admin":
            return redirect(url_for("admin.dashboard"))
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register_redirect():
    return redirect(url_for("auth.register"))


@app.route("/set-language/<language>")
def set_language_route(language):
    if language not in SUPPORTED_LANGUAGES:
        language = "en"
    set_language(language)
    next_url = request.args.get("next") or url_for("index")
    response = redirect(next_url)
    response.set_cookie("language", language, max_age=60 * 60 * 24 * 365)
    return response


@app.errorhandler(404)
def not_found(_error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(_error):
    return render_template("errors/500.html"), 500


if __name__ == "__main__":
    app.run(debug=True)

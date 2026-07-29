from flask import Blueprint, render_template, session

from config import get_db_connection
from routes.auth import login_required

provider_bp = Blueprint("provider", __name__, url_prefix="/provider")


@provider_bp.route("/dashboard")
@login_required(role="provider")
def dashboard():
    conn = get_db_connection()
    machinery_count = conn.execute("SELECT COUNT(*) AS total_machinery FROM machinery WHERE provider_id=%s", (session.get("user_id"),)).fetchone()
    conn.close()
    return render_template("provider/dashboard.html", machinery_count=machinery_count["total_machinery"])

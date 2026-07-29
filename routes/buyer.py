from flask import Blueprint, render_template, session

from config import get_db_connection
from routes.auth import login_required

buyer_bp = Blueprint("buyer", __name__, url_prefix="/buyer")


@buyer_bp.route("/dashboard")
@login_required(role="buyer")
def dashboard():
    conn = get_db_connection()
    requirements_count = conn.execute("SELECT COUNT(*) AS total_requirements FROM buyer_requirements WHERE buyer_id=%s", (session.get("user_id"),)).fetchone()
    conn.close()
    return render_template("buyer/dashboard.html", requirements_count=requirements_count["total_requirements"])

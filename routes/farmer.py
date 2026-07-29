from flask import Blueprint, render_template, session

from config import get_db_connection
from routes.auth import login_required

farmer_bp = Blueprint("farmer", __name__, url_prefix="/farmer")


@farmer_bp.route("/dashboard")
@login_required(role="farmer")
def dashboard():
    conn = get_db_connection()
    post_count = conn.execute("SELECT COUNT(*) AS total_posts FROM community_posts").fetchone()
    prices = conn.execute("SELECT * FROM market_prices ORDER BY price_date DESC LIMIT 3").fetchall()
    schemes = conn.execute("SELECT * FROM government_schemes ORDER BY start_date DESC LIMIT 3").fetchall()
    notifications = conn.execute("SELECT * FROM notifications WHERE user_id=%s ORDER BY created_at DESC LIMIT 5", (session["user_id"],)).fetchall()
    conn.close()

    return render_template(
        "farmer/dashboard.html",
        post_count=post_count["total_posts"],
        prices=prices,
        schemes=schemes,
        notifications=notifications,
    )

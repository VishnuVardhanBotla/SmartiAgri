from flask import Blueprint, render_template

from config import get_db_connection
from routes.auth import login_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/dashboard")
@login_required(role="admin")
def dashboard():
    conn = get_db_connection()
    stats = conn.execute(
        "SELECT (SELECT COUNT(*) FROM users WHERE role='farmer') AS total_farmers, (SELECT COUNT(*) FROM users WHERE role='provider') AS total_providers, (SELECT COUNT(*) FROM users WHERE role='buyer') AS total_buyers, (SELECT COUNT(*) FROM machinery) AS total_machinery, (SELECT COUNT(*) FROM technologies) AS total_technologies, (SELECT COUNT(*) FROM community_posts) AS total_posts, (SELECT COUNT(*) FROM advertisements) AS total_ads"
    ).fetchone()
    conn.close()
    return render_template("admin/dashboard.html", stats=stats)

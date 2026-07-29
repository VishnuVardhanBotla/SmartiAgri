from flask import Blueprint, render_template, request

from config import get_db_connection
from routes.auth import login_required

market_bp = Blueprint("market", __name__, url_prefix="/market")


@market_bp.route("/prices")
@login_required()
def prices():
    conn = get_db_connection()
    query = "SELECT * FROM market_prices"
    filters = []
    if request.args.get("crop"):
        query += " WHERE crop_name LIKE %s"
        filters.append(f"%{request.args.get('crop')}%")
    if request.args.get("district"):
        query += " AND district LIKE %s" if "WHERE" in query else " WHERE district LIKE %s"
        filters.append(f"%{request.args.get('district')}%")
    query += " ORDER BY price_date DESC"
    prices = conn.execute(query, filters).fetchall()
    conn.close()
    return render_template("market/prices.html", prices=prices)

from flask import Blueprint, render_template, request

from config import get_db_connection
from routes.auth import login_required

schemes_bp = Blueprint("schemes", __name__, url_prefix="/schemes")


@schemes_bp.route("/")
@login_required()
def list_schemes():
    conn = get_db_connection()
    query = "SELECT * FROM government_schemes"
    filters = []
    if request.args.get("search"):
        query += " WHERE scheme_name LIKE %s OR description LIKE %s"
        search_term = f"%{request.args.get('search')}%"
        filters.extend([search_term, search_term])
    query += " ORDER BY scheme_name"
    schemes = conn.execute(query, filters).fetchall()
    conn.close()
    return render_template("schemes/list.html", schemes=schemes)

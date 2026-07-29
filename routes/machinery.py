from flask import Blueprint, render_template, request

from config import get_db_connection
from routes.auth import login_required

machinery_bp = Blueprint("machinery", __name__, url_prefix="/machinery")


@machinery_bp.route("/")
@login_required()
def list_machinery():
    conn = get_db_connection()
    query = "SELECT m.*, u.full_name AS provider_name FROM machinery m JOIN users u ON m.provider_id=u.id"
    filters = []
    if request.args.get("category"):
        query += " WHERE m.category=%s"
        filters.append(request.args.get("category"))
    if request.args.get("location"):
        query += " AND m.location LIKE %s" if "WHERE" in query else " WHERE m.location LIKE %s"
        filters.append(f"%{request.args.get('location')}%")
    query += " ORDER BY m.name"
    machinery = conn.execute(query, filters).fetchall()
    conn.close()
    return render_template("machinery/list.html", machinery=machinery)


@machinery_bp.route("/<int:machinery_id>")
@login_required()
def details(machinery_id):
    conn = get_db_connection()
    machinery = conn.execute("SELECT m.*, u.full_name AS provider_name FROM machinery m JOIN users u ON m.provider_id=u.id WHERE m.id=%s", (machinery_id,)).fetchone()
    conn.close()
    return render_template("machinery/details.html", machinery=machinery)

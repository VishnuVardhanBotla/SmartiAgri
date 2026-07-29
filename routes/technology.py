from flask import Blueprint, render_template, request

from config import get_db_connection
from routes.auth import login_required

technology_bp = Blueprint("technology", __name__, url_prefix="/technologies")


@technology_bp.route("/")
@login_required()
def list_technologies():
    conn = get_db_connection()
    query = "SELECT * FROM technologies"
    filters = []
    if request.args.get("category"):
        query += " WHERE category=%s"
        filters.append(request.args.get("category"))
    query += " ORDER BY name"
    technologies = conn.execute(query, filters).fetchall()
    conn.close()
    return render_template("technology/list.html", technologies=technologies)


@technology_bp.route("/<int:tech_id>")
@login_required()
def details(tech_id):
    conn = get_db_connection()
    technology = conn.execute("SELECT * FROM technologies WHERE id=%s", (tech_id,)).fetchone()
    conn.close()
    return render_template("technology/details.html", technology=technology)

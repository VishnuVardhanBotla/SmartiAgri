from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from config import get_db_connection
from routes.auth import login_required

community_bp = Blueprint("community", __name__, url_prefix="/community")


@community_bp.route("/")
@login_required()
def feed():
    conn = get_db_connection()
    posts = conn.execute("SELECT cp.*, u.full_name FROM community_posts cp JOIN users u ON cp.user_id=u.id ORDER BY cp.created_at DESC").fetchall()
    conn.close()
    return render_template("community/feed.html", posts=posts)


@community_bp.route("/create", methods=["POST"])
@login_required()
def create_post():
    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()
    conn = get_db_connection()
    conn.execute("INSERT INTO community_posts (user_id, title, content) VALUES (%s, %s, %s)", (session["user_id"], title, content))
    conn.commit()
    conn.close()
    flash("Post created.", "success")
    return redirect(url_for("community.feed"))


@community_bp.route("/<int:post_id>/comment", methods=["POST"])
@login_required()
def add_comment(post_id):
    comment_text = request.form.get("comment_text", "").strip()
    conn = get_db_connection()
    conn.execute("INSERT INTO community_comments (post_id, user_id, comment_text) VALUES (%s, %s, %s)", (post_id, session["user_id"], comment_text))
    conn.commit()
    conn.close()
    flash("Comment added.", "success")
    return redirect(url_for("community.feed"))

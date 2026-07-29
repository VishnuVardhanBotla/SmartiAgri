import re

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import generate_password_hash

from config import get_db_connection
from database import password_matches
from language import translate
from models import generate_user_id, initialize_database

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def login_required(role=None):
    def decorator(view_func):
        def wrapped(*args, **kwargs):
            if "user_id" not in session:
                flash(translate("messages.login_required"), "warning")
                return redirect(url_for("auth.login"))
            if role and session.get("role") != role:
                flash(translate("messages.access_denied"), "danger")
                return redirect(url_for("auth.login"))
            return view_func(*args, **kwargs)

        wrapped.__name__ = view_func.__name__
        return wrapped

    return decorator


def _is_valid_email(value):
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value))


def _is_strong_password(value):
    return len(value) >= 8 and re.search(r"[A-Z]", value) and re.search(r"\d", value)


def _is_valid_phone(value):
    return bool(re.fullmatch(r"\d{10}", value))


def _is_valid_pin(value):
    return bool(re.fullmatch(r"\d{6}", value))


def _is_valid_url(value):
    return bool(re.match(r"^https?://.+", value))


def _is_valid_gst(value):
    return not value or bool(re.fullmatch(r"[0-9A-Z]{2}[A-Z0-9]{10,}", value))


def _get_stored_password(user):
    if not user:
        return None
    return user.get("password")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    conn = get_db_connection()
    initialize_database(conn)
    if request.method == "POST":
        role = request.form.get("role", "").strip().lower()
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        alternate_phone = request.form.get("alternate_phone", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        house_no = request.form.get("house_no", "").strip()
        street = request.form.get("street", "").strip()
        village = request.form.get("village", "").strip()
        mandal = request.form.get("mandal", "").strip()
        district = request.form.get("district", "").strip()
        state = request.form.get("state", "").strip()
        pin_code = request.form.get("pin_code", "").strip()
        country = request.form.get("country", "India").strip() or "India"

        if role not in {"farmer", "provider", "buyer"}:
            flash(translate("messages.role_invalid"), "danger")
            return render_template("auth/register.html", role=role)
        if not all([full_name, email, phone, password, confirm_password]):
            flash(translate("messages.required"), "danger")
            return render_template("auth/register.html", role=role)
        if not _is_valid_email(email):
            flash(translate("messages.invalid_email"), "danger")
            return render_template("auth/register.html", role=role)
        if not _is_valid_phone(phone):
            flash(translate("messages.invalid_phone"), "danger")
            return render_template("auth/register.html", role=role)
        if password != confirm_password:
            flash(translate("messages.password_mismatch"), "danger")
            return render_template("auth/register.html", role=role)
        if not _is_strong_password(password):
            flash(translate("messages.weak_password"), "danger")
            return render_template("auth/register.html", role=role)
        if pin_code and not _is_valid_pin(pin_code):
            flash(translate("messages.pin_invalid"), "danger")
            return render_template("auth/register.html", role=role)

        existing = conn.execute("SELECT id FROM users WHERE email=%s OR phone=%s", (email, phone)).fetchone()
        if existing:
            flash(translate("messages.account_exists"), "warning")
            return render_template("auth/register.html", role=role)

        user_id = generate_user_id(role, conn)
        hashed_password = generate_password_hash(password)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (user_id, role, full_name, email, phone, alternate_phone, password, house_no, street, village, mandal, district, state, pin_code, country) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (user_id, role, full_name, email, phone, alternate_phone or None, hashed_password, house_no, street, village, mandal, district, state, pin_code, country),
        )
        user_row_id = cursor.lastrowid

        if role == "farmer":
            farm_name = request.form.get("farm_name", "").strip()
            land_acres = request.form.get("land_acres", "").strip()
            main_crops = request.form.get("main_crops", "").strip()
            farming_type = request.form.get("farming_type", "").strip()
            irrigation_type = request.form.get("irrigation_type", "").strip()
            preferred_language = request.form.get("preferred_language", "").strip()
            if not all([farm_name, land_acres, main_crops, farming_type, irrigation_type, preferred_language]):
                conn.close()
                flash(translate("messages.farmer_details"), "danger")
                return render_template("auth/register.html", role=role)
            conn.execute(
                "INSERT INTO farmers (user_id, farm_name, land_acres, main_crops, farming_type, irrigation_type, preferred_language) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (user_row_id, farm_name, land_acres, main_crops, farming_type, irrigation_type, preferred_language),
            )
        elif role == "provider":
            business_name = request.form.get("business_name", "").strip()
            owner_name = request.form.get("owner_name", "").strip()
            machinery_category = request.form.get("machinery_category", "").strip()
            service_category = request.form.get("service_category", "").strip()
            equipment = request.form.get("equipment", "").strip()
            rental_available = request.form.get("rental_available", "").strip()
            service_area = request.form.get("service_area", "").strip()
            gst_number = request.form.get("gst_number", "").strip()
            website = request.form.get("website", "").strip()
            if not all([business_name, owner_name, machinery_category, service_category, equipment, rental_available, service_area]):
                conn.close()
                flash(translate("messages.provider_details"), "danger")
                return render_template("auth/register.html", role=role)
            if not _is_valid_gst(gst_number):
                conn.close()
                flash("Please enter a valid GST number.", "danger")
                return render_template("auth/register.html", role=role)
            if website and not _is_valid_url(website):
                conn.close()
                flash("Please enter a valid website URL.", "danger")
                return render_template("auth/register.html", role=role)
            conn.execute(
                "INSERT INTO providers (user_id, business_name, owner_name, machinery_category, service_category, equipment, rental_available, service_area, gst_number, website) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (user_row_id, business_name, owner_name, machinery_category, service_category, equipment, rental_available, service_area, gst_number, website),
            )
        else:
            company_name = request.form.get("company_name", "").strip()
            contact_person = request.form.get("contact_person", "").strip()
            business_type = request.form.get("business_type", "").strip()
            interested_crops = request.form.get("interested_crops", "").strip()
            buying_locations = request.form.get("buying_locations", "").strip()
            daily_buying_capacity = request.form.get("daily_buying_capacity", "").strip()
            gst_number = request.form.get("gst_number", "").strip()
            website = request.form.get("website", "").strip()
            if not all([company_name, contact_person, business_type, interested_crops, buying_locations, daily_buying_capacity]):
                conn.close()
                flash(translate("messages.buyer_details"), "danger")
                return render_template("auth/register.html", role=role)
            if not _is_valid_gst(gst_number):
                conn.close()
                flash("Please enter a valid GST number.", "danger")
                return render_template("auth/register.html", role=role)
            if website and not _is_valid_url(website):
                conn.close()
                flash("Please enter a valid website URL.", "danger")
                return render_template("auth/register.html", role=role)
            conn.execute(
                "INSERT INTO buyers (user_id, company_name, contact_person, business_type, interested_crops, buying_locations, daily_buying_capacity, gst_number, website) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (user_row_id, company_name, contact_person, business_type, interested_crops, buying_locations, daily_buying_capacity, gst_number, website),
            )

        conn.commit()
        conn.close()
        flash(translate("messages.registration_success"), "success")
        return redirect(url_for("auth.login"))

    conn.close()
    return render_template("auth/register.html", role="")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_input = request.form.get("login_input", "").strip()
        password = request.form.get("password", "")

        conn = get_db_connection()
        initialize_database(conn)
        user = conn.execute("SELECT * FROM users WHERE email=%s OR phone=%s OR user_id=%s", (login_input, login_input, login_input)).fetchone()
        conn.close()

        stored_password = _get_stored_password(user)
        if user and stored_password and password_matches(stored_password, password):
            session.clear()
            session["user_id"] = user["id"]
            session["role"] = user["role"]
            session["full_name"] = user["full_name"]
            flash(translate("messages.login_success"), "success")
            if user["role"] == "farmer":
                return redirect(url_for("farmer.dashboard"))
            if user["role"] == "provider":
                return redirect(url_for("provider.dashboard"))
            if user["role"] == "buyer":
                return redirect(url_for("buyer.dashboard"))
            if user["role"] == "admin":
                return redirect(url_for("admin.dashboard"))
        flash(translate("messages.invalid_login"), "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash(translate("messages.logged_out"), "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/forgot-password")
def forgot_password():
    flash(translate("messages.forgot_password"), "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/profile")
@login_required()
def profile():
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id=%s", (session["user_id"],)).fetchone()
    conn.close()
    return render_template("auth/profile.html", user=user)


@auth_bp.route("/change-password", methods=["GET", "POST"])
@login_required()
def change_password():
    if request.method == "POST":
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        conn = get_db_connection()
        row = conn.execute("SELECT password FROM users WHERE id=%s", (session["user_id"],)).fetchone()
        if row and password_matches(row["password"], current_password):
            conn.execute("UPDATE users SET password=%s WHERE id=%s", (generate_password_hash(new_password), session["user_id"]))
            conn.commit()
            flash(translate("messages.password_changed"), "success")
        else:
            flash(translate("messages.incorrect_password"), "danger")
        conn.close()
        return redirect(url_for("auth.profile"))
    return render_template("auth/change_password.html")

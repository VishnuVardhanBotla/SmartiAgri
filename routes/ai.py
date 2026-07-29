from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from config import get_db_connection
from routes.auth import login_required

ai_bp = Blueprint("ai", __name__, url_prefix="/ai")


@ai_bp.route("/recommendation", methods=["GET", "POST"])
@login_required()
def recommendation():
    if request.method == "POST":
        crop = request.form.get("crop", "")
        farm_size = request.form.get("farm_size", "")
        soil_type = request.form.get("soil_type", "")
        water_availability = request.form.get("water_availability", "")
        budget = request.form.get("budget", "")
        location = request.form.get("location", "")
        season = request.form.get("season", "")

        recommendation_text = (
            f"For {crop} on a {farm_size} farm with {soil_type} soil, using {water_availability} water and a budget of {budget}, "
            f"the best approach in {location} during {season} is to adopt precision irrigation, use a soil sensor, and plan for drip irrigation."
        )

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO ai_recommendations (user_id, crop, farm_size, soil_type, water_availability, budget, location, season, recommendation_text) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (session["user_id"], crop, farm_size, soil_type, water_availability, budget, location, season, recommendation_text),
        )
        cursor.close()
        conn.close()
        flash("Recommendation generated.", "success")
        return redirect(url_for("ai.recommendation"))

    return render_template("ai/recommendation.html")


@ai_bp.route("/diagnosis", methods=["GET", "POST"])
@login_required()
def diagnosis():
    result = None
    if request.method == "POST":
        crop_name = request.form.get("crop_name", "")
        symptoms = request.form.get("symptoms", "")
        problem_description = request.form.get("problem_description", "")
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM crop_diseases WHERE crop_name=%s", (crop_name,))
        disease = cursor.fetchone()
        cursor.close()
        conn.close()
        if disease:
            result = {
                "disease": disease["disease_name"],
                "causes": disease["causes"],
                "recommended_actions": disease["recommended_actions"],
                "prevention_tips": disease["prevention_tips"],
            }
        else:
            result = {"disease": "No clear match found", "causes": "Please consult an agricultural expert", "recommended_actions": "Inspect the crop closely", "prevention_tips": "Use recommended preventive practices"}
        flash("Diagnosis completed using demo rules.", "info")
    return render_template("ai/diagnosis.html", result=result)

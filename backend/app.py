from flask import Flask, render_template, request
from models import init_db, update_medical_record

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Initialize Database
init_db()

# Import Blueprints
from register import register_bp
from auth import auth_bp
from emergency import emergency_bp

# Register Blueprints
app.register_blueprint(register_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(emergency_bp)

# ---------------- HOME PAGE ----------------
@app.route("/")
def home():
    return render_template("index.html")

# ---------------- UPDATE MEDICAL RECORDS ----------------
@app.route("/update", methods=["GET", "POST"])
def update_records():
    if request.method == "GET":
        return render_template("update.html")

    citizen_id = request.form.get("citizen_id")
    treatment = request.form.get("treatment")
    new_conditions = request.form.get("new_conditions")

    if not citizen_id or not treatment:
        return render_template(
            "update.html",
            error="User ID and Treatment details are required"
        )

    success = update_medical_record(citizen_id, treatment, new_conditions)

    if not success:
        return render_template(
            "update.html",
            error="Invalid User ID. Please check and try again."
        )

    return render_template(
        "update.html",
        success="Medical records updated successfully"
    )

# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)

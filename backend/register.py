from flask import Blueprint, request, render_template
import qrcode
import os
from models import register_citizen

register_bp = Blueprint('register', __name__)

@register_bp.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        name = request.form.get('name')
        blood_group = request.form.get('blood_group')
        medical_info = request.form.get('medical_info')
        emergency_contact = request.form.get('emergency_contact')
        consent = request.form.get('consent')

        # Consent check
        if not consent:
            return render_template(
                "register.html",
                error="Consent is required to proceed"
            )

        # Register citizen in DB
        citizen_id = register_citizen(
            name=name,
            blood_group=blood_group,
            medical_info=medical_info,
            emergency_contact=emergency_contact,
            consent=True
        )

        # Generate QR Code
        qr_folder = os.path.join("static", "qr_codes")
        os.makedirs(qr_folder, exist_ok=True)

        qr_path = os.path.join(qr_folder, f"{citizen_id}.png")
        qr = qrcode.make(citizen_id)
        qr.save(qr_path)

        # Show success page instead of JSON
        return render_template(
            "register_success.html",
            citizen_id=citizen_id,
            qr_path=f"/static/qr_codes/{citizen_id}.png"
        )

    # GET request → show registration form
    return render_template("register.html")


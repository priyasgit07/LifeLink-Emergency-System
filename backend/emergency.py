from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from models import (
    get_citizen_by_id,
    log_access,
    get_all_citizens,
    get_citizen_by_fingerprint
)
from datetime import datetime
import cv2   # kept for future real integration

emergency_bp = Blueprint('emergency', __name__)

# ---------------- AUTH CHECK ----------------
def require_auth(f):
    def wrapper(*args, **kwargs):
        if 'authority_username' not in session:
            if request.is_json or request.method == 'POST':
                return jsonify({
                    'error': 'Session expired. Please login again.',
                    'session_expired': True
                }), 401
            return redirect(url_for('auth.login_page'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# ---------------- SESSION CHECK ----------------
@emergency_bp.route('/check_session', methods=['GET'])
def check_session():
    if 'authority_username' in session:
        return jsonify({'valid': True})
    return jsonify({'valid': False, 'message': 'Session expired'}), 401

# ---------------- SCAN PAGE ----------------
@emergency_bp.route('/scan', methods=['GET'])
@require_auth
def scan_page():
    return render_template('scan.html')

# ---------------- QR / MANUAL ACCESS ----------------
@emergency_bp.route('/access', methods=['POST'])
@require_auth
def access_medical_data():
    citizen_id = request.form.get('citizen_id')

    if not citizen_id:
        return jsonify({'error': 'Citizen ID is required'}), 400

    citizen = get_citizen_by_id(citizen_id)

    if not citizen:
        return jsonify({'error': 'Citizen not found'}), 404

    authority_username = session['authority_username']
    log_access(authority_username, citizen_id)

    alert_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    alert_message = f"Emergency alert sent to {citizen['emergency_contact']}"

    return jsonify({
        'name': citizen['name'],
        'blood_group': citizen['blood_group'],
        'medical_info': citizen['medical_info'] or 'None',
        'emergency_contact': citizen['emergency_contact'],
        'timestamp': alert_timestamp,
        'alert_sent': True,
        'alert_message': alert_message
    })

# ---------------- FACE RECOGNITION (SIMULATED) ----------------
@emergency_bp.route('/face_recognize', methods=['POST'])
@require_auth
def face_recognize():
    """
    Face recognition simulated for hackathon demo.
    Architecture supports real biometric integration.
    """
    try:
        citizens = get_all_citizens()

        if not citizens:
            return jsonify({'error': 'No citizens registered'}), 404

        # Simulate successful face match (first citizen)
        citizen = citizens[0]

        authority_username = session['authority_username']
        log_access(authority_username, citizen['id'])

        alert_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        alert_message = f"Emergency alert sent to {citizen['emergency_contact']}"

        return jsonify({
            'name': citizen['name'],
            'blood_group': citizen['blood_group'],
            'medical_info': citizen['medical_info'] or 'None',
            'emergency_contact': citizen['emergency_contact'],
            'timestamp': alert_timestamp,
            'alert_sent': True,
            'alert_message': alert_message,
            'note': 'Face recognition simulated for demo stability'
        })

    except Exception as e:
        return jsonify({
            'error': f'Face recognition simulation error: {str(e)}'
        }), 500

# ---------------- FINGERPRINT IDENTIFICATION ----------------
@emergency_bp.route('/fingerprint_identify', methods=['POST'])
@require_auth
def fingerprint_identify():
    fingerprint_id = request.form.get('fingerprint_id')

    if not fingerprint_id:
        return jsonify({'error': 'Fingerprint ID is required'}), 400

    citizen = get_citizen_by_fingerprint(fingerprint_id)

    if not citizen:
        return jsonify({'error': 'No matching fingerprint found in database'}), 404

    authority_username = session['authority_username']
    log_access(authority_username, citizen['id'])

    alert_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    alert_message = f"Emergency alert sent to {citizen['emergency_contact']}"

    return jsonify({
        'name': citizen['name'],
        'blood_group': citizen['blood_group'],
        'medical_info': citizen['medical_info'] or 'None',
        'emergency_contact': citizen['emergency_contact'],
        'timestamp': alert_timestamp,
        'alert_sent': True,
        'alert_message': alert_message
    })

# ---------------- RESULT PAGE ----------------
@emergency_bp.route('/result', methods=['GET'])
@require_auth
def result_page():
    return render_template('result.html')

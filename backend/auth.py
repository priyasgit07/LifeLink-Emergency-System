from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from models import verify_authority

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@auth_bp.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if verify_authority(username, password):
        session['authority_username'] = username
        return jsonify({'success': True, 'redirect': '/scan'})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@auth_bp.route('/logout')
def logout():
    session.pop('authority_username', None)
    return redirect(url_for('auth.login_page'))

def require_auth(f):
    def wrapper(*args, **kwargs):
        if 'authority_username' not in session:
            return redirect(url_for('auth.login_page'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

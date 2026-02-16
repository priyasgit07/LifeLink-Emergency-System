import sqlite3
import uuid
from datetime import datetime
import os

# Absolute path to backend directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database file path
DATABASE = os.path.join(BASE_DIR, "database.db")


# -------------------- DATABASE INIT --------------------
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Citizens table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS citizens (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            blood_group TEXT NOT NULL,
            medical_info TEXT,
            emergency_contact TEXT NOT NULL,
            consent INTEGER NOT NULL,
            face_encoding TEXT,
            fingerprint_id TEXT
        )
    """)

    # Authorities table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS authorities (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    """)

    # Access logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS access_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            authority_username TEXT NOT NULL,
            citizen_id TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    # Default authority
    cursor.execute(
        "INSERT OR IGNORE INTO authorities (username, password) VALUES (?, ?)",
        ("emergency", "rescue123")
    )

    conn.commit()
    conn.close()


# -------------------- DB CONNECTION --------------------
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# -------------------- CITIZEN REGISTRATION --------------------
def register_citizen(
    name, blood_group, medical_info, emergency_contact, consent,
    face_encoding=None, fingerprint_id=None
):
    citizen_id = str(uuid.uuid4())
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO citizens
        (id, name, blood_group, medical_info, emergency_contact, consent, face_encoding, fingerprint_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        citizen_id,
        name,
        blood_group,
        medical_info,
        emergency_contact,
        1 if consent else 0,
        face_encoding,
        fingerprint_id
    ))

    conn.commit()
    conn.close()
    return citizen_id


# -------------------- GET CITIZENS --------------------
def get_citizen_by_id(citizen_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM citizens WHERE id = ?", (citizen_id,))
    citizen = cursor.fetchone()
    conn.close()
    return citizen


def get_citizen_by_fingerprint(fingerprint_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM citizens WHERE fingerprint_id = ?",
        (fingerprint_id,)
    )
    citizen = cursor.fetchone()
    conn.close()
    return citizen


def get_all_citizens():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, face_encoding FROM citizens WHERE face_encoding IS NOT NULL"
    )
    citizens = cursor.fetchall()
    conn.close()
    return citizens


# -------------------- AUTHORITY --------------------
def verify_authority(username, password):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM authorities WHERE username = ? AND password = ?",
        (username, password)
    )
    authority = cursor.fetchone()
    conn.close()
    return authority is not None


# -------------------- ACCESS LOGGING --------------------
def log_access(authority_username, citizen_id):
    conn = get_db()
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO access_logs (authority_username, citizen_id, timestamp)
        VALUES (?, ?, ?)
    """, (
        authority_username,
        citizen_id,
        timestamp
    ))

    conn.commit()
    conn.close()


def get_access_logs():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM access_logs ORDER BY timestamp DESC")
    logs = cursor.fetchall()
    conn.close()
    return logs


# -------------------- UPDATE MEDICAL RECORD --------------------
def update_medical_record(citizen_id, treatment, new_conditions):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT medical_info FROM citizens WHERE id = ?",
        (citizen_id,)
    )

    row = cursor.fetchone()
    if not row:
        conn.close()
        return False

    old_info = row["medical_info"] or ""

    updated_info = (
        old_info
        + "\n\n--- Post Treatment Update ---\n"
        + "Treatment: " + treatment
    )

    if new_conditions:
        updated_info += "\nNew Conditions: " + new_conditions

    cursor.execute(
        "UPDATE citizens SET medical_info = ? WHERE id = ?",
        (updated_info, citizen_id)
    )

    conn.commit()
    conn.close()
    return True

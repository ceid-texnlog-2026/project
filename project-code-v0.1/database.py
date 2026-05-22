"""SQLite persistence layer for RedHope.

The in-memory object model (Donor/Hospital/etc.) remains the source of truth
during runtime. This module loads it from disk on startup and rewrites the
relevant rows after each mutation via `save_*` helpers.
"""

import sqlite3
import json
import os
from datetime import datetime, date


DB_PATH = os.path.join(os.path.dirname(__file__), "redhope.sqlite3")


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT NOT NULL,
    username TEXT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    is_suspended INTEGER DEFAULT 0,
    full_name TEXT, amka TEXT, blood_type TEXT, phone TEXT,
    qr_code TEXT, is_available INTEGER DEFAULT 0,
    date_of_birth TEXT, gender TEXT,
    name TEXT, address TEXT, city TEXT, region TEXT,
    service_code TEXT, is_certified INTEGER DEFAULT 0,
    must_change_password INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS applications (
    request_id INTEGER PRIMARY KEY AUTOINCREMENT,
    hospital_user_id INTEGER,
    status TEXT DEFAULT 'pending',
    center_type TEXT, hospital_name TEXT,
    contact_name TEXT, contact_email TEXT,
    phone TEXT, address TEXT, city TEXT, region TEXT,
    documents TEXT,
    cross_reference_passed INTEGER DEFAULT 0,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS reports (
    report_id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT, justification TEXT DEFAULT '',
    status TEXT DEFAULT 'open', action TEXT DEFAULT '',
    reporter_id INTEGER, reporter_name TEXT,
    target_type TEXT, target_identifier TEXT,
    created_at TEXT,
    clarification_requested_at TEXT
);

CREATE TABLE IF NOT EXISTS appointments (
    appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    donor_id INTEGER, hospital_id INTEGER,
    appointment_date TEXT, time TEXT,
    status TEXT DEFAULT 'upcoming'
);

CREATE TABLE IF NOT EXISTS donations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    donor_id INTEGER, hospital_id INTEGER,
    donation_date TEXT, blood_group TEXT,
    donation_type TEXT, amount_ml INTEGER,
    organization TEXT, status TEXT DEFAULT 'completed',
    notes TEXT
);

CREATE TABLE IF NOT EXISTS medical_documents (
    document_id INTEGER PRIMARY KEY AUTOINCREMENT,
    donor_id INTEGER, filename TEXT,
    upload_date TEXT, document_type TEXT, file_path TEXT
);

CREATE TABLE IF NOT EXISTS certificates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    donor_id INTEGER, hospital_id INTEGER,
    certificate_number TEXT, issue_date TEXT,
    donation_date TEXT, donor_name TEXT,
    organization TEXT, pdf_path TEXT,
    status TEXT DEFAULT 'issued'
);

CREATE TABLE IF NOT EXISTS blood_units (
    unit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    hospital_id INTEGER, blood_type TEXT,
    quantity INTEGER, unit_code TEXT,
    collection_date TEXT, expiration_date TEXT,
    product_type TEXT, status TEXT DEFAULT 'available'
);

CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER, message TEXT, created_at TEXT
);
"""


def _iso(d):
    if d is None:
        return None
    if isinstance(d, (datetime, date)):
        return d.isoformat()
    return str(d)


def _parse_date(s):
    if not s:
        return None
    try:
        return date.fromisoformat(s[:10])
    except Exception:
        return None


def _parse_datetime(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None


class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_conn()
        return cls._instance

    def _init_conn(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        # Safe migrations for columns added after initial release
        for sql in [
            "ALTER TABLE reports ADD COLUMN clarification_requested_at TEXT",
        ]:
            try:
                self.conn.execute(sql)
            except sqlite3.OperationalError:
                pass  # column already exists
        self.conn.commit()

    # ---------- USER PERSISTENCE ----------

    def insert_user(self, role: str, user) -> int:
        cur = self.conn.execute(
            """INSERT INTO users (role, username, email, password, status,
               is_suspended, full_name, amka, blood_type, phone, qr_code,
               is_available, date_of_birth, gender, name, address, city, region,
               service_code, is_certified, must_change_password)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                role, user.username, user.email, user.password, user.status,
                int(getattr(user, "is_suspended", False)),
                getattr(user, "full_name", None),
                getattr(user, "amka", None),
                getattr(user, "blood_type", None),
                getattr(user, "phone", None),
                getattr(user, "qr_code", None),
                int(getattr(user, "is_available", False)),
                _iso(getattr(user, "date_of_birth", None)),
                getattr(user, "gender", None),
                getattr(user, "name", None),
                getattr(user, "address", None),
                getattr(user, "city", None),
                getattr(user, "region", None),
                getattr(user, "service_code", None),
                int(getattr(user, "is_certified", False)),
                int(getattr(user, "must_change_password", False)),
            ),
        )
        self.conn.commit()
        return cur.lastrowid

    def update_user(self, user_id: int, user):
        self.conn.execute(
            """UPDATE users SET username=?, email=?, password=?, status=?,
               is_suspended=?, full_name=?, amka=?, blood_type=?, phone=?,
               qr_code=?, is_available=?, date_of_birth=?, gender=?, name=?,
               address=?, city=?, region=?, service_code=?, is_certified=?,
               must_change_password=? WHERE user_id=?""",
            (
                user.username, user.email, user.password, user.status,
                int(getattr(user, "is_suspended", False)),
                getattr(user, "full_name", None),
                getattr(user, "amka", None),
                getattr(user, "blood_type", None),
                getattr(user, "phone", None),
                getattr(user, "qr_code", None),
                int(getattr(user, "is_available", False)),
                _iso(getattr(user, "date_of_birth", None)),
                getattr(user, "gender", None),
                getattr(user, "name", None),
                getattr(user, "address", None),
                getattr(user, "city", None),
                getattr(user, "region", None),
                getattr(user, "service_code", None),
                int(getattr(user, "is_certified", False)),
                int(getattr(user, "must_change_password", False)),
                user_id,
            ),
        )
        self.conn.commit()

    def load_users(self):
        return list(self.conn.execute("SELECT * FROM users"))

    def email_exists(self, email: str) -> bool:
        row = self.conn.execute(
            "SELECT 1 FROM users WHERE email = ?", (email,)
        ).fetchone()
        return row is not None

    # ---------- APPLICATION PERSISTENCE ----------

    def insert_application(self, app) -> int:
        cur = self.conn.execute(
            """INSERT INTO applications (hospital_user_id, status, center_type,
               hospital_name, contact_name, contact_email, phone, address, city,
               region, documents, cross_reference_passed, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                getattr(app, "hospital_user_id", None),
                app.status, app.center_type, app.hospital_name,
                app.contact_name, app.contact_email, app.phone,
                app.address, app.city, app.region,
                json.dumps(app.documents),
                int(app.cross_reference_passed),
                _iso(app.created_at),
            ),
        )
        self.conn.commit()
        return cur.lastrowid

    def update_application(self, app):
        self.conn.execute(
            """UPDATE applications SET status=?, cross_reference_passed=?,
               documents=? WHERE request_id=?""",
            (app.status, int(app.cross_reference_passed),
             json.dumps(app.documents), app.request_id),
        )
        self.conn.commit()

    def load_applications(self):
        return list(self.conn.execute("SELECT * FROM applications"))

    # ---------- REPORTS ----------

    def insert_report(self, r) -> int:
        cur = self.conn.execute(
            """INSERT INTO reports (description, justification, status, action,
               reporter_id, reporter_name, target_type, target_identifier,
               created_at, clarification_requested_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (r.description, r.justification, r.status, r.action,
             r.reporter_id, r.reporter_name, r.target_type,
             r.target_identifier, _iso(r.created_at),
             _iso(getattr(r, "clarification_requested_at", None))),
        )
        self.conn.commit()
        return cur.lastrowid

    def update_report(self, r):
        self.conn.execute(
            """UPDATE reports SET status=?, justification=?, action=?,
               clarification_requested_at=? WHERE report_id=?""",
            (r.status, r.justification, r.action,
             _iso(getattr(r, "clarification_requested_at", None)),
             r.report_id),
        )
        self.conn.commit()

    def load_reports(self):
        return list(self.conn.execute("SELECT * FROM reports"))

    # ---------- APPOINTMENTS ----------

    def insert_appointment(self, a, donor_id: int, hospital_id: int) -> int:
        cur = self.conn.execute(
            """INSERT INTO appointments (donor_id, hospital_id, appointment_date,
               time, status) VALUES (?, ?, ?, ?, ?)""",
            (donor_id, hospital_id, _iso(a.appointment_date), a.time, a.status),
        )
        self.conn.commit()
        return cur.lastrowid

    def update_appointment_status(self, appointment_id: int, status: str):
        self.conn.execute(
            "UPDATE appointments SET status=? WHERE appointment_id=?",
            (status, appointment_id),
        )
        self.conn.commit()

    def load_appointments(self):
        return list(self.conn.execute("SELECT * FROM appointments"))

    # ---------- DONATIONS ----------

    def insert_donation(self, d, hospital_id: int) -> int:
        cur = self.conn.execute(
            """INSERT INTO donations (donor_id, hospital_id, donation_date,
               blood_group, donation_type, amount_ml, organization, status, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (d.donor_id, hospital_id, _iso(d.donation_date), d.blood_group,
             d.donation_type, d.amount_ml, d.organization, d.status, d.notes),
        )
        self.conn.commit()
        return cur.lastrowid

    def load_donations(self):
        return list(self.conn.execute("SELECT * FROM donations"))

    # ---------- MEDICAL DOCUMENTS ----------

    def insert_medical_document(self, doc, donor_id: int) -> int:
        cur = self.conn.execute(
            """INSERT INTO medical_documents (donor_id, filename, upload_date,
               document_type, file_path) VALUES (?, ?, ?, ?, ?)""",
            (donor_id, doc.filename, _iso(doc.upload_date),
             doc.document_type, getattr(doc, "file_path", "")),
        )
        self.conn.commit()
        return cur.lastrowid

    def load_medical_documents(self):
        return list(self.conn.execute("SELECT * FROM medical_documents"))

    # ---------- CERTIFICATES ----------

    def insert_certificate(self, c) -> int:
        cur = self.conn.execute(
            """INSERT INTO certificates (donor_id, hospital_id,
               certificate_number, issue_date, donation_date, donor_name,
               organization, pdf_path, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (c.donor_id, c.hospital_id, c.certificate_number,
             _iso(c.issue_date), _iso(c.donation_date), c.donor_name,
             c.organization, c.pdf_path, c.status),
        )
        self.conn.commit()
        return cur.lastrowid

    def load_certificates(self):
        return list(self.conn.execute("SELECT * FROM certificates"))

    # ---------- BLOOD UNITS ----------

    def insert_blood_unit(self, u, hospital_id: int) -> int:
        cur = self.conn.execute(
            """INSERT INTO blood_units (hospital_id, blood_type, quantity,
               unit_code, collection_date, expiration_date, product_type, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (hospital_id, u.blood_type, u.quantity, u.unit_code,
             _iso(u.collection_date), _iso(u.expiration_date),
             u.product_type, u.status),
        )
        self.conn.commit()
        return cur.lastrowid

    def update_blood_unit_status(self, unit_code: str, hospital_id: int,
                                 status: str):
        self.conn.execute(
            """UPDATE blood_units SET status=? WHERE unit_code=?
               AND hospital_id=?""",
            (status, unit_code, hospital_id),
        )
        self.conn.commit()

    def load_blood_units(self):
        return list(self.conn.execute("SELECT * FROM blood_units"))

    # ---------- NOTIFICATIONS ----------

    def insert_notification(self, user_id: int, message: str):
        self.conn.execute(
            """INSERT INTO notifications (user_id, message, created_at)
               VALUES (?, ?, ?)""",
            (user_id, message, _iso(datetime.now())),
        )
        self.conn.commit()

    def load_notifications_for(self, user_id: int):
        return list(self.conn.execute(
            "SELECT message FROM notifications WHERE user_id=? ORDER BY id",
            (user_id,),
        ))

    def clear_notifications_for(self, user_id: int):
        self.conn.execute(
            "DELETE FROM notifications WHERE user_id=?", (user_id,)
        )
        self.conn.commit()


__all__ = ["Database", "_parse_date", "_parse_datetime"]

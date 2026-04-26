from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Initialize Flask app and SQLAlchemy
app = Flask(__name__)
db = SQLAlchemy()


class HealthcareProvider(db.Model):
    __tablename__ = "healthcare_providers"

    id = db.Column(db.Integer, primary_key=True)
    membership_status = db.Column(db.String)
    nearest_facility = db.Column(db.String)
    prime_privileges = db.Column(db.String)
    physician_type = db.Column(db.String)
    affiliation_status = db.Column(db.String)
    specialty = db.Column(db.String, index=True)
    sub_specialty = db.Column(db.String, index=True)
    service_details = db.Column(db.String)
    gender = db.Column(db.String)
    first_name = db.Column(db.String, index=True)
    last_name = db.Column(db.String, index=True)
    middle_name = db.Column(db.String, index=True)
    title = db.Column(db.String)
    service_location = db.Column(db.String, index=True)
    address = db.Column(db.String, index=True)
    city = db.Column(db.String, index=True)
    state = db.Column(db.String, index=True)
    zip_code = db.Column(db.String, index=True)
    phone = db.Column(db.String)
    fax = db.Column(db.String)
    preferred_provider = db.Column(db.String)

    def to_dict(self):
        return {
            "id": self.id,
            "membership_status": self.membership_status,
            "nearest_facility": self.nearest_facility,
            "prime_privileges": self.prime_privileges,
            "physician_type": self.physician_type,
            "affiliation_status": self.affiliation_status,
            "specialty": self.specialty,
            "sub_specialty": self.sub_specialty,
            "service_details": self.service_details,
            "gender": self.gender,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "middle_name": self.middle_name,
            "title": self.title,
            "service_location": self.service_location,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code,
            "phone": self.phone,
            "fax": self.fax,
            "preferred_provider": self.preferred_provider,
        }


class Suites(db.Model):
    __tablename__ = "suites"

    id = db.Column(db.Integer, primary_key=True)
    suite = db.Column(db.String)
    physician_name = db.Column(db.String)
    practice_name = db.Column(db.String)

    def to_dict(self):
        return {
            "suite": self.suite,
            "physician_name": self.physician_name,
            "practice_name": self.practice_name,
        }


def init_db(flask_app):
    database_url = os.getenv("DATABASE_URL")
    if database_url and database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(flask_app)

    with flask_app.app_context():
        db.create_all()

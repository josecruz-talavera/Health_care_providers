from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask app and SQLAlchemy
app = Flask(__name__)
db = SQLAlchemy()

class HealthcareProvider(db.Model):
    __tablename__ = 'healthcare_providers'

    id = db.Column(db.Integer, primary_key=True)
    membership_status = db.Column(db.String)
    nearest_facility = db.Column(db.String)
    prime_privileges = db.Column(db.String)
    physician_type = db.Column(db.String)
    affiliation_status = db.Column(db.String)
    specialty = db.Column(db.String, index=True)  # Full-text search
    sub_specialty = db.Column(db.String, index=True)  # Full-text search
    service_details = db.Column(db.String)
    gender = db.Column(db.String)
    first_name = db.Column(db.String, index=True)  # Full-text search
    last_name = db.Column(db.String, index=True)  # Full-text search
    middle_name = db.Column(db.String, index=True)  # Full-text search
    title = db.Column(db.String)
    service_location = db.Column(db.String, index=True)  # Full-text search
    address = db.Column(db.String, index=True)  # Full-text search
    city = db.Column(db.String, index=True)  # Full-text search
    state = db.Column(db.String, index=True)  # Full-text search
    zip_code = db.Column(db.String, index=True)  # Full-text search
    phone = db.Column(db.String)
    fax = db.Column(db.String)
    preferred_provider = db.Column(db.String)

    def to_dict(self):
        return {
            'id': self.id,
            'membership_status': self.membership_status,
            'nearest_facility': self.nearest_facility,
            'prime_privileges': self.prime_privileges,
            'physician_type': self.physician_type,
            'affiliation_status': self.affiliation_status,
            'specialty': self.specialty,
            'sub_specialty': self.sub_specialty,
            'service_details': self.service_details,
            'gender': self.gender,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'middle_name': self.middle_name,
            'title': self.title,
            'service_location': self.service_location,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'phone': self.phone,
            'fax': self.fax,
            'preferred_provider': self.preferred_provider
        }

class Suites(db.Model):
    __tablename__ = 'suites'

    id = db.Column(db.Integer, primary_key=True)
    suite = db.Column(db.String)
    physician_name = db.Column(db.String)
    practice_name = db.Column(db.String)

    def to_dict(self):
        return {
            'suite': self.suite,
            'physician_name': self.physician_name,
            'practice_name': self.practice_name
        }


class Price_quotes(db.Model):
    __tablename__ = 'price_quotes'

    id = db.Column(db.Integer, primary_key=True)
    procedure = db.Column(db.String, index=True)
    code = db.Column(db.String, index=True)
    type = db.Column(db.String, index=True)

    standard_charges = db.relationship(
        'Standard_charges',
        backref='price_quote',
        lazy=True,
        cascade='all, delete-orphan'
    )


class Standard_charges(db.Model):
    __tablename__ = 'standard_charges'

    id = db.Column(db.Integer, primary_key=True)
    setting = db.Column(db.String, index=True)
    minimum = db.Column(db.Float)
    maximum = db.Column(db.Float)
    price_quote_id = db.Column(db.Integer, db.ForeignKey('price_quotes.id'), index=True)

    payers_information = db.relationship(
        'Payers_information',
        backref='standard_charge',
        lazy=True,
        cascade='all, delete-orphan'
    )


class Payers_information(db.Model):
    __tablename__ = 'payers_information'

    id = db.Column(db.Integer, primary_key=True)
    payer_name = db.Column(db.String, index=True)
    plan_name = db.Column(db.String, index=True)
    standard_charge_dollar = db.Column(db.Float)
    estimated_amount = db.Column(db.Float)
    methodology = db.Column(db.String)
    standard_charge_id = db.Column(db.Integer, db.ForeignKey('standard_charges.id'), index=True)


def init_db(flask_app):
    database_path = flask_app.config.get('DATABASE_PATH', 'healthcare.db')
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{database_path}"
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(flask_app)

    with flask_app.app_context():
        db.create_all()

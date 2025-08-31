from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text

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
    procedure = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    
    # Relationship with Standard_charges
    standard_charges = db.relationship('Standard_charges', backref='price_quote', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Price_quote {self.procedure} ({self.code})>'

class Standard_charges(db.Model):
    __tablename__ = 'standard_charges'
    
    id = db.Column(db.Integer, primary_key=True)
    setting = db.Column(db.String(100), nullable=False)
    minimum = db.Column(db.Float, nullable=True)
    maximum = db.Column(db.Float, nullable=True)
    
    # Foreign key to Price_quotes
    price_quote_id = db.Column(db.Integer, db.ForeignKey('price_quotes.id'), nullable=False)
    
    # Relationship with Payers_information
    payers_information = db.relationship('Payers_information', backref='standard_charge', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Standard_charge {self.setting} (Min: {self.minimum}, Max: {self.maximum})>'

class Payers_information(db.Model):
    __tablename__ = 'payers_information'
    
    id = db.Column(db.Integer, primary_key=True)
    payer_name = db.Column(db.String(255), nullable=False)
    plan_name = db.Column(db.String(255), nullable=True)
    standard_charge_dollar = db.Column(db.Float, nullable=False)
    estimated_amount = db.Column(db.Float, nullable=True)
    methodology = db.Column(db.Text, nullable=True)
    
    # Foreign key to Standard_charges
    standard_charge_id = db.Column(db.Integer, db.ForeignKey('standard_charges.id'), nullable=False)
    
    def __repr__(self):
        return f'<Payer_information {self.payer_name} - {self.plan_name}>'

def init_db(app):
    """Initialize the database and create FTS tables"""
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{app.config["DATABASE_PATH"]}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize the SQLAlchemy app
    db.init_app(app)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create virtual tables for full-text search
        db.session.execute(text("""
            CREATE VIRTUAL TABLE IF NOT EXISTS provider_fts USING fts5(
                first_name, last_name, middle_name,
                specialty, sub_specialty, service_location,
                address, city, state, zip_code,
                content='healthcare_providers',
                content_rowid='id'
            )
        """))
        
        # Create triggers to keep FTS index up to date
        db.session.execute(text("""
            CREATE TRIGGER IF NOT EXISTS healthcare_providers_ai AFTER INSERT ON healthcare_providers BEGIN
                INSERT INTO provider_fts(rowid, first_name, last_name, middle_name, 
                    specialty, sub_specialty, service_location,
                    address, city, state, zip_code)
                VALUES (new.id, new.first_name, new.last_name, new.middle_name,
                    new.specialty, new.sub_specialty, new.service_location,
                    new.address, new.city, new.state, new.zip_code);
            END
        """))
        
        db.session.execute(text("""
            CREATE TRIGGER IF NOT EXISTS healthcare_providers_ad AFTER DELETE ON healthcare_providers BEGIN
                INSERT INTO provider_fts(provider_fts, rowid, first_name, last_name, middle_name,
                    specialty, sub_specialty, service_location,
                    address, city, state, zip_code)
                VALUES('delete', old.id, old.first_name, old.last_name, old.middle_name,
                    old.specialty, old.sub_specialty, old.service_location,
                    old.address, old.city, old.state, old.zip_code);
            END
        """))
        
        db.session.execute(text("""
            CREATE TRIGGER IF NOT EXISTS healthcare_providers_au AFTER UPDATE ON healthcare_providers BEGIN
                INSERT INTO provider_fts(provider_fts, rowid, first_name, last_name, middle_name,
                    specialty, sub_specialty, service_location,
                    address, city, state, zip_code)
                VALUES('delete', old.id, old.first_name, old.last_name, old.middle_name,
                    old.specialty, old.sub_specialty, old.service_location,
                    old.address, old.city, old.state, old.zip_code);
                INSERT INTO provider_fts(rowid, first_name, last_name, middle_name,
                    specialty, sub_specialty, service_location,
                    address, city, state, zip_code)
                VALUES (new.id, new.first_name, new.last_name, new.middle_name,
                    new.specialty, new.sub_specialty, new.service_location,
                    new.address, new.city, new.state, new.zip_code);
            END
        """))
        
        db.session.commit()

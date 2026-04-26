from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import text, distinct
from models import (
    app,
    db,
    HealthcareProvider,
    Suites,
    init_db,
)
from admin import init_admin, login_manager, login_user, login_required, logout_user, current_user, User
from collections import defaultdict
from dotenv import load_dotenv
import os
from sqlalchemy import or_, and_

# Initialize the database and admin interface
load_dotenv()
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
init_db(app)
init_admin(app)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('admin.index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/')
def index():
    name = request.args.get('name', '')
    specialty = request.args.get('specialty', '')
    location = request.args.get('location', '')
    
    specialty_synonyms = {
        'cancer': ['hematology', 'oncology', 'hematology/oncology', 'medical oncology', 'radiation oncology'],
        'hematology': ['cancer', 'oncology', 'hematology/oncology', 'medical oncology'],
        'oncology': ['cancer', 'hematology', 'hematology/oncology', 'medical oncology', 'radiation oncology'],
        'cardiology': ['heart', 'cardiovascular'],
        'orthopedics': ['ortho', 'bone', 'joint'],
        'pediatrics': ['pediatric', 'children', 'child'],
        'psychiatry': ['psychiatric', 'mental health', 'behavioral health'],
        'neurology': ['neurological', 'brain', 'nervous system'],
        'dermatology': ['skin', 'dermatological'],
        'endocrinology': ['hormone', 'diabetes', 'thyroid'],
        'gastroenterology': ['gi', 'digestive', 'stomach', 'intestine'],
        'nephrology': ['kidney', 'renal'],
        'pulmonology': ['lung', 'respiratory', 'breathing'],
        'rheumatology': ['arthritis', 'joint', 'rheumatic'],
        'urology': ['urinary', 'bladder', 'prostate'],
        'ent': ['otolaryngology'],
        'ophthalmology': ['eye', 'vision', 'retina'],
        'podiatry': ['foot', 'ankle', 'podiatric'],
        'plastic surgery': ['cosmetic', 'reconstructive'],
        'general surgery': ['surgical', 'surgeon'],
        'family medicine': ['family practice', 'primary care', 'general practice'],
        'internal medicine': ['internist', 'internal'],
        'emergency medicine': ['er', 'emergency room', 'emergency department'],
        'obstetrics': ['ob', 'pregnancy', 'prenatal'],
        'gynecology': ['gyn', 'women health', 'reproductive'],
        'obstetrics and gynecology': ['obgyn', 'ob/gyn', 'women health', 'reproductive']
    }
    
    base_query = HealthcareProvider.query
    
    if name:
        name_terms = name.split()
        name_conditions = []
        for term in name_terms:
            name_conditions.append(
                or_(
                    HealthcareProvider.first_name.ilike(f'{term}%'),
                    HealthcareProvider.last_name.ilike(f'{term}%')
                )
            )
        base_query = base_query.filter(and_(*name_conditions))
    
    if specialty:
        specialty_terms = specialty.lower().split()
        specialty_conditions = []
        for term in specialty_terms:
            synonyms = specialty_synonyms.get(term, [term])
            term_conditions = []
            for syn in synonyms:
                term_conditions.extend([
                    HealthcareProvider.specialty.ilike(f'%{syn}%'),
                    HealthcareProvider.sub_specialty.ilike(f'%{syn}%')
                ])
            specialty_conditions.append(or_(*term_conditions))
        base_query = base_query.filter(and_(*specialty_conditions))
    
    if location:
        location_terms = location.split()
        location_conditions = []
        for term in location_terms:
            location_conditions.append(
                or_(
                    HealthcareProvider.service_location.ilike(f'%{term}%'),
                    HealthcareProvider.address.ilike(f'%{term}%'),
                    HealthcareProvider.city.ilike(f'%{term}%'),
                    HealthcareProvider.state.ilike(f'%{term}%'),
                    HealthcareProvider.zip_code.ilike(f'%{term}%')
                )
            )
        base_query = base_query.filter(and_(*location_conditions))
    
    results = base_query.order_by(HealthcareProvider.last_name, HealthcareProvider.first_name).all()
    
    return render_template('homepage.html',
                         results=results,
                         name=name,
                         specialty=specialty,
                         location=location)

@app.route('/suites')
def suites():
    suites = Suites.query.all()
    
    suite_groups = defaultdict(lambda: {'practices': [], 'physicians': []})
    
    for suite in suites:
        if suite.suite:
            if suite.practice_name:
                suite_groups[suite.suite]['practices'].append(suite.practice_name)
            if suite.physician_name:
                suite_groups[suite.suite]['physicians'].append(suite.physician_name)
    
    entries = []
    for suite, data in suite_groups.items():
        entries.append({
            'suite': suite,
            'practices': data['practices'],
            'physicians': data['physicians']
        })
    
    entries.sort(key=lambda x: int(x['suite']) if x['suite'].isdigit() else float('inf'))
    
    return render_template('suites.html', entries=entries)


@app.route('/setup')
def setup():
    db.create_all()

    if HealthcareProvider.query.first():
        return "Database already set up!"

    import pandas as pd

    # Process PCP CSV
    pcp_path = os.path.join(os.path.dirname(__file__), 'data', 'Prime-Healthcare-Network-IL_PCP-Directory1.csv')
    sp_path = os.path.join(os.path.dirname(__file__), 'data', 'Prime-Healthcare-Network-IL_SP-Directory1.csv')
    suites_path = os.path.join(os.path.dirname(__file__), 'data', 'suites-smn.xlsx')

    column_mapping = {
        'Membership Status': 'membership_status',
        'NearestFaclity': 'nearest_facility',
        'Prime Privileges': 'prime_privileges',
        'Physician Type': 'physician_type',
        'Affliation Status': 'affiliation_status',
        'Specialty': 'specialty',
        'Sub Specialty': 'sub_specialty',
        'Service Details': 'service_details',
        'Gender': 'gender',
        'FirstName': 'first_name',
        'Last Name': 'last_name',
        'MiddleName': 'middle_name',
        'Title': 'title',
        'Service Location (DBA)': 'service_location',
        'Address': 'address',
        'City': 'city',
        'State': 'state',
        'Zip': 'zip_code',
        'Phone': 'phone',
        'Fax': 'fax',
        'Preferred Provider': 'preferred_provider'
    }

    for csv_path in [pcp_path, sp_path]:
        df = pd.read_csv(csv_path)
        df = df.rename(columns=column_mapping)
        df = df.where(pd.notna(df), None)
        for record in df.to_dict('records'):
            provider = HealthcareProvider(**{k: v for k, v in record.items() if k in column_mapping.values()})
            db.session.add(provider)
    db.session.commit()

    # Process suites
    df_suites = pd.read_excel(suites_path)
    df_suites = df_suites.rename(columns={
        'SUITE': 'suite',
        'PHYSICIAN NAME': 'physician_name',
        'PRACTICE NAME': 'practice_name'
    })
    for record in df_suites.to_dict('records'):
        import math
        if record.get('suite') and not (isinstance(record['suite'], float) and math.isnan(record['suite'])):
            suite = Suites(
                suite=str(record['suite']),
                physician_name=record.get('physician_name'),
                practice_name=record.get('practice_name')
            )
            db.session.add(suite)
    db.session.commit()

    return "Database set up and populated successfully!"


@app.route('/create-admin')
def create_admin():
    db.create_all()
    admin_username = os.getenv('ADMIN_USERNAME')
    admin_password = os.getenv('ADMIN_PASSWORD')

    if User.query.filter_by(username=admin_username).first():
        return "Admin already exists!"

    admin_user = User(username=admin_username)
    admin_user.set_password(admin_password)
    db.session.add(admin_user)
    db.session.commit()
    return "Admin created!"


if __name__ == '__main__':
    app.run(debug=True)
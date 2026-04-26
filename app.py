from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import text, distinct
from models import (
    app,
    db,
    HealthcareProvider,
    Suites,
    Price_quotes,
    Standard_charges,
    Payers_information,
    init_db,
)
from admin import init_admin, login_manager, login_user, login_required, logout_user, current_user, User
import re
import pandas as pd
from pathlib import Path
from collections import defaultdict
from dotenv import load_dotenv
import os
from sqlalchemy import or_, and_

# Initialize the database and admin interface
load_dotenv()
app.config['DATABASE_PATH'] = os.getenv('DATABASE_PATH')
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
    query = request.args.get('query', '')
    name = request.args.get('name', '')
    specialty = request.args.get('specialty', '')
    location = request.args.get('location', '')
    
    # Define specialty synonyms and related terms
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
    
    # Build the query
    base_query = HealthcareProvider.query
    
    # Add name search if provided
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
    
    # Add specialty search if provided
    if specialty:
        specialty_terms = specialty.lower().split()
        specialty_conditions = []
        for term in specialty_terms:
            # Get synonyms for the term
            synonyms = specialty_synonyms.get(term, [term])
            # Create conditions for the term and its synonyms
            term_conditions = []
            for syn in synonyms:
                term_conditions.extend([
                    HealthcareProvider.specialty.ilike(f'%{syn}%'),
                    HealthcareProvider.sub_specialty.ilike(f'%{syn}%')
                ])
            specialty_conditions.append(or_(*term_conditions))
        base_query = base_query.filter(and_(*specialty_conditions))
    
    # Add location search if provided
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
    
    # Order results by last name and first name
    results = base_query.order_by(HealthcareProvider.last_name, HealthcareProvider.first_name).all()
    
    return render_template('homepage.html', 
                         results=results, 
                         query=query,
                         name=name,
                         specialty=specialty,
                         location=location)

@app.route('/suites')
def suites():
    # Get all suites from the database
    suites = Suites.query.all()
    
    # Group entries by suite number
    suite_groups = defaultdict(lambda: {'practices': [], 'physicians': []})
    
    for suite in suites:
        if suite.suite:
            if suite.practice_name:
                suite_groups[suite.suite]['practices'].append(suite.practice_name)
            if suite.physician_name:
                suite_groups[suite.suite]['physicians'].append(suite.physician_name)
    
    # Convert to list and sort by suite number
    entries = []
    for suite, data in suite_groups.items():
        entries.append({
            'suite': suite,
            'practices': data['practices'],
            'physicians': data['physicians']
        })
    
    # Sort entries by suite number
    entries.sort(key=lambda x: int(x['suite']) if x['suite'].isdigit() else float('inf'))
    
    return render_template('suites.html', entries=entries)

@app.route('/price_data')
def price_data():
    # Get counts
    price_quotes_count = Price_quotes.query.count()
    standard_charges_count = Standard_charges.query.count()
    payers_information_count = Payers_information.query.count()
    
    # Get sample data
    price_quotes = Price_quotes.query.limit(10).all()
    standard_charges = Standard_charges.query.limit(10).all()
    payers_information = Payers_information.query.limit(10).all()
    
    return render_template('price_data.html', 
                         price_quotes_count=price_quotes_count,
                         standard_charges_count=standard_charges_count,
                         payers_information_count=payers_information_count,
                         price_quotes=price_quotes,
                         standard_charges=standard_charges,
                         payers_information=payers_information)

@app.route('/insurance_info')
def insurance_info():
    # Get search parameters
    procedure = request.args.get('procedure', '')
    code = request.args.get('code', '')
    payer = request.args.get('payer', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Build query
    query = Price_quotes.query
    
    if procedure:
        query = query.filter(Price_quotes.procedure.ilike(f'%{procedure}%'))
    
    if code:
        query = query.filter(Price_quotes.code.ilike(f'%{code}%'))
    
    if payer:
        # This is more complex as we need to join with Payers_information
        query = query.join(Standard_charges).join(Payers_information).filter(
            Payers_information.payer_name.ilike(f'%{payer}%')
        )
    
    # Get total count for pagination
    total_count = query.count()
    
    # Apply pagination
    price_quotes = query.paginate(page=page, per_page=per_page, error_out=False).items
    
    # Calculate total pages
    pages = (total_count + per_page - 1) // per_page
    
    return render_template('insurance_info.html',
                         price_quotes=price_quotes,
                         total_count=total_count,
                         page=page,
                         pages=pages)

if __name__ == '__main__':
    app.run(debug=True) 
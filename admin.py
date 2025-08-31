from flask import Flask, redirect, url_for, flash, render_template, request
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.fields import PasswordField
from models import db, HealthcareProvider, Suites, Price_quotes, Standard_charges, Payers_information
import os

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'admin.login'

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin.login'))

class HealthcareProviderView(SecureModelView):
    # List of columns to be displayed in the list view
    column_list = ['id', 'membership_status', 'nearest_facility', 'prime_privileges', 'physician_type',
                   'affiliation_status', 'specialty', 'sub_specialty', 'service_details', 'gender',
                   'first_name', 'last_name', 'middle_name', 'title', 'service_location',
                   'address', 'city', 'state', 'zip_code', 'phone', 'fax', 'preferred_provider']
    
    # Columns that can be searched from the search bar
    column_searchable_list = ['first_name', 'last_name', 'specialty', 'sub_specialty', 'service_location',
                             'address', 'city', 'state', 'zip_code', 'phone', 'fax']
    
    # Columns that can be filtered in the right sidebar
    column_filters = ['membership_status', 'nearest_facility', 'prime_privileges', 'physician_type',
                      'affiliation_status', 'specialty', 'sub_specialty', 'gender', 'city', 'state',
                      'preferred_provider']
    
    # Columns that can be sorted by clicking the header
    column_sortable_list = ['id', 'last_name', 'first_name', 'specialty', 'city', 'state']
    
    # Default sort order
    column_default_sort = ('last_name', False)
    
    # Number of entries per page
    page_size = 20

class SuitesView(SecureModelView):
    # List of columns to be displayed in the list view
    column_list = ['id', 'suite', 'physician_name', 'practice_name']
    
    # Columns that can be searched from the search bar
    column_searchable_list = ['suite', 'physician_name', 'practice_name']
    
    # Columns that can be filtered in the right sidebar
    column_filters = ['suite', 'physician_name', 'practice_name']
    
    # Columns that can be sorted by clicking the header
    column_sortable_list = ['id', 'suite', 'physician_name', 'practice_name']
    
    # Default sort order
    column_default_sort = 'suite'
    
    # Number of entries per page
    page_size = 20

class UserView(SecureModelView):
    # List of columns to be displayed in the list view
    column_list = ['id', 'username']
    
    # Exclude password hash from form
    form_excluded_columns = ['password_hash']
    
    # Columns that can be sorted by clicking the header
    column_sortable_list = ['id', 'username']
    
    # Define the form
    form_columns = ['username', 'password']
    
    # Define the form fields
    form_extra_fields = {
        'password': PasswordField('Password')
    }
    
    def on_model_change(self, form, model, is_created):
        if form.password.data:
            model.set_password(form.password.data)
    
    def create_form(self, obj=None):
        form = super(UserView, self).create_form(obj)
        if hasattr(form, 'password'):
            form.password.validators = []
        return form
    
    def edit_form(self, obj=None):
        form = super(UserView, self).edit_form(obj)
        if hasattr(form, 'password'):
            form.password.validators = []
        return form

class PriceQuotesView(SecureModelView):
    # List of columns to be displayed in the list view
    column_list = ['id', 'procedure', 'code', 'type']
    
    # Columns that can be searched from the search bar
    column_searchable_list = ['procedure', 'code', 'type']
    
    # Columns that can be filtered in the right sidebar
    column_filters = ['type']
    
    # Columns that can be sorted by clicking the header
    column_sortable_list = ['id', 'procedure', 'code', 'type']
    
    # Default sort order
    column_default_sort = 'procedure'
    
    # Number of entries per page
    page_size = 20

class StandardChargesView(SecureModelView):
    # List of columns to be displayed in the list view
    column_list = ['id', 'setting', 'minimum', 'maximum', 'price_quote_id']
    
    # Columns that can be searched from the search bar
    column_searchable_list = ['setting', 'price_quote_id']
    
    # Columns that can be filtered in the right sidebar
    column_filters = ['setting']
    
    # Columns that can be sorted by clicking the header
    column_sortable_list = ['id', 'setting', 'minimum', 'maximum']
    
    # Default sort order
    column_default_sort = 'setting'
    
    # Number of entries per page
    page_size = 20

class PayersInformationView(SecureModelView):
    # List of columns to be displayed in the list view
    column_list = ['id', 'payer_name', 'plan_name', 'standard_charge_dollar', 'estimated_amount', 'standard_charge_id']
    
    # Columns that can be searched from the search bar
    column_searchable_list = ['payer_name', 'plan_name', 'standard_charge_id']
    
    # Columns that can be filtered in the right sidebar
    column_filters = ['payer_name']
    
    # Columns that can be sorted by clicking the header
    column_sortable_list = ['id', 'payer_name', 'plan_name', 'standard_charge_dollar', 'estimated_amount']
    
    # Default sort order
    column_default_sort = 'payer_name'
    
    # Number of entries per page
    page_size = 20

def init_admin(app):
    # Initialize Flask-Admin with custom template
    admin = Admin(app, name='Healthcare Provider Admin', template_mode='bootstrap3',
                 base_template='admin/master.html')
    
    # Add model views with custom configurations
    admin.add_view(HealthcareProviderView(HealthcareProvider, db.session, name='Healthcare Providers'))
    admin.add_view(SuitesView(Suites, db.session, name='Suites'))
    admin.add_view(UserView(User, db.session, name='Users'))
    admin.add_view(PriceQuotesView(Price_quotes, db.session, name='Price Quotes'))
    admin.add_view(StandardChargesView(Standard_charges, db.session, name='Standard Charges'))
    admin.add_view(PayersInformationView(Payers_information, db.session, name='Payer Information'))
    
    # Initialize Flask-Login
    login_manager.init_app(app)
    
    # Create admin user if it doesn't exist
    # You can change the default username and password here
    DEFAULT_ADMIN_USERNAME = 'your_admin_username'  # Change this to your desired username
    DEFAULT_ADMIN_PASSWORD = 'your_secure_password'  # Change this to your desired password
    
    with app.app_context():
        if not User.query.filter_by(username=DEFAULT_ADMIN_USERNAME).first():
            admin_user = User(username=DEFAULT_ADMIN_USERNAME)
            admin_user.set_password(DEFAULT_ADMIN_PASSWORD)
            db.session.add(admin_user)
            db.session.commit() 
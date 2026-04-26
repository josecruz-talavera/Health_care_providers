from flask import Flask, redirect, url_for, flash, render_template, request
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.fields import PasswordField
from models import db, HealthcareProvider, Suites
import os

login_manager = LoginManager()
login_manager.login_view = 'admin.login'

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    
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
        return redirect(url_for('admin_login'))

class HealthcareProviderView(SecureModelView):
    column_list = ['id', 'membership_status', 'nearest_facility', 'prime_privileges', 'physician_type',
                   'affiliation_status', 'specialty', 'sub_specialty', 'service_details', 'gender',
                   'first_name', 'last_name', 'middle_name', 'title', 'service_location',
                   'address', 'city', 'state', 'zip_code', 'phone', 'fax', 'preferred_provider']
    column_searchable_list = ['first_name', 'last_name', 'specialty', 'sub_specialty', 'service_location',
                             'address', 'city', 'state', 'zip_code', 'phone', 'fax']
    column_filters = ['membership_status', 'nearest_facility', 'prime_privileges', 'physician_type',
                      'affiliation_status', 'specialty', 'sub_specialty', 'gender', 'city', 'state',
                      'preferred_provider']
    column_sortable_list = ['id', 'last_name', 'first_name', 'specialty', 'city', 'state']
    column_default_sort = ('last_name', False)
    page_size = 20

class SuitesView(SecureModelView):
    column_list = ['id', 'suite', 'physician_name', 'practice_name']
    column_searchable_list = ['suite', 'physician_name', 'practice_name']
    column_filters = ['suite', 'physician_name', 'practice_name']
    column_sortable_list = ['id', 'suite', 'physician_name', 'practice_name']
    column_default_sort = 'suite'
    page_size = 20

class UserView(SecureModelView):
    column_list = ['id', 'username']
    form_excluded_columns = ['password_hash']
    column_sortable_list = ['id', 'username']
    form_columns = ['username', 'password']
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

def init_admin(app):
    admin = Admin(app, name='Healthcare Provider Admin', template_mode='bootstrap3',
                 base_template='admin/master.html')
    
    admin.add_view(HealthcareProviderView(HealthcareProvider, db.session, name='Healthcare Providers'))
    admin.add_view(SuitesView(Suites, db.session, name='Suites'))
    admin.add_view(UserView(User, db.session, name='Users'))
    
    login_manager.init_app(app)
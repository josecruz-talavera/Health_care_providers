# Documentation

We have CSV with healthcare network data. We want to read this CSV and insert the data into
a SQLite database.

Write a computer program that accepts a filepath to the CSV file and it
processes the data.

The CSV should have the following columns:
* Membership Status
* NearestFaclity
* Prime Privileges
* Physician Type
* Affliation Status
* Specialty
* Sub Specialty
* Service Details
* Gender
* FirstName
* Last Name
* MiddleName
* Title
* Service Location (DBA)
* Address
* City
* State
* Zip
* Phone
* Fax
* Preferred Provider

Each column should map to a column in a SQLite database.

The following columns should be able to be searched via full-text.

* FirstName
* Last Name
* MiddleName
* Specialty
* Sub Specialty
* Service Location (DBA)

The command should be written in python 3.
The database schema should be specified in a SQLAlchemy model.

We're planning to add a web interface, can you rewrite the models
using the Flask-SQLAlchemy extension?

# Web interface

We want to search the healthcare network data via a web portal.
There should be a single search box that returns the results matching
all of our full-text search columns.

The design of the website should match that of typical healthcare and
hospital websites.

You can use images in the references folder for style reference.

I want to make a new model in my flask-sqlalchemy database named Suites.
Will populate this database with information from  suites-smn.xlsx sheet in this directory. 
the Suites model should contain columns:
*Suite
*Physician Name
*Practice Name

I want to create a new model in models.py named Price_quotes.
This will be a parent model to the Standard_charges model

the Price_quotes model should contain these columns:
*procedure
*code
*type
*standard_charges is the child

Standard_charges model should contain these columns:
*setting
*minimum
*maximum
*payers_information will be a child 

I want to create a child model named Payers_information that has a relationship with Standard_charges
*payer_name
*plan_name
*standard_charge_dollar
*estimated_amount
*methodology

I want to populate these 3 models:
-Price_quotes
-Standard_charges
-Payers_information

The data used to populate the models is in price_transperecy.json

can you build a program that does that?

can we add these to the web interface as insurance_info.html?
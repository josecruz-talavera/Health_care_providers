import argparse
import pandas as pd
from models import app, db, HealthcareProvider, init_db

def process_csv(csv_path, db_path):
    # Configure and initialize the database
    app.config['DATABASE_PATH'] = db_path
    init_db(app)
    
    try:
        # Read CSV file
        df = pd.read_csv(csv_path)
        
        # Rename columns to match SQLAlchemy model
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
        df = df.rename(columns=column_mapping)
        
        # Convert DataFrame to list of dictionaries
        records = df.to_dict('records')
        
        with app.app_context():
            # Insert records into database
            for record in records:
                provider = HealthcareProvider(**record)
                db.session.add(provider)
            
            # Commit the changes
            db.session.commit()
            print(f"Successfully processed {len(records)} records from {csv_path}")
        
    except Exception as e:
        print(f"Error processing CSV file: {str(e)}")
        with app.app_context():
            db.session.rollback()

def main():
    parser = argparse.ArgumentParser(description='Process healthcare provider CSV into SQLite database')
    parser.add_argument('csv_path', help='Path to the CSV file')
    parser.add_argument('--db-path', default='healthcare.db', help='Path to SQLite database (default: healthcare.db)')
    
    args = parser.parse_args()
    process_csv(args.csv_path, args.db_path)

if __name__ == '__main__':
    main() 
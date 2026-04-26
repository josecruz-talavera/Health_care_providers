import pandas as pd
from models import app, db, Suites, init_db


def process_suites_excel(excel_path, db_path):
    # Configure and initialize the database
    app.config["DATABASE_PATH"] = db_path
    init_db(app)

    try:
        # Read Excel file
        df = pd.read_excel(excel_path)

        # Rename columns to match SQLAlchemy model
        column_mapping = {
            "SUITE": "suite",
            "PHYSICIAN NAME": "physician_name",
            "PRACTICE NAME": "practice_name",
        }
        df = df.rename(columns=column_mapping)

        # Convert DataFrame to list of dictionaries
        records = df.to_dict("records")

        with app.app_context():
            # Clear existing records
            Suites.query.delete()

            # Insert records into database
            for record in records:
                # Only add records where suite is not NaN
                if pd.notna(record["suite"]):
                    suite = Suites(**record)
                    db.session.add(suite)

            # Commit the changes
            db.session.commit()
            print(f"Successfully processed {len(records)} records from {excel_path}")

    except Exception as e:
        print(f"Error processing Excel file: {str(e)}")
        with app.app_context():
            db.session.rollback()


def main():
    process_suites_excel("suites-smn.xlsx", "healthcare.db")


if __name__ == "__main__":
    main()

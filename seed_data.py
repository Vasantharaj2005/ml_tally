from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date
from models.invoice import Invoice  # Adjust this path if needed
from database import Base
from faker import Faker
import random
from sqlalchemy.exc import IntegrityError

# Use a SYNC SQLite engine just for seeding
DATABASE_URL = "sqlite:///./invoices.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

# Create tables if not exist
Base.metadata.create_all(bind=engine)

fake = Faker('en_IN')
units = ["pcs", "kg", "m", "l", "box"]
hsn_codes = ["8414", "8517", "9401", "9403", "4820", "3926", "7326", "8205", "3215", "9031"]

def generate_invoice():
    company_name = fake.company()
    buyer_details = f"{fake.name()}, {fake.city()}"
    invoice_no = f"INV-{random.randint(10000, 99999)}"  # Increased range for more uniqueness
    invoice_date = fake.date_between(start_date='-1y', end_date='today')
    vehicle_number = f"TN{random.randint(10, 99)}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.randint(1000, 9999)}"
    description = fake.sentence(nb_words=4)
    hsn_sac = random.choice(hsn_codes)
    quantity = random.randint(1, 50)
    unit = random.choice(units)
    rate = round(random.uniform(100, 5000), 2)
    status = 
    amount = round(quantity * rate, 2)
    amount_in_words = fake.numerify("Rupees Only") # Placeholder, needs a proper conversion
    gstin = fake.numerify(random.choice(['07', '27']) + 'ABCDE' + '#####F1Z' + random.choice(['5', '6']))
    return Invoice(
        company_name=company_name,
        buyer_details=buyer_details,
        invoice_no=invoice_no,
        invoice_date=invoice_date,
        vehicle_number=vehicle_number,
        description=description,
        hsn_sac=hsn_sac,
        quantity=quantity,
        unit=unit,
        rate=rate,
        amount=amount,
        amount_in_words=amount_in_words,
        gstin=gstin
    )

# Generate sample invoices
num_records = 1000
sample_invoices = [generate_invoice() for _ in range(num_records)]

# Insert into DB
def seed_data():
    session = SessionLocal()
    inserted_count = 0
    skipped_count = 0
    try:
        for invoice in sample_invoices:
            try:
                session.add(invoice)
                session.commit()
                inserted_count += 1
            except IntegrityError as e:
                session.rollback()
                if "UNIQUE constraint failed: invoices.invoice_no" in str(e):
                    skipped_count += 1
                else:
                    print("❌ An unexpected database error occurred:", e)
                    break # Stop if it's a different error
        print(f"✅ Successfully inserted {inserted_count} new records.")
        if skipped_count > 0:
            print(f"⚠️ Skipped {skipped_count} duplicate invoice numbers.")
    except Exception as e:
        session.rollback()
        print("❌ An error occurred during the seeding process:", e)
    finally:
        session.close()

if __name__ == "__main__":
    seed_data()
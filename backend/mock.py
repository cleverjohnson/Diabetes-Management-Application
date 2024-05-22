import datetime
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from faker import Faker
import random

# Assuming the model.py is already imported or available in the same directory
from model import Base, User, GlucoseRecord

# Initialize the database engine and session
engine = create_engine('sqlite:///glucose_data.db', echo=True)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
session = Session()

# Initialize Faker
fake = Faker()

# Helper functions
def generate_glucose_level(diabetes_type):
    if diabetes_type == 'Type 1':
        return round(random.uniform(70, 250), 1)  # Type 1 can have more extreme levels
    else:
        return round(random.uniform(80, 180), 1)

def generate_hba1c():
    return round(random.uniform(5.5, 10.5), 1)

def generate_medications(diabetes_type):
    if diabetes_type == 'Type 1':
        meds = ['Insulin']
    else:
        meds = ['Metformin', 'Sulfonylureas', 'DPP-4 inhibitors', 'GLP-1 receptor agonists', 'Insulin']
    return random.choice(meds)

def generate_meal_type():
    return random.choice(['Breakfast', 'Lunch', 'Dinner', 'Snack'])

def generate_exercise_details():
    return random.choice(['30 min walk', '20 min jog', '1 hour gym', '15 min yoga', 'No exercise'])

# Generate users
for _ in range(50):  # Creating 50 users
    diabetes_type = random.choice(['Type 1', 'Type 2'])
    user = User(email=fake.email(), diabetes_type=diabetes_type)
    session.add(user)
    session.commit()

    # Generate glucose records for each user
    for _ in range(100):  # Creating 100 glucose records per user
        record = GlucoseRecord(
            user_id=user.id,
            glucose_level=generate_glucose_level(diabetes_type),
            date=fake.date_time_between(start_date='-1y', end_date='now'),
            meal_type=generate_meal_type(),
            pre_or_post_meal=random.choice(['Pre-meal', 'Post-meal']),
            carbs=random.randint(0, 100),
            insulin_dose=random.randint(0, 20) if diabetes_type == 'Type 1' else random.randint(0, 10),
            medications=generate_medications(diabetes_type),
            exercise_details=generate_exercise_details(),
            symptoms=json.dumps({
                "dizziness": fake.boolean(),
                "sweating": fake.boolean(),
                "blurred_vision": fake.boolean()
            }),
            notes=fake.sentence(),
            hbA1c_levels=generate_hba1c(),
            family_history=json.dumps({
                "diabetes": fake.boolean(),
                "hypertension": fake.boolean(),
                "heart_disease": fake.boolean()
            }),
            diet_info=fake.sentence(),
            patient_outcomes=fake.sentence()
        )
        session.add(record)

session.commit()
session.close()
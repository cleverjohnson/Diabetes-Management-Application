from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'  # Corrected the attribute name
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    diabetes_type = Column(String, nullable=False)  # Add diabetes_type column
    records = relationship("GlucoseRecord", back_populates="user")

class GlucoseRecord(Base):
    __tablename__ = 'glucose_records'  # Corrected the attribute name
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    glucose_level = Column(Float, nullable=False)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    meal_type = Column(String)
    pre_or_post_meal = Column(String)
    carbs = Column(Integer)
    insulin_dose = Column(Integer)
    medications = Column(String)
    exercise_details = Column(String)
    symptoms = Column(Text)  # Store as JSON string
    notes = Column(Text)
    hbA1c_levels = Column(Float)
    family_history = Column(Text)  # Store as JSON string
    diet_info = Column(Text)
    patient_outcomes = Column(Text)

    user = relationship("User", back_populates="records")

User.records = relationship("GlucoseRecord", order_by=GlucoseRecord.id, back_populates="user")

# Create an engine that stores data in the local directory's
engine = create_engine('sqlite:///glucose_data.db', echo=True)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

Base.metadata.create_all(engine)
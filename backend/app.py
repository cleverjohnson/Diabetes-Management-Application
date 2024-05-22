from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy.orm import scoped_session, sessionmaker
from datetime import datetime
import json
import os
import stripe
import openai

# Import your SQLAlchemy models
from model import Base, engine, Session, User, GlucoseRecord

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///glucose_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

stripe.api_key = 'sk_test_51PHTBGRoLiyx8hB5KWLCBAppD0OvZ1W9PALFIHtGMVIL7bBjrT0ZS3Hs4WotcUFUnLjCNMKlooJbMNJBf7yDqxVk00GYntEsgc'
openai.api_key = os.getenv("OPENAI_API_KEY")

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

def parse_iso_datetime(date_str):
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        if len(date_str.split(':')) == 2:
            date_str += ':00'
        return datetime.fromisoformat(date_str)

def record_to_fhir(record):
    return {
        "resourceType": "Observation",
        "id": str(record.id),
        "status": "final",
        "category": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                        "code": "laboratory",
                        "display": "Laboratory"
                    }
                ]
            }
        ],
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "15074-8",
                    "display": "Glucose [Moles/volume] in Blood"
                }
            ]
        },
        "subject": {
            "reference": f"User/{record.user_id}"
        },
        "effectiveDateTime": record.date.isoformat(),
        "valueQuantity": {
            "value": record.glucose_level,
            "unit": "mg/dL",
            "system": "http://unitsofmeasure.org",
            "code": "mg/dL"
        },
        "note": [
            {
                "text": record.notes
            }
        ],
        "meal_type": record.meal_type,
        "pre_or_post_meal": record.pre_or_post_meal,
        "carbs": record.carbs,
        "insulin_dose": record.insulin_dose,
        "medications": record.medications,
        "exercise_details": record.exercise_details,
        "symptoms": json.loads(record.symptoms) if record.symptoms else [],
        "hbA1c_levels": record.hbA1c_levels,
        "family_history": json.loads(record.family_history) if record.family_history else [],
        "diet_info": record.diet_info,
        "patient_outcomes": record.patient_outcomes
    }

def fhir_to_record(data):
    return GlucoseRecord(
        user_id=1,  # Assuming a user_id of 1 for demonstration purposes
        glucose_level=data['valueQuantity']['value'],
        date=parse_iso_datetime(data['effectiveDateTime']),
        meal_type=data['meal_type'],
        pre_or_post_meal=data['pre_or_post_meal'],
        carbs=data['carbs'],
        insulin_dose=data['insulin_dose'],
        medications=data['medications'],
        exercise_details=data['exercise_details'],
        symptoms=json.dumps(data['symptoms']),
        notes=data['note'][0]['text'],
        hbA1c_levels=data['hbA1c_levels'],
        family_history=json.dumps(data['family_history']),
        diet_info=data['diet_info'],
        patient_outcomes=data['patient_outcomes']
    )


@app.route('/add_glucose_record', methods=['POST'])
def add_glucose_record():
    session = Session()
    data = request.json
    app.logger.info("Received data: %s", data)
    
    try:
        record = fhir_to_record(data)
        session.add(record)
        session.commit()
        return jsonify({'message': 'Record added successfully!'}), 201
    except Exception as e:
        session.rollback()
        app.logger.error('Failed to add record: %s', str(e))
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@app.route('/delete_glucose_record/<int:record_id>', methods=['DELETE'])
def delete_glucose_record(record_id):
    session = Session()
    record = session.query(GlucoseRecord).filter_by(id=record_id).first()
    if not record:
        return jsonify({'error': 'Record not found'}), 404

    try:
        session.delete(record)
        session.commit()
        return jsonify({'message': 'Record deleted successfully!'}), 200
    except Exception as e:
        session.rollback()
        app.logger.error('Failed to delete record: %s', str(e))
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@app.route('/get_glucose_records', methods=['GET'])
def get_glucose_records():
    session = Session()
    limit = request.args.get('limit', default=500, type=int)
    try:
        records = session.query(GlucoseRecord).limit(limit).all()
        return jsonify([record_to_fhir(record) for record in records]), 200
    except Exception as e:
        app.logger.error('Failed to fetch records: %s', str(e))
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@app.route('/update_glucose_record/<int:record_id>', methods=['PUT'])
def update_glucose_record(record_id):
    session = Session()
    data = request.json
    record = session.query(GlucoseRecord).filter_by(id=record_id).first()
    if not record:
        return jsonify({'error': 'Record not found'}), 404
    
    try:
        updated_record = fhir_to_record(data)
        record.glucose_level = updated_record.glucose_level
        record.date = updated_record.date
        record.meal_type = updated_record.meal_type
        record.pre_or_post_meal = updated_record.pre_or_post_meal
        record.carbs = updated_record.carbs
        record.insulin_dose = updated_record.insulin_dose
        record.medications = updated_record.medications
        record.exercise_details = updated_record.exercise_details
        record.symptoms = updated_record.symptoms
        record.notes = updated_record.notes
        record.hbA1c_levels = updated_record.hbA1c_levels
        record.family_history = updated_record.family_history
        record.diet_info = updated_record.diet_info
        record.patient_outcomes = updated_record.patient_outcomes

        session.commit()
        return jsonify({'message': 'Record updated successfully!'}), 200
    except Exception as e:
        session.rollback()
        app.logger.error('Failed to update record: %s', str(e))
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

if __name__ == '__main__':
    app.run(debug=True)
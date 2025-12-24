import os
import logging
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
import bcrypt
from datetime import datetime
import joblib
import numpy as np

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL') or 'sqlite:///pravartak.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# SQLite doesn't support connection pooling, so we remove these options for SQLite
if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
    app.config.pop('SQLALCHEMY_ENGINE_OPTIONS', None)
else:
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 10,
        'max_overflow': 20,
        'pool_recycle': 1800,  # Recycle connections after 30 minutes
    }
app.config['SECRET_KEY'] = os.urandom(24)

db = SQLAlchemy(app)

# Database Models
class Mentor(db.Model):
    __tablename__ = 'mentors'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    expertise = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    students = db.relationship('Student', backref='mentor', lazy=True)

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    roll_no = db.Column(db.String(20))
    gender = db.Column(db.String(10))
    category = db.Column(db.String(50))
    fees_status = db.Column(db.String(20))
    attendance = db.Column(db.Float)
    marks = db.Column(db.Float)
    backlog = db.Column(db.Integer)
    dropout_risk = db.Column(db.Boolean, default=False)
    mentor_id = db.Column(db.Integer, db.ForeignKey('mentors.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Load ML model with error handling
try:
    model_path = os.getenv('RISK_MODEL_PATH')
    risk_model = joblib.load(model_path)
    logger.info("✅ Model loaded successfully!")
except Exception as e:
    logger.error(f"❌ Error loading model: {e}")
    risk_model = None

# Helper functions
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(password, password_hash):
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

# API Routes
@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if Mentor.query.filter_by(email=data['email']).first():
            return jsonify({"message": "Email already registered"}), 400
        
        new_mentor = Mentor(
            full_name=data['fullName'],
            email=data['email'],
            password_hash=hash_password(data['password']).decode('utf-8'),
            expertise=data['expertise']
        )
        
        db.session.add(new_mentor)
        db.session.commit()
        
        return jsonify({"message": "Registration successful"}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 400

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        mentor = Mentor.query.filter_by(email=data['email']).first()
        
        if mentor and check_password(data['password'], mentor.password_hash):
            return jsonify({
                "id": mentor.id,
                "fullName": mentor.full_name,
                "email": mentor.email,
                "expertise": mentor.expertise
            }), 200
        
        return jsonify({"message": "Invalid credentials"}), 401
    
    except Exception as e:
        return jsonify({"message": str(e)}), 400


@app.route('/api/students', methods=['GET'])
def get_students():
    try:
        mentor_id = request.args.get('mentor_id')
        students = Student.query.filter_by(mentor_id=mentor_id).all()
        
        return jsonify([{
            "id": s.id,
            "fullName": s.full_name,
            "email": s.email,
            "rollNo": s.roll_no,
            "gender": s.gender,
            "category": s.category,
            "feesStatus": s.fees_status,
            "attendance": s.attendance,
            "marks": s.marks,
            "backlog": s.backlog,
            "dropoutRisk": s.dropout_risk
        } for s in students]), 200
    
    except Exception as e:
        return jsonify({"message": str(e)}), 400

@app.route('/api/students/<int:id>', methods=['GET'])
def get_student(id):
    try:
        student = Student.query.get_or_404(id)
        
        return jsonify({
            "id": student.id,
            "fullName": student.full_name,
            "email": student.email,
            "rollNo": student.roll_no,
            "gender": student.gender,
            "category": student.category,
            "feesStatus": student.fees_status,
            "attendance": student.attendance,
            "marks": student.marks,
            "backlog": student.backlog,
            "dropoutRisk": student.dropout_risk
        }), 200
    
    except Exception as e:
        return jsonify({"message": str(e)}), 400

@app.route('/api/students', methods=['POST'])
def add_student():
    try:
        data = request.get_json()
        
        if Student.query.filter_by(email=data['email']).first():
            return jsonify({"message": "Email already registered"}), 400
        
        # Predict risk before saving
        features = np.array([[
            data['attendance'],
            data['marks'],
            data['backlog'],
            1 if data['gender'].lower() == 'male' else 0
        ]])
        
        risk_prediction = risk_model.predict(features)[0] if risk_model else False
        
        new_student = Student(
            full_name=data['fullName'],
            email=data['email'],
            roll_no=data['rollNo'],
            gender=data['gender'],
            category=data['category'],
            fees_status=data['feesStatus'],
            attendance=data['attendance'],
            marks=data['marks'],
            backlog=data['backlog'],
            dropout_risk=bool(risk_prediction),
            mentor_id=data['mentorId']
        )
        
        db.session.add(new_student)
        db.session.commit()
        
        return jsonify({
            "id": new_student.id,
            "full_name": new_student.full_name,
            "email": new_student.email,
            "roll_no": new_student.roll_no,
            "gender": new_student.gender,
            "category": new_student.category,
            "fees_status": new_student.fees_status,
            "attendance": new_student.attendance,
            "marks": new_student.marks,
            "backlog": new_student.backlog,
            "dropout_risk": bool(new_student.dropout_risk),
            "mentor_id": new_student.mentor_id,
            "message": "Student added successfully",
            "dropoutRisk": bool(risk_prediction)
        }), 201
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding student: {str(e)}")
        return jsonify({"message": f"Error adding student: {str(e)}"}), 400

@app.route('/api/predict', methods=['POST'])
def predict_risk():
    try:
        if risk_model is None:
            return jsonify({"message": "Risk model not available"}), 503
        
        data = request.get_json()
        
        features = np.array([[
            data['attendance'],
            data['marks'],
            data['backlog'],
            1 if data['gender'].lower() == 'male' else 0
        ]])
        
        # Debug: Print feature shape and values
        logger.info(f"Features shape: {features.shape}")
        logger.info(f"Features values: {features}")
        
        risk_prediction = risk_model.predict(features)[0]
        
        return jsonify({
            "dropoutRisk": bool(risk_prediction),
            "message": "High risk of dropout" if risk_prediction else "Low risk of dropout"
        }), 200
    
    except Exception as e:
        print(f"Prediction error: {e}")
        return jsonify({"message": str(e)}), 400

def create_test_accounts():
    with app.app_context():
        # Check if test accounts already exist
        if not Mentor.query.first():
            # Create test mentor accounts
            test_mentors = [
                {
                    "full_name": "Dr. Sarah Johnson",
                    "email": "sarah.johnson@example.com",
                    "password": "password123",
                    "expertise": "Computer Science"
                },
                {
                    "full_name": "Prof. Michael Chen",
                    "email": "michael.chen@example.com",
                    "password": "password123",
                    "expertise": "Mathematics"
                },
                {
                    "full_name": "Dr. Emily Rodriguez",
                    "email": "emily.rodriguez@example.com",
                    "password": "password123",
                    "expertise": "Physics"
                }
            ]
            
            for mentor_data in test_mentors:
                # Hash password
                hashed_password = bcrypt.hashpw(mentor_data["password"].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                
                # Create mentor
                mentor = Mentor(
                    full_name=mentor_data["full_name"],
                    email=mentor_data["email"],
                    password_hash=hashed_password,
                    expertise=mentor_data["expertise"]
                )
                
                db.session.add(mentor)
            
            db.session.commit()
            logger.info("✅ Test mentor accounts created successfully!")
        else:
            logger.info("ℹ️ Test mentor accounts already exist")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_test_accounts()
        logger.info("✅ Database tables created successfully!")
    app.run(debug=True)



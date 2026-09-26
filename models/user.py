from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from models import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'hr' or 'candidate'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    hr_profile = db.relationship('HRProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    candidate_profile = db.relationship('CandidateProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    jobs = db.relationship('Job', backref='hr_user', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


class HRProfile(db.Model):
    __tablename__ = 'hr_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    full_name = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), default='Human Resources')

    def __repr__(self):
        return f"<HRProfile {self.full_name} at {self.company}>"


class CandidateProfile(db.Model):
    __tablename__ = 'candidate_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    education = db.Column(db.String(100), nullable=True)
    experience_years = db.Column(db.Integer, default=0)
    resume_filename = db.Column(db.String(255), nullable=True)
    resume_text = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Skills relationship via candidate_skills
    skills = db.relationship('Skill', secondary='candidate_skills', backref=db.backref('candidates', lazy='dynamic'))
    applications = db.relationship('Application', backref='candidate', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<CandidateProfile {self.full_name}>"

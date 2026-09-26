from datetime import datetime
from models import db

# Association Table for Job & Skill
job_skills = db.Table(
    'job_skills',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('job_id', db.Integer, db.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False),
    db.Column('skill_id', db.Integer, db.ForeignKey('skills.id', ondelete='CASCADE'), nullable=False),
    db.UniqueConstraint('job_id', 'skill_id', name='unique_job_skill')
)

class Skill(db.Model):
    __tablename__ = 'skills'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False, index=True)
    category = db.Column(db.String(50), default='Technical')

    def __repr__(self):
        return f"<Skill {self.name}>"


class Job(db.Model):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    hr_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    required_skills_text = db.Column(db.Text, nullable=False)
    min_qualification = db.Column(db.String(100), nullable=False)
    min_experience_years = db.Column(db.Integer, default=0, nullable=False)
    location = db.Column(db.String(100), default='Remote')
    status = db.Column(db.String(20), default='Open') # 'Open' or 'Closed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Skills relationship
    hr = db.relationship('User', backref=db.backref('jobs_posted', lazy=True))
    skills = db.relationship('Skill', secondary=job_skills, backref=db.backref('jobs', lazy='dynamic'))
    applications = db.relationship('Application', backref='job', cascade='all, delete-orphan')

    def get_skill_names(self):
        if self.skills:
            return [s.name for s in self.skills]
        return [s.strip() for s in self.required_skills_text.split(',') if s.strip()]

    def __repr__(self):
        return f"<Job {self.title}>"

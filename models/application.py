from datetime import datetime
from models import db

candidate_skills = db.Table(
    'candidate_skills',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('candidate_id', db.Integer, db.ForeignKey('candidate_profiles.id', ondelete='CASCADE'), nullable=False),
    db.Column('skill_id', db.Integer, db.ForeignKey('skills.id', ondelete='CASCADE'), nullable=False),
    db.UniqueConstraint('candidate_id', 'skill_id', name='unique_cand_skill')
)

class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate_profiles.id', ondelete='CASCADE'), nullable=False)
    match_score = db.Column(db.Float, default=0.0, nullable=False)
    skill_score = db.Column(db.Float, default=0.0, nullable=False)
    exp_score = db.Column(db.Float, default=0.0, nullable=False)
    edu_score = db.Column(db.Float, default=0.0, nullable=False)
    status = db.Column(db.String(30), default='Applied') # 'Applied', 'Reviewing', 'Shortlisted', 'Rejected'
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('job_id', 'candidate_id', name='unique_job_candidate'),
    )

    def __repr__(self):
        return f"<Application Candidate {self.candidate_id} -> Job {self.job_id} ({self.match_score}%)>"

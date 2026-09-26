import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from werkzeug.utils import secure_filename
from functools import wraps
from models import db
from models.user import CandidateProfile
from models.job import Job, Skill
from models.application import Application
from services.resume_parser import extract_resume_text
from services.skill_extractor import extract_skills_from_text, extract_education_from_text, extract_experience_years_from_text
from services.candidate_matcher import calculate_comprehensive_match

candidate_bp = Blueprint('candidate', __name__, url_prefix='/candidate')

def candidate_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'candidate':
            flash('Access restricted to Candidates only.', 'danger')
            return redirect(url_for('auth.candidate_login'))
        return f(*args, **kwargs)
    return decorated_function


@candidate_bp.route('/dashboard')
@candidate_required
def dashboard():
    cand_profile = CandidateProfile.query.filter_by(user_id=session['user_id']).first()
    
    # Open job openings
    open_jobs = Job.query.filter_by(status='Open').all()
    
    # Candidate applications dict job_id -> application
    cand_applications = {app.job_id: app for app in cand_profile.applications} if cand_profile else {}

    return render_template(
        'candidate/dashboard.html',
        profile=cand_profile,
        jobs=open_jobs,
        applications=cand_applications
    )


@candidate_bp.route('/profile', methods=['GET', 'POST'])
@candidate_required
def profile():
    cand_profile = CandidateProfile.query.filter_by(user_id=session['user_id']).first()
    
    if request.method == 'POST':
        cand_profile.full_name = request.form.get('full_name', '').strip()
        cand_profile.phone = request.form.get('phone', '').strip()
        cand_profile.education = request.form.get('education', 'B.Tech').strip()
        try:
            cand_profile.experience_years = int(request.form.get('experience_years', '0'))
        except ValueError:
            cand_profile.experience_years = 0

        # Optional manual skill addition
        manual_skills = request.form.get('manual_skills', '').strip()
        if manual_skills:
            skill_names = [s.strip() for s in manual_skills.split(',') if s.strip()]
            for sname in skill_names:
                skill = Skill.query.filter_by(name=sname).first()
                if not skill:
                    skill = Skill(name=sname)
                    db.session.add(skill)
                    db.session.flush()
                if skill not in cand_profile.skills:
                    cand_profile.skills.append(skill)

        # Process Resume Upload if file attached
        if 'resume_file' in request.files and request.files['resume_file'].filename != '':
            file = request.files['resume_file']
            ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
            
            if ext not in current_app.config['ALLOWED_EXTENSIONS']:
                flash('Invalid file format! Only PDF (.pdf) and Word DOCX (.docx) resumes are allowed.', 'danger')
                return render_template('candidate/profile.html', profile=cand_profile)

            filename = secure_filename(f"user_{session['user_id']}_{file.filename}")
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            
            # Ensure upload directory exists
            os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(upload_path)

            try:
                # Extract text
                resume_text = extract_resume_text(upload_path)
                cand_profile.resume_filename = filename
                cand_profile.resume_text = resume_text

                # Auto Extract Skills & Metadata via NLP
                extracted_skill_names = extract_skills_from_text(resume_text)
                detected_education = extract_education_from_text(resume_text)
                detected_exp = extract_experience_years_from_text(resume_text)

                if detected_education and cand_profile.education == 'B.Tech':
                    cand_profile.education = detected_education
                if detected_exp and cand_profile.experience_years == 0:
                    cand_profile.experience_years = detected_exp

                # Sync extracted skills to candidate profile
                for sname in extracted_skill_names:
                    skill = Skill.query.filter_by(name=sname).first()
                    if not skill:
                        skill = Skill(name=sname)
                        db.session.add(skill)
                        db.session.flush()
                    if skill not in cand_profile.skills:
                        cand_profile.skills.append(skill)

                # Recalculate match score for candidate's applications
                for app in cand_profile.applications:
                    match_res = calculate_comprehensive_match(app.job, cand_profile)
                    app.match_score = match_res['match_score']
                    app.skill_score = match_res['skill_score']
                    app.exp_score = match_res['exp_score']
                    app.edu_score = match_res['edu_score']

                flash(f'Resume processed successfully! {len(extracted_skill_names)} skills automatically identified.', 'success')

            except Exception as e:
                flash(f'Error processing resume file: {str(e)}', 'warning')

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('candidate.profile'))

    return render_template('candidate/profile.html', profile=cand_profile)


@candidate_bp.route('/apply/<int:job_id>', methods=['GET', 'POST'])
@candidate_required
def apply_job(job_id):
    job = Job.query.get_or_404(job_id)
    cand_profile = CandidateProfile.query.filter_by(user_id=session['user_id']).first()

    existing_app = Application.query.filter_by(job_id=job.id, candidate_id=cand_profile.id).first()
    if existing_app:
        flash(f'You have already submitted an application for "{job.title}".', 'info')
        return redirect(url_for('candidate.dashboard'))

    if request.method == 'POST':
        # 1. Update Candidate Info from Application Form
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        education = request.form.get('education', 'B.Tech').strip()
        exp_input = request.form.get('experience_years', '0').strip()

        if full_name:
            cand_profile.full_name = full_name
        if phone:
            cand_profile.phone = phone
        cand_profile.education = education
        try:
            cand_profile.experience_years = int(exp_input)
        except ValueError:
            pass

        # 2. Process Resume File if uploaded directly in Application Form
        if 'resume_file' in request.files and request.files['resume_file'].filename != '':
            file = request.files['resume_file']
            ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''

            if ext not in current_app.config['ALLOWED_EXTENSIONS']:
                flash('Invalid resume file format! Only PDF (.pdf) and Word DOCX (.docx) files are allowed.', 'danger')
                return render_template('candidate/apply.html', job=job, profile=cand_profile)

            filename = secure_filename(f"user_{session['user_id']}_{file.filename}")
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(upload_path)

            try:
                resume_text = extract_resume_text(upload_path)
                cand_profile.resume_filename = filename
                cand_profile.resume_text = resume_text

                # Auto Extract Skills via NLP
                extracted_skill_names = extract_skills_from_text(resume_text)
                for sname in extracted_skill_names:
                    skill = Skill.query.filter_by(name=sname).first()
                    if not skill:
                        skill = Skill(name=sname)
                        db.session.add(skill)
                        db.session.flush()
                    if skill not in cand_profile.skills:
                        cand_profile.skills.append(skill)
            except Exception as e:
                flash(f'Warning parsing resume file: {str(e)}', 'warning')

        # Guarantee a resume exists before completing application
        if not cand_profile.resume_filename:
            flash('A valid PDF or DOCX resume file is required to submit your job application.', 'danger')
            return render_template('candidate/apply.html', job=job, profile=cand_profile)

        db.session.commit()

        # 3. Calculate Comprehensive Screening Match Score
        match_result = calculate_comprehensive_match(job, cand_profile)

        new_application = Application(
            job_id=job.id,
            candidate_id=cand_profile.id,
            match_score=match_result['match_score'],
            skill_score=match_result['skill_score'],
            exp_score=match_result['exp_score'],
            edu_score=match_result['edu_score'],
            status='Applied'
        )
        db.session.add(new_application)
        db.session.commit()

        flash(f'Application submitted successfully for "{job.title}"! Automated screening match: {match_result["match_score"]}%.', 'success')
        return redirect(url_for('candidate.dashboard'))

    return render_template('candidate/apply.html', job=job, profile=cand_profile)

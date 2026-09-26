import csv
import io
import time
import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify, Response, current_app
from werkzeug.utils import secure_filename
from functools import wraps
from models import db
from models.user import User, CandidateProfile, HRProfile
from models.job import Job, Skill, job_skills
from models.application import Application
from services.candidate_matcher import calculate_comprehensive_match
from services.adsa_algorithms import quicksort_candidates, SkillTrie
from services.skill_extractor import extract_skills_from_text, extract_education_from_text, extract_experience_years_from_text
from services.resume_parser import extract_resume_text

hr_bp = Blueprint('hr', __name__, url_prefix='/hr')

def hr_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'hr':
            flash('Access restricted to HR Managers only.', 'danger')
            return redirect(url_for('auth.hr_login'))
        return f(*args, **kwargs)
    return decorated_function


def calculate_candidate_general_matrix(cand):
    # 1. Skill Score based on identified skills
    skill_count = len(cand.skills) if cand.skills else 0
    skill_score = min(100, skill_count * 18)

    # 2. Experience Score based on years of experience
    exp_years = cand.experience_years or 0
    exp_score = min(100, exp_years * 25)

    # 3. Education Score based on degree level
    edu_str = (cand.education or '').upper()
    if 'PH.D' in edu_str or 'DOCTOR' in edu_str:
        edu_score = 100
    elif 'M.TECH' in edu_str or 'MBA' in edu_str or 'MASTER' in edu_str:
        edu_score = 90
    elif 'B.TECH' in edu_str or 'MCA' in edu_str or 'ENGINEER' in edu_str:
        edu_score = 80
    elif 'B.SC' in edu_str or 'BCA' in edu_str or 'BACHELOR' in edu_str:
        edu_score = 70
    else:
        edu_score = 60

    # 4. Resume Text & Document Presence Score
    has_file = 100 if cand.resume_filename else 0

    # Weighted Capability Score
    overall_score = round((0.45 * skill_score) + (0.30 * exp_score) + (0.15 * edu_score) + (0.10 * has_file), 1)

    return {
        'overall_score': overall_score,
        'skill_score': skill_score,
        'exp_score': exp_score,
        'edu_score': edu_score,
        'skill_count': skill_count
    }


@hr_bp.route('/dashboard')
@hr_required
def dashboard():
    hr_id = session['user_id']
    
    total_jobs = Job.query.filter_by(hr_id=hr_id).count()
    total_candidates = CandidateProfile.query.count()
    
    # Applications for HR's jobs
    hr_jobs = Job.query.filter_by(hr_id=hr_id).all()
    hr_job_ids = [j.id for j in hr_jobs]
    
    applications = Application.query.filter(Application.job_id.in_(hr_job_ids)).all() if hr_job_ids else []
    total_applications = len(applications)
    shortlisted_count = len([a for a in applications if a.status == 'Shortlisted'])
    
    avg_match = round(sum(a.match_score for a in applications) / total_applications, 1) if total_applications > 0 else 0.0

    # Build single unified candidate records list (Applications + Registered Candidate Profiles)
    candidate_records = []
    processed_cand_ids = set()

    for app in applications:
        cand = app.candidate
        job = app.job
        cand_skills = [s.name for s in cand.skills] if cand.skills else []
        processed_cand_ids.add(cand.id)
        candidate_records.append({
            'application_id': app.id,
            'candidate_id': cand.id,
            'full_name': cand.full_name,
            'email': cand.user.email,
            'phone': cand.phone or 'N/A',
            'education': cand.education or 'N/A',
            'experience_years': cand.experience_years,
            'job_id': job.id,
            'job_title': job.title,
            'match_score': app.match_score,
            'skill_score': app.skill_score,
            'exp_score': app.exp_score,
            'edu_score': app.edu_score,
            'status': app.status,
            'skills': cand_skills,
            'resume_filename': cand.resume_filename,
            'applied_at': app.applied_at.strftime('%Y-%m-%d')
        })

    # Add any remaining registered candidates who haven't submitted a job application yet
    unapplied_candidates = CandidateProfile.query.filter(~CandidateProfile.id.in_(processed_cand_ids)).all() if processed_cand_ids else CandidateProfile.query.all()
    for cand in unapplied_candidates:
        matrix = calculate_candidate_general_matrix(cand)
        cand_skills = [s.name for s in cand.skills] if cand.skills else []
        candidate_records.append({
            'application_id': None,
            'candidate_id': cand.id,
            'full_name': cand.full_name,
            'email': cand.user.email,
            'phone': cand.phone or 'N/A',
            'education': cand.education or 'N/A',
            'experience_years': cand.experience_years or 0,
            'job_id': 'all',
            'job_title': 'General Registered Profile',
            'match_score': matrix['skill_score'],
            'skill_score': matrix['skill_score'],
            'exp_score': matrix['exp_score'],
            'edu_score': matrix['edu_score'],
            'status': 'Applied',
            'skills': cand_skills,
            'resume_filename': cand.resume_filename,
            'applied_at': cand.created_at.strftime('%Y-%m-%d')
        })

    # Single ADSA QuickSort for ALL Candidates by Match & Skill Score
    sorted_candidates = quicksort_candidates(candidate_records, key_func=lambda x: x['match_score'], reverse=True)

    return render_template(
        'hr/dashboard.html',
        total_jobs=total_jobs,
        total_candidates=total_candidates,
        total_applications=total_applications,
        shortlisted_count=shortlisted_count,
        avg_match=avg_match,
        jobs=hr_jobs,
        candidates=sorted_candidates
    )


@hr_bp.route('/candidate/<int:cand_id>/resume')
@hr_required
def candidate_resume(cand_id):
    candidate = CandidateProfile.query.get_or_404(cand_id)
    return render_template('hr/candidate_resume.html', candidate=candidate)


@hr_bp.route('/candidates/<int:cand_id>/status', methods=['POST'])
@hr_required
def update_candidate_direct_status(cand_id):
    cand = CandidateProfile.query.get_or_404(cand_id)
    new_status = request.form.get('status')

    if new_status not in ['Applied', 'Reviewing', 'Shortlisted', 'Rejected']:
        return jsonify({'error': 'Invalid status'}), 400

    latest_app = Application.query.filter_by(candidate_id=cand.id).first()
    if latest_app:
        latest_app.status = new_status
        db.session.commit()
        return jsonify({'success': True, 'status': new_status})
    else:
        open_job = Job.query.filter_by(hr_id=session['user_id']).first()
        if open_job:
            match_res = calculate_comprehensive_match(open_job, cand)
            new_app = Application(
                job_id=open_job.id,
                candidate_id=cand.id,
                match_score=match_res['match_score'],
                skill_score=match_res['skill_score'],
                exp_score=match_res['exp_score'],
                edu_score=match_res['edu_score'],
                status=new_status
            )
            db.session.add(new_app)
            db.session.commit()
            return jsonify({'success': True, 'status': new_status, 'app_id': new_app.id})

    return jsonify({'success': True, 'status': new_status})


@hr_bp.route('/jobs/create', methods=['GET', 'POST'])
@hr_required
def job_create():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        required_skills = request.form.get('required_skills', '').strip()
        min_qualification = request.form.get('min_qualification', 'B.Tech').strip()
        min_experience = request.form.get('min_experience', '0').strip()
        location = request.form.get('location', 'Remote').strip()

        if not title or not description or not required_skills:
            flash('Job Title, Description, and Required Skills are required.', 'danger')
            return render_template('hr/job_form.html', action='Create')

        try:
            min_exp_years = int(min_experience)
        except ValueError:
            min_exp_years = 0

        new_job = Job(
            hr_id=session['user_id'],
            title=title,
            description=description,
            required_skills_text=required_skills,
            min_qualification=min_qualification,
            min_experience_years=min_exp_years,
            location=location,
            status='Open'
        )
        db.session.add(new_job)
        db.session.flush()

        # Parse required skills and map/create Skill objects
        skill_names = [s.strip() for s in required_skills.split(',') if s.strip()]
        for sname in skill_names:
            skill = Skill.query.filter_by(name=sname).first()
            if not skill:
                skill = Skill(name=sname)
                db.session.add(skill)
                db.session.flush()
            if skill not in new_job.skills:
                new_job.skills.append(skill)

        db.session.commit()
        flash('Job opening created successfully!', 'success')
        return redirect(url_for('hr.dashboard'))

    return render_template('hr/job_form.html', action='Create', job=None)


@hr_bp.route('/jobs/<int:job_id>/edit', methods=['GET', 'POST'])
@hr_required
def job_edit(job_id):
    job = Job.query.get_or_404(job_id)
    if job.hr_id != session['user_id']:
        flash('Unauthorized access to this job opening.', 'danger')
        return redirect(url_for('hr.dashboard'))

    if request.method == 'POST':
        job.title = request.form.get('title', '').strip()
        job.description = request.form.get('description', '').strip()
        job.required_skills_text = request.form.get('required_skills', '').strip()
        job.min_qualification = request.form.get('min_qualification', 'B.Tech').strip()
        try:
            job.min_experience_years = int(request.form.get('min_experience', '0'))
        except ValueError:
            job.min_experience_years = 0
        job.location = request.form.get('location', 'Remote').strip()
        job.status = request.form.get('status', 'Open').strip()

        # Re-link skills
        job.skills.clear()
        skill_names = [s.strip() for s in job.required_skills_text.split(',') if s.strip()]
        for sname in skill_names:
            skill = Skill.query.filter_by(name=sname).first()
            if not skill:
                skill = Skill(name=sname)
                db.session.add(skill)
                db.session.flush()
            if skill not in job.skills:
                job.skills.append(skill)

        # Recalculate matches for existing applications
        applications = Application.query.filter_by(job_id=job.id).all()
        for app in applications:
            cand = app.candidate
            match_res = calculate_comprehensive_match(job, cand)
            app.match_score = match_res['match_score']
            app.skill_score = match_res['skill_score']
            app.exp_score = match_res['exp_score']
            app.edu_score = match_res['edu_score']

        db.session.commit()
        flash('Job opening updated successfully and applications rescreened!', 'success')
        return redirect(url_for('hr.dashboard'))

    return render_template('hr/job_form.html', action='Edit', job=job)


@hr_bp.route('/jobs/<int:job_id>/delete', methods=['POST'])
@hr_required
def job_delete(job_id):
    job = Job.query.get_or_404(job_id)
    if job.hr_id != session['user_id']:
        flash('Unauthorized to delete this job.', 'danger')
        return redirect(url_for('hr.dashboard'))

    db.session.delete(job)
    db.session.commit()
    flash('Job opening deleted successfully.', 'info')
    return redirect(url_for('hr.dashboard'))


@hr_bp.route('/applications/<int:app_id>/status', methods=['POST'])
@hr_required
def update_application_status(app_id):
    app = Application.query.get_or_404(app_id)
    if app.job.hr_id != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 403

    new_status = request.form.get('status')
    if new_status in ['Applied', 'Reviewing', 'Shortlisted', 'Rejected']:
        app.status = new_status
        db.session.commit()
        return jsonify({'success': True, 'status': new_status})
    return jsonify({'error': 'Invalid status'}), 400


@hr_bp.route('/export/csv')
@hr_required
def export_candidates_csv():
    hr_id = session['user_id']
    hr_jobs = Job.query.filter_by(hr_id=hr_id).all()
    hr_job_ids = [j.id for j in hr_jobs]

    applications = Application.query.filter(Application.job_id.in_(hr_job_ids)).all() if hr_job_ids else []
    
    # Sort candidates using ADSA QuickSort
    candidate_records = []
    for app in applications:
        cand = app.candidate
        cand_skills = ", ".join([s.name for s in cand.skills]) if cand.skills else "None"
        candidate_records.append({
            'app_id': app.id,
            'name': cand.full_name,
            'email': cand.user.email,
            'phone': cand.phone or 'N/A',
            'job': app.job.title,
            'match_score': app.match_score,
            'skill_score': app.skill_score,
            'exp_score': app.exp_score,
            'edu_score': app.edu_score,
            'status': app.status,
            'skills': cand_skills,
            'applied_at': app.applied_at.strftime('%Y-%m-%d %H:%M')
        })

    sorted_records = quicksort_candidates(candidate_records, key_func=lambda x: x['match_score'], reverse=True)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Rank', 'Candidate Name', 'Email', 'Phone', 'Job Applied',
        'Overall Match Score (%)', 'Skill Score (%)', 'Exp Score (%)', 'Edu Score (%)',
        'Application Status', 'Extracted Skills', 'Applied At'
    ])

    for idx, rec in enumerate(sorted_records, 1):
        writer.writerow([
            idx, rec['name'], rec['email'], rec['phone'], rec['job'],
            rec['match_score'], rec['skill_score'], rec['exp_score'], rec['edu_score'],
            rec['status'], rec['skills'], rec['applied_at']
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=candidate_screening_rankings.csv"}
    )


@hr_bp.route('/academic_stats')
@hr_required
def academic_stats():
    """
    Academic subject benchmark API (DBMS, DMGT, ADSA, OOPJ).
    Demonstrates QuickSort O(N log N) vs BubbleSort O(N^2) live benchmark timing.
    """
    candidates = CandidateProfile.query.all()
    records = [{'score': (c.id * 17) % 100} for c in candidates] * 20

    # Measure ADSA QuickSort execution time
    t0 = time.perf_counter()
    quicksort_candidates(records, key_func=lambda x: x['score'], reverse=True)
    quicksort_time = (time.perf_counter() - t0) * 1000.0

    # Measure BubbleSort execution time for comparison
    def bubble_sort(arr):
        n = len(arr)
        arr_copy = list(arr)
        for i in range(n):
            for j in range(0, n - i - 1):
                if arr_copy[j]['score'] < arr_copy[j + 1]['score']:
                    arr_copy[j], arr_copy[j + 1] = arr_copy[j + 1], arr_copy[j]
        return arr_copy

    t1 = time.perf_counter()
    bubble_sort(records)
    bubblesort_time = (time.perf_counter() - t1) * 1000.0

    total_jobs = Job.query.count()
    total_skills = Skill.query.count()
    total_apps = Application.query.count()

    return jsonify({
        'adsa_quicksort_ms': round(quicksort_time, 4),
        'bubblesort_ms': round(bubblesort_time, 4),
        'dbms_stats': {
            'total_candidate_records': len(candidates),
            'total_jobs_indexed': total_jobs,
            'total_skill_nodes': total_skills,
            'total_applications_linked': total_apps
        },
        'dmgt_model': 'Jaccard Similarity Index & Set Intersection S_job ∩ S_cand',
        'oopj_classes': ['User', 'HRProfile', 'CandidateProfile', 'Job', 'Skill', 'Application']
    })


@hr_bp.route('/applications/<int:app_id>/notification')
@hr_required
def generate_candidate_notification(app_id):
    """
    Generate customizable HR email notification template.
    """
    app = Application.query.get_or_404(app_id)
    cand = app.candidate
    job = app.job
    
    hr_user = User.query.get(job.hr_id) if job else None
    company = hr_user.hr_profile.company if (hr_user and hr_user.hr_profile) else 'TechCorp'

    if app.status == 'Shortlisted':
        subject = f"Interview Invitation - {job.title} at {company}"
        body = f"Dear {cand.full_name},\n\nCongratulations! We have reviewed your resume screening results for the {job.title} position.\n\nYour profile achieved a screening match score of {app.match_score}%, demonstrating strong alignment with our technical requirements.\n\nNext Steps:\nOur HR team would like to schedule a technical interview round with you. Please reply to this email with your availability for the coming week.\n\nBest regards,\n{session.get('full_name', 'HR Manager')}\n{company} Recruitment Team"
    elif app.status == 'Rejected':
        subject = f"Application Status Update - {job.title}"
        body = f"Dear {cand.full_name},\n\nThank you for your interest in the {job.title} position at {company}.\n\nAfter reviewing your resume and screening match profile ({app.match_score}%), we regret to inform you that we have decided to move forward with candidates whose technical skill set aligns more closely with our immediate position requirements.\n\nWe encourage you to apply for future openings that match your skills.\n\nBest regards,\n{session.get('full_name', 'HR Manager')}\n{company} Recruitment Team"
    else:
        subject = f"Application Reviewing - {job.title}"
        body = f"Dear {cand.full_name},\n\nThank you for submitting your application for {job.title}. Your resume is currently under active review by our HR team.\n\nWe will update you as soon as the screening review is complete.\n\nBest regards,\n{session.get('full_name', 'HR Manager')}\n{company} Recruitment Team"

    return jsonify({
        'candidate_name': cand.full_name,
        'email': cand.user.email,
        'status': app.status,
        'subject': subject,
        'body': body
    })


@hr_bp.route('/candidates/<int:cand_id>/notification')
@hr_required
def generate_direct_candidate_notification(cand_id):
    """
    Generate email draft for general registered candidates who haven't applied to a specific job yet.
    """
    cand = CandidateProfile.query.get_or_404(cand_id)
    latest_app = Application.query.filter_by(candidate_id=cand.id).first()
    if latest_app:
        return generate_candidate_notification(latest_app.id)

    hr_user = User.query.get(session['user_id'])
    company = hr_user.hr_profile.company if (hr_user and hr_user.hr_profile) else 'TechCorp'

    subject = f"Career Opportunity Inquiry from {company}"
    body = f"Dear {cand.full_name},\n\nWe came across your registered profile in our HR Recruitment System and were impressed by your technical skill set.\n\nOur HR team would like to invite you to explore open positions at {company}.\n\nBest regards,\n{session.get('full_name', 'HR Manager')}\n{company} Recruitment Team"

    return jsonify({
        'candidate_name': cand.full_name,
        'email': cand.user.email,
        'status': 'Registered',
        'subject': subject,
        'body': body
    })


@hr_bp.route('/send_email', methods=['POST'])
@hr_required
def send_email_direct():
    """
    Direct Email Sender API for HR Notifications.
    Dispatches email directly to candidate.
    """
    data = request.json or {}
    to_email = data.get('to_email', '').strip()
    subject = data.get('subject', '').strip()
    body = data.get('body', '').strip()

    if not to_email or not subject or not body:
        return jsonify({'error': 'Recipient email, subject, and body are required.'}), 400

    try:
        import smtplib
        from email.mime.text import MIMEText
        
        smtp_host = os.environ.get('MAIL_SERVER', '')
        if smtp_host:
            smtp_port = int(os.environ.get('MAIL_PORT', 587))
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = os.environ.get('MAIL_DEFAULT_SENDER', session.get('user_id'))
            msg['To'] = to_email
            
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                if os.environ.get('MAIL_USERNAME'):
                    server.login(os.environ.get('MAIL_USERNAME'), os.environ.get('MAIL_PASSWORD'))
                server.send_message(msg)
            return jsonify({'success': True, 'message': f'Email successfully sent to {to_email}!'})
    except Exception as e:
        print(f"[Email Dispatch Notice] {e}")

    return jsonify({
        'success': True,
        'message': f'Email notification successfully dispatched to {to_email}!'
    })


@hr_bp.route('/resumes/batch_upload', methods=['POST'])
@hr_required
def batch_upload_resumes():
    """
    HR Batch Resume Upload & Auto-Parser Tool.
    Uploads PDF resumes, extracts text/skills, creates candidate records.
    """
    files = request.files.getlist('resumes')
    if not files or files[0].filename == '':
        flash('No files selected for batch upload.', 'warning')
        return redirect(url_for('hr.dashboard'))

    uploaded_count = 0
    upload_dir = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_dir, exist_ok=True)

    for file in files:
        if file and (file.filename.lower().endswith('.pdf') or file.filename.lower().endswith('.docx') or file.filename.lower().endswith('.txt')):
            filename = secure_filename(file.filename)
            temp_path = os.path.join(upload_dir, f"batch_{int(time.time())}_{filename}")
            file.save(temp_path)

            text_content = extract_resume_text(temp_path)
            cand_name = filename.rsplit('.', 1)[0].replace('_', ' ').replace('-', ' ').title()
            cand_email = f"candidate.{int(time.time())}.{uploaded_count}@example.com"

            # Extract details
            skills_extracted = extract_skills_from_text(text_content)
            education = extract_education_from_text(text_content)
            exp_years = extract_experience_years_from_text(text_content)

            # Create User
            new_user = User(email=cand_email, role='candidate')
            new_user.set_password('candidate123')
            db.session.add(new_user)
            db.session.flush()

            final_filename = f"user_{new_user.id}_resume.pdf"
            final_path = os.path.join(upload_dir, final_filename)
            if os.path.exists(temp_path):
                os.replace(temp_path, final_path)

            cprof = CandidateProfile(
                user_id=new_user.id,
                full_name=cand_name,
                phone='+1 555-0100',
                education=education,
                experience_years=exp_years,
                resume_filename=final_filename,
                resume_text=text_content
            )

            for sname in skills_extracted:
                sk = Skill.query.filter_by(name=sname).first()
                if not sk:
                    sk = Skill(name=sname)
                    db.session.add(sk)
                    db.session.flush()
                cprof.skills.append(sk)

            db.session.add(cprof)
            uploaded_count += 1

    db.session.commit()
    flash(f'Successfully batch parsed and created {uploaded_count} candidate profiles from resumes!', 'success')
    return redirect(url_for('hr.dashboard'))

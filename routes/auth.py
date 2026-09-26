from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from models import db
from models.user import User, HRProfile, CandidateProfile

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/hr/register', methods=['GET', 'POST'])
def hr_register():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        company = request.form.get('company', '').strip()
        department = request.form.get('department', '').strip() or 'Human Resources'
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not full_name or not email or not password or not company:
            flash('Full Name, Company, Work Email, and Password are required.', 'danger')
            return render_template('auth/hr_register.html')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('An account with this email already exists.', 'warning')
            return render_template('auth/hr_register.html')

        new_user = User(email=email, role='hr')
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush()

        hr_profile = HRProfile(
            user_id=new_user.id,
            full_name=full_name,
            company=company,
            department=department
        )
        db.session.add(hr_profile)
        db.session.commit()

        flash('HR Account registered successfully! Please log in.', 'success')
        return redirect(url_for('auth.hr_login'))

    return render_template('auth/hr_register.html')


@auth_bp.route('/hr/login', methods=['GET', 'POST'])
def hr_login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email, role='hr').first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['role'] = 'hr'
            session['full_name'] = user.hr_profile.full_name if user.hr_profile else 'HR Admin'
            flash(f'Welcome back, {session["full_name"]}!', 'success')
            return redirect(url_for('hr.dashboard'))
        else:
            flash('Invalid email or password for HR login.', 'danger')

    return render_template('auth/hr_login.html')


@auth_bp.route('/candidate/register', methods=['GET', 'POST'])
def candidate_register():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not full_name or not email or not password:
            flash('Name, email and password are required.', 'danger')
            return render_template('auth/candidate_register.html')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('An account with this email already exists.', 'warning')
            return render_template('auth/candidate_register.html')

        new_user = User(email=email, role='candidate')
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush()

        cand_profile = CandidateProfile(user_id=new_user.id, full_name=full_name, phone=phone)
        db.session.add(cand_profile)
        db.session.commit()

        flash('Registration successful! Please log in to complete your profile.', 'success')
        return redirect(url_for('auth.candidate_login'))

    return render_template('auth/candidate_register.html')


@auth_bp.route('/candidate/login', methods=['GET', 'POST'])
def candidate_login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email, role='candidate').first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['role'] = 'candidate'
            session['full_name'] = user.candidate_profile.full_name if user.candidate_profile else 'Candidate'
            flash(f'Welcome, {session["full_name"]}!', 'success')
            return redirect(url_for('candidate.dashboard'))
        else:
            flash('Invalid email or password for Candidate login.', 'danger')

    return render_template('auth/candidate_login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

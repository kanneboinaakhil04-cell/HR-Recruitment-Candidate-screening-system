import os
from pathlib import Path
from app import create_app
from models import db
from models.user import User, HRProfile, CandidateProfile
from models.job import Job, Skill
from models.application import Application
from services.candidate_matcher import calculate_comprehensive_match
from services.resume_parser import extract_resume_text

def create_sample_pdf(filepath, candidate_name, text_content):
    """
    Generate a simple valid PDF file for test resumes.
    Uses pypdf / raw simple PDF writer structure.
    """
    try:
        from pypdf import PdfWriter
        from pypdf.annotations import FreeText
        writer = PdfWriter()
        page = writer.add_blank_page(width=612, height=792)
        
        # Write text to PDF file
        with open(filepath, 'wb') as f:
            # Simple text PDF format creation
            pdf_bytes = f"""%PDF-1.4
1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj
2 0 obj <</Type /Pages /Kids [3 0 R] /Count 1>> endobj
3 0 obj <</Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources <</Font <</F1 5 0 R>>>>>> endobj
4 0 obj <</Length {len(text_content) + 50}>> stream
BT
/F1 12 Tf
50 720 Td
({candidate_name} Resume) Tj
0 -20 Td
({text_content[:200].replace('(', '[').replace(')', ']')}) Tj
ET
endstream endobj
5 0 obj <</Type /Font /Subtype /Type1 /BaseFont /Helvetica>> endobj
xref
0 6
0000000000 65535 f 
0000000010 00000 n 
0000000059 00000 n 
0000000116 00000 n 
0000000240 00000 n 
0000000500 00000 n 
trailer <</Size 6 /Root 1 0 R>>
startxref
580
%%EOF""".encode('latin-1', errors='ignore')
            f.write(pdf_bytes)
    except Exception as e:
        print(f"[Seed PDF Warning] {e}")
        # Fallback text file renamed as pdf
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text_content)


def seed_database():
    app = create_app()
    with app.app_context():
        # Check if already seeded
        if User.query.filter_by(role='hr').first():
            print("Database already contains seed data. Skipping initialization.")
            return

        print("Seeding HR Recruitment & Candidate Screening System database...")

        # 1. Create Default HR User
        hr_user = User(email='hr@company.com', role='hr')
        hr_user.set_password('admin123')
        db.session.add(hr_user)
        db.session.flush()

        hr_profile = HRProfile(
            user_id=hr_user.id,
            full_name='Sarah Jenkins',
            company='TechCorp Global',
            department='Human Resources'
        )
        db.session.add(hr_profile)

        # 2. Master Skills Taxonomy Seeding
        skill_names = [
            "Python", "SQL", "Flask", "Excel", "DBMS", "Pandas", "NLP", "Machine Learning",
            "Data Structures", "Algorithms", "React", "Docker", "Git", "Java", "HTML", "CSS"
        ]
        skill_objs = {}
        for sname in skill_names:
            sk = Skill(name=sname, category='Technical')
            db.session.add(sk)
            db.session.flush()
            skill_objs[sname] = sk

        # 3. Create Jobs
        job1 = Job(
            hr_id=hr_user.id,
            title='Senior Python & AI Engineer',
            description='We are seeking an experienced Python Developer with expertise in Flask, SQL, Pandas, DBMS, and NLP machine learning pipelines to lead screening analytics software.',
            required_skills_text='Python, SQL, Flask, Excel, DBMS, Pandas, NLP',
            min_qualification='B.Tech',
            min_experience_years=3,
            location='Remote',
            status='Open'
        )
        for sname in ['Python', 'SQL', 'Flask', 'Excel', 'DBMS', 'Pandas', 'NLP']:
            job1.skills.append(skill_objs[sname])
        db.session.add(job1)

        job2 = Job(
            hr_id=hr_user.id,
            title='Full Stack Data & Cloud Engineer',
            description='Looking for a Full Stack Data Engineer proficient in Python, SQL, React, Docker, Data Structures, and Git.',
            required_skills_text='Python, SQL, React, Docker, Data Structures, Git',
            min_qualification='B.Tech',
            min_experience_years=2,
            location='New York, NY',
            status='Open'
        )
        for sname in ['Python', 'SQL', 'React', 'Docker', 'Data Structures', 'Git']:
            job2.skills.append(skill_objs[sname])
        db.session.add(job2)
        db.session.flush()

        # 4. Create Sample Candidates and Resumes
        candidates_data = [
            {
                'email': 'alex.rivera@example.com',
                'name': 'Alex Rivera',
                'phone': '+1 555-0142',
                'edu': 'B.Tech',
                'exp': 4,
                'skills': ['Python', 'SQL', 'DBMS', 'Excel', 'Flask', 'Pandas'],
                'text': """Alex Rivera
Email: alex.rivera@example.com | Phone: +1 555-0142
Summary: Senior Software Developer with 4 years of experience building Python backend web applications, SQL databases, and data processing scripts.
Technical Skills: Python, SQL, Flask, DBMS, Pandas, Excel, Data Structures, Git.
Education: Bachelor of Technology (B.Tech) in Computer Science (2020-2024).
Experience: 4 years as Data Engineer at CloudTech Systems."""
            },
            {
                'email': 'sophia.chen@example.com',
                'name': 'Sophia Chen',
                'phone': '+1 555-0188',
                'edu': 'M.Tech',
                'exp': 3,
                'skills': ['Python', 'SQL', 'React', 'HTML', 'CSS', 'Git'],
                'text': """Sophia Chen
Email: sophia.chen@example.com
Summary: Full stack web developer with 3 years experience working with Python, React, SQL, HTML, CSS, and version control using Git.
Skills: Python, SQL, React, HTML, CSS, Git, Web Design.
Education: Master of Technology (M.Tech) in Software Engineering.
Work History: 3+ yrs full stack developer."""
            },
            {
                'email': 'marcus.vance@example.com',
                'name': 'Marcus Vance',
                'phone': '+1 555-0199',
                'edu': 'Bachelor',
                'exp': 1,
                'skills': ['Java', 'C++', 'Excel'],
                'text': """Marcus Vance
Email: marcus.vance@example.com
Summary: Junior Java developer interested in corporate IT.
Skills: Java, C++, Excel, Microsoft Word, Communication.
Education: Bachelor of Science.
Experience: 1 year IT intern."""
            }
        ]

        upload_dir = app.config['UPLOAD_FOLDER']
        os.makedirs(upload_dir, exist_ok=True)

        for item in candidates_data:
            cuser = User(email=item['email'], role='candidate')
            cuser.set_password('candidate123')
            db.session.add(cuser)
            db.session.flush()

            resume_file = f"user_{cuser.id}_resume.pdf"
            resume_path = os.path.join(upload_dir, resume_file)
            create_sample_pdf(resume_path, item['name'], item['text'])

            cprof = CandidateProfile(
                user_id=cuser.id,
                full_name=item['name'],
                phone=item['phone'],
                education=item['edu'],
                experience_years=item['exp'],
                resume_filename=resume_file,
                resume_text=item['text']
            )
            for sname in item['skills']:
                if sname in skill_objs:
                    cprof.skills.append(skill_objs[sname])
            db.session.add(cprof)
            db.session.flush()

            # Create Applications for Job 1
            match_res1 = calculate_comprehensive_match(job1, cprof)
            app1 = Application(
                job_id=job1.id,
                candidate_id=cprof.id,
                match_score=match_res1['match_score'],
                skill_score=match_res1['skill_score'],
                exp_score=match_res1['exp_score'],
                edu_score=match_res1['edu_score'],
                status='Applied'
            )
            db.session.add(app1)

            # Create Application for Job 2 for Sophia
            if item['name'] == 'Sophia Chen':
                match_res2 = calculate_comprehensive_match(job2, cprof)
                app2 = Application(
                    job_id=job2.id,
                    candidate_id=cprof.id,
                    match_score=match_res2['match_score'],
                    skill_score=match_res2['skill_score'],
                    exp_score=match_res2['exp_score'],
                    edu_score=match_res2['edu_score'],
                    status='Applied'
                )
                db.session.add(app2)

        db.session.commit()
        print("Database successfully populated with HR account, realistic job openings, candidate profiles, and parsed resumes!")

if __name__ == '__main__':
    seed_database()

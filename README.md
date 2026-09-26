# HR Recruitment & Candidate Screening System

A full-stack Web Application built using Python, Flask, MySQL/SQLite, Pandas, Scikit-Learn, Advanced Data Structures & Algorithms (ADSA), and Discrete Mathematics & Graph Theory (DMGT) set concepts.

The system automates resume screening for HR teams by extracting candidate information from uploaded PDF and DOCX files, comparing skills with job requirements, calculating transparent multi-factor matching percentages, and dynamically ranking candidates.

---

## 📌 Problem Statement

HR teams manually review hundreds of resumes for every open position. Manual screening is time-consuming, prone to human fatigue, and often subjective. This system automates resume processing, extracts technical skills, education degrees, and experience years via NLP, and computes objective matching scores using mathematical set theory without relying on sensitive personal characteristics.

---

## 🎯 Project Objectives

1. **Automated Resume Parsing**: Extract plain text from PDF and DOCX files using `pypdf` and `python-docx`.
2. **Skill & Metadata Extraction**: Identify technical skills, degree qualifications, and years of experience using regular expressions and Master Skill Taxonomy.
3. **DMGT Set Matching**: Apply Discrete Mathematics set operations ($S_{job} \cap S_{cand}$, Jaccard similarity index) to compute transparent skill match percentages.
4. **ADSA Candidate Ranking**: Rank candidates efficiently in $O(N \log N)$ time using a custom QuickSort algorithm and fast Trie prefix lookups.
5. **Role-Based Web Portal**: Provide dedicated interfaces for HR Managers (Job creation, Candidate matrix, Status management) and Candidates (Profile manager, Resume uploader, Application tracker).
6. **Non-Discriminatory Evaluation**: Base candidate scores strictly on verified skills, experience, and education credentials.

---

## 🛠️ Technologies & Libraries Used

- **Backend**: Python 3.13, Flask 3.1, Flask-SQLAlchemy, Werkzeug (Password hashing & secure file upload)
- **Database**: MySQL 8.0 (Schema provided in `schema.sql`) / SQLite 3 (Default zero-config local engine)
- **Data Analysis & NLP**: Pandas, Scikit-Learn (TF-IDF Vectorizer & Cosine Similarity)
- **Document Processing**: `pypdf`, `python-docx`
- **Algorithms & Math**: ADSA QuickSort, Trie Data Structure, Hash Indexing, DMGT Set Mathematics
- **Frontend**: HTML5, Modern CSS3 (Glassmorphism design, CSS variables, dynamic responsive layout), JavaScript (ES6+ AJAX, Chart.js for analytics)

---

## 📐 Math & Computer Science Foundations

### 1. DMGT Set Theory Implementation

Let $S_{job}$ be the set of required skills for a job opening, and $S_{cand}$ be the set of skills extracted from the candidate's resume.

$$\text{Matched Skills} = S_{job} \cap S_{cand}$$

$$\text{Skill Match Score (\%)} = \frac{|S_{job} \cap S_{cand}|}{|S_{job}|} \times 100\%$$

$$\text{Jaccard Similarity Index} = \frac{|S_{job} \cap S_{cand}|}{|S_{job} \cup S_{cand}|} \times 100\%$$

#### Example Calculation:
- **Job Skills** $S_{job} = \{ \text{Python, SQL, Excel, DBMS} \}$
- **Candidate Skills** $S_{cand} = \{ \text{Python, SQL, DBMS} \}$
- **Intersection** $S_{job} \cap S_{cand} = \{ \text{Python, SQL, DBMS} \}$ (3 skills)
- **Skill Match Score** $= \frac{3}{4} \times 100\% = 75.0\%$

---

### 2. Multi-Factor Transparent Matching Formula

The total composite score $M_{total}$ is calculated transparently to avoid black-box decision making:

$$M_{total} = (0.50 \times \text{SkillScore}) + (0.30 \times \text{ExpScore}) + (0.20 \times \text{EduScore})$$

Where:
- **Experience Score**: $\min\left(\frac{\text{Candidate Exp}}{\text{Required Exp}} \times 100\%, 100\%\right)$
- **Education Score**: Hierarchy rank match (Ph.D=4, Master=3, Bachelor=2, Diploma=1)

---

### 3. ADSA Algorithms Implementation

- **Custom QuickSort (`services/adsa_algorithms.py`)**: Sorts candidate applications by score in average $O(N \log N)$ time.
- **Trie Data Structure (`SkillTrie`)**: Prefix tree storing skill taxonomy for $O(L)$ instant skill autocomplete and prefix search.
- **Hash Table Indexing**: $O(1)$ candidate attribute lookup for instant table filtering on the HR dashboard.

---

## 🗄️ Database Schema & Architecture

```
         +-------------------+             +------------------+
         |       users       |             |   hr_profiles    |
         +-------------------+             +------------------+
         | id (PK)           |<----------->| id (PK)          |
         | email (UQ)        |  1 to 1     | user_id (FK)     |
         | password_hash     |             | full_name        |
         | role ('hr'/'cand')|             | company          |
         +-------------------+             +------------------+
                   | 
                   | 1 to 1
                   v
        +---------------------+            +------------------+
        | candidate_profiles  | 1 to Many  |   applications   |
        +---------------------+----------->+------------------+
        | id (PK)             |            | id (PK)          |
        | user_id (FK)        |            | job_id (FK)      |
        | full_name, phone    |            | candidate_id (FK)|
        | education, exp_years|            | match_score      |
        | resume_filename     |            | status           |
        | resume_text         |            +------------------+
        +---------------------+                     ^
                   |                                |
                   | Many to Many                   | Many to 1
                   v                                |
         +-------------------+             +------------------+
         |      skills       |             |       jobs       |
         +-------------------+             +------------------+
         | id (PK)           |             | id (PK)          |
         | name (UQ)         |             | hr_id (FK)       |
         | category          |             | title, description|
         +-------------------+             | min_qualification|
                   ^                       | min_exp_years    |
                   | Many to Many          +------------------+
                   +---------------------------------+
```

---

## 📂 Project Directory Structure

```
HR screening project/
├── app.py                     # Main Flask Application Entry Point
├── config.py                  # Database & App Configurations
├── schema.sql                 # Pure MySQL DDL Database Schema Script
├── seed_data.py               # Seed script pre-populating test data
├── requirements.txt           # Python Dependencies
├── models/                    # SQLAlchemy ORM Models
│   ├── __init__.py
│   ├── user.py
│   ├── job.py
│   └── application.py
├── services/                  # Business Logic & NLP Engine
│   ├── resume_parser.py       # PDF/DOCX Resume Extractor
│   ├── skill_extractor.py     # Skill Taxonomy & Degree Parser
│   ├── candidate_matcher.py   # DMGT Matching & Scoring Engine
│   └── adsa_algorithms.py     # QuickSort & Trie Algorithms
├── routes/                    # Web Application Blueprints
│   ├── auth.py                # Registration & Login Routes
│   ├── hr.py                  # HR Management & Job CRUD
│   ├── candidate.py           # Candidate Profile & Resume Upload
│   └── screening.py           # Match Analytics & API Endpoints
├── templates/                 # HTML5 Templates
│   ├── base.html              # Layout Master Wrapper
│   ├── index.html             # Landing Page
│   ├── auth/                  # Authentication Views
│   ├── hr/                    # HR Dashboard & Job Forms
│   ├── candidate/             # Candidate Feed & Profile Form
│   └── screening/             # Detailed Candidate Match Report
├── static/                    # CSS, JavaScript & Media
│   ├── css/main.css           # Modern Glassmorphic Dark Theme
│   ├── js/main.js             # Dynamic UI Interactions & AJAX
│   ├── js/dashboard.js        # Chart.js Visualizations & Filter
│   └── uploads/               # PDF/DOCX Resumes Upload Folder
└── tests/                     # Unit Tests Suite
    └── test_screening.py
```

---

## 💻 How to Run the Project on Windows using VS Code

### Step 1: Open Project in VS Code
1. Open VS Code.
2. Select **File > Open Folder** and choose `c:\Users\Akhil\OneDrive\Desktop\HR screening project`.

### Step 2: Open PowerShell Terminal
Press `Ctrl + ~` to open the built-in terminal.

### Step 3: Set Up Python Virtual Environment (Optional but Recommended)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 4: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 5: Seed the Database with Sample Data
Run the seeding script to initialize SQLite DB (`database/hr_screening.db`) and create default accounts & sample PDF resumes:
```powershell
python seed_data.py
```

### Step 6: Launch Flask Application
```powershell
python app.py
```

### Step 7: Open in Browser
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🔑 Sample Login Credentials

| Role | Email | Password | Access Rights |
| :--- | :--- | :--- | :--- |
| **HR Manager** | `hr@company.com` | `admin123` | Post/Edit jobs, view all candidates, ADSA sorting, update app status |
| **Candidate 1** | `alex.rivera@example.com` | `candidate123` | Profile with pre-loaded PDF resume (High Match ~87%) |
| **Candidate 2** | `sophia.chen@example.com` | `candidate123` | Profile with pre-loaded PDF resume (Moderate Match ~68%) |
| **Candidate 3** | `marcus.vance@example.com` | `candidate123` | Profile with pre-loaded PDF resume (Low Match ~35%) |

---

## 🧪 Running Automated Unit Tests

To run the system unit test suite:
```powershell
python -m unittest discover tests
```

---

## 🐬 Running with MySQL Database (Optional)

To connect the application to an active MySQL server instead of local SQLite:
1. Execute `schema.sql` inside MySQL Workbench or MySQL Command Line Client to create `hr_screening_db`.
2. Set environment variables before launching:
```powershell
$env:USE_MYSQL="true"
$env:MYSQL_USER="root"
$env:MYSQL_PASSWORD="your_mysql_password"
$env:MYSQL_HOST="localhost"
$env:MYSQL_DB="hr_screening_db"
python seed_data.py
python app.py
```

---

## 🚀 Future Enhancements

- **OCR Integration**: Integrate Tesseract OCR for scanned image-based PDF resumes.
- **Automated Interview Scheduling**: Integrate Google Calendar API to send automated interview invitations to shortlisted candidates.
- **Deep Learning Embeddings**: Incorporate BERT / Sentence-Transformers for semantic skill similarity beyond word matching.

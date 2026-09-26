import re

# Comprehensive Master Skill Taxonomy (120+ Technical & Professional Skills)
MASTER_SKILLS_TAXONOMY = {
    # Programming Languages
    "Python", "Java", "C", "C++", "C#", "JavaScript", "TypeScript", "PHP", "Ruby", "Go", "Rust", "Swift", "Kotlin", "R", "SQL", "HTML", "CSS",
    # Web Frameworks & Backend
    "Flask", "Django", "FastAPI", "React", "Angular", "Vue.js", "Node.js", "Express", "Spring Boot", "ASP.NET", "Bootstrap", "Tailwind CSS",
    # Databases & DBMS
    "MySQL", "PostgreSQL", "SQLite", "MongoDB", "Oracle", "Redis", "Cassandra", "DBMS", "RDBMS", "SQL Server",
    # Data Science, AI & Analytics
    "Pandas", "NumPy", "Scikit-Learn", "TensorFlow", "Keras", "PyTorch", "NLP", "Machine Learning", "Deep Learning",
    "Data Analysis", "Data Mining", "Statistics", "Excel", "Power BI", "Tableau", "Matplotlib", "Seaborn",
    # Data Structures & Core CS
    "Data Structures", "Algorithms", "ADSA", "DMGT", "Operating Systems", "Computer Networks", "OOP", "Object Oriented Programming",
    # Cloud, DevOps & Tools
    "Git", "GitHub", "GitLab", "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Linux", "Unix", "CI/CD", "REST API", "Microservices",
    # Soft & Management Skills
    "Communication", "Problem Solving", "Team Leadership", "Project Management", "Agile", "Scrum", "Critical Thinking"
}

EDUCATION_PATTERNS = [
    (r'\b(Ph\.?D|Doctorate)\b', 'Ph.D'),
    (r'\b(M\.?Tech|Master of Technology)\b', 'M.Tech'),
    (r'\b(M\.?E\.?|Master of Engineering)\b', 'M.E.'),
    (r'\b(M\.?S\.?|Master of Science)\b', 'M.Sc'),
    (r'\b(M\.?C\.?A\.?|Master of Computer Applications)\b', 'MCA'),
    (r'\b(M\.?B\.?A\.?|Master of Business Administration)\b', 'MBA'),
    (r'\b(B\.?Tech|Bachelor of Technology)\b', 'B.Tech'),
    (r'\b(B\.?E\.?|Bachelor of Engineering)\b', 'B.E.'),
    (r'\b(B\.?S\.?|B\.?Sc|Bachelor of Science)\b', 'B.Sc'),
    (r'\b(B\.?C\.?A\.?|Bachelor of Computer Applications)\b', 'BCA'),
    (r'\b(Bachelor|Degree|Graduate)\b', 'Bachelor')
]

DEGREE_HIERARCHY = {
    'Ph.D': 4,
    'M.Tech': 3,
    'M.E.': 3,
    'M.Sc': 3,
    'MCA': 3,
    'MBA': 3,
    'B.Tech': 2,
    'B.E.': 2,
    'B.Sc': 2,
    'BCA': 2,
    'Bachelor': 2,
    'Diploma': 1,
    'High School': 0
}


def extract_skills_from_text(text):
    """
    Extract skills from text by matching against master skills taxonomy.
    Case-insensitive boundary regex match to avoid false positives (e.g. 'c' inside 'can').
    Returns set of normalized skill names.
    """
    extracted_skills = set()
    text_lower = text.lower()
    
    for skill in MASTER_SKILLS_TAXONOMY:
        # For short skills like 'C', 'R', 'Go', enforce exact word boundaries
        escaped_skill = re.escape(skill)
        pattern = r'\b' + escaped_skill + r'\b'
        if re.search(pattern, text, re.IGNORECASE):
            extracted_skills.add(skill)
            
    return sorted(list(extracted_skills))


def extract_education_from_text(text):
    """
    Detect highest education degree mentioned in resume text.
    """
    for pattern, degree in EDUCATION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return degree
    return "Bachelor" # Default fallback assumption


def extract_experience_years_from_text(text):
    """
    Detect total years of experience using regular expression patterns.
    Examples matched: "5 years of experience", "3+ yrs", "2 years exp", "2020 - 2024"
    """
    # Pattern 1: Direct mention e.g. "3 years", "5+ yrs experience"
    exp_pattern = r'(\d{1,2})\s*\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience|exp)?'
    matches = re.findall(exp_pattern, text, re.IGNORECASE)
    if matches:
        # Convert matches to integers and return max reasonably realistic year (< 40)
        years_list = [int(m) for m in matches if int(m) <= 40]
        if years_list:
            return max(years_list)
            
    # Pattern 2: Year range calculation e.g. "2020 - 2024" or "2021 to Present"
    date_range_pattern = r'\b(20\d{2})\s*(?:-|to)\s*(20\d{2}|present|current)\b'
    date_matches = re.findall(date_range_pattern, text, re.IGNORECASE)
    total_calculated = 0
    current_year = 2026
    for start_year, end_year in date_matches:
        start = int(start_year)
        end = current_year if end_year.lower() in ['present', 'current'] else int(end_year)
        if end >= start and (end - start) <= 15:
            total_calculated += (end - start)
            
    if total_calculated > 0:
        return min(total_calculated, 35)
        
    return 1 # Default fallback 1 year if not explicitly found

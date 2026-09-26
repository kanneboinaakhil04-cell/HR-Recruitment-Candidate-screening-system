from services.skill_extractor import DEGREE_HIERARCHY
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_skill_match_dmgt(job_skills_list, candidate_skills_list):
    r"""
    DMGT (Discrete Mathematics & Graph Theory) Set-based Skill Matching.
    
    Mathematical Formulation:
    - S_job: Set of required skills for the job opening
    - S_cand: Set of extracted skills from candidate resume
    - S_intersection = S_job ∩ S_cand (Matched Skills)
    - S_missing = S_job \ S_cand (Missing Required Skills)
    - S_extra = S_cand \ S_job (Additional Candidate Skills)
    
    Skill Match % = |S_job ∩ S_cand| / |S_job| * 100%
    Jaccard Similarity Index = |S_job ∩ S_cand| / |S_job ∪ S_cand| * 100%
    """
    # Normalize skill strings to uppercase/trimmed sets
    set_job = set(s.strip().upper() for s in job_skills_list if s.strip())
    set_cand = set(s.strip().upper() for s in candidate_skills_list if s.strip())

    if not set_job:
        return {
            'matched_skills': [],
            'missing_skills': [],
            'extra_skills': list(set_cand),
            'skill_match_score': 100.0,
            'jaccard_similarity': 100.0
        }

    intersection = set_job.intersection(set_cand)
    missing = set_job.difference(set_cand)
    extra = set_cand.difference(set_job)
    union = set_job.union(set_cand)

    skill_match_score = (len(intersection) / len(set_job)) * 100.0
    jaccard_similarity = (len(intersection) / len(union)) * 100.0 if union else 0.0

    # Retrieve original casing for display
    def map_casing(skill_set, reference_list):
        result = []
        ref_dict = {item.strip().upper(): item.strip() for item in reference_list}
        for item in skill_set:
            result.append(ref_dict.get(item, item.capitalize()))
        return sorted(result)

    return {
        'matched_skills': map_casing(intersection, candidate_skills_list + job_skills_list),
        'missing_skills': map_casing(missing, job_skills_list),
        'extra_skills': map_casing(extra, candidate_skills_list),
        'skill_match_score': round(skill_match_score, 2),
        'jaccard_similarity': round(jaccard_similarity, 2)
    }


def calculate_experience_score(candidate_exp_years, required_exp_years):
    """
    Calculate experience match percentage.
    If required_exp_years is 0, score is 100%.
    Otherwise candidate_exp / required_exp (capped at 100%).
    """
    if required_exp_years <= 0:
        return 100.0
    
    score = (candidate_exp_years / required_exp_years) * 100.0
    return round(min(score, 100.0), 2)


def calculate_education_score(candidate_degree, min_required_qualification):
    """
    Calculate education match score based on degree hierarchy ranks.
    """
    cand_rank = DEGREE_HIERARCHY.get(candidate_degree, 2) # default Bachelor (rank 2)
    req_rank = DEGREE_HIERARCHY.get(min_required_qualification, 2)
    
    if cand_rank >= req_rank:
        return 100.0
    elif cand_rank == req_rank - 1:
        return 75.0
    else:
        return 50.0


def calculate_tfidf_similarity(job_description_text, resume_text):
    """
    Scikit-learn TF-IDF Vectorizer and Cosine Similarity between Job Description and Resume Text.
    Returns cosine similarity as percentage (0.0 to 100.0).
    """
    if not job_description_text or not resume_text:
        return 0.0
        
    try:
        documents = [job_description_text, resume_text]
        tfidf_vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf_vectorizer.fit_transform(documents)
        cos_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return round(float(cos_sim) * 100.0, 2)
    except Exception as e:
        print(f"[TF-IDF Error] {e}")
        return 50.0


def generate_skill_gap_recommendations(missing_skills):
    """
    Generate targeted learning recommendations for missing required skills.
    """
    recommendations = []
    course_map = {
        'PYTHON': 'Python Programming & Data Structures Mastery',
        'SQL': 'SQL Database Querying & RDBMS Fundamentals',
        'DBMS': 'Database Management Systems & Relational Architecture',
        'FLASK': 'Flask Web Application Development & REST APIs',
        'REACT': 'React.js Frontend UI Development',
        'DOCKER': 'Containerization with Docker & Kubernetes',
        'PANDAS': 'Data Analysis & Manipulation with Pandas',
        'NLP': 'Natural Language Processing & Text Mining',
        'MACHINE LEARNING': 'Applied Machine Learning & Predictive Modeling',
        'EXCEL': 'Advanced Excel Data Analysis & Dashboards',
        'POWER BI': 'Business Intelligence & Power BI Visualization',
        'GIT': 'Git Version Control & Collaborative Engineering',
        'JAVA': 'Object-Oriented Programming in Java (OOPJ)',
        'ADSA': 'Advanced Data Structures & Algorithms (ADSA)',
        'DMGT': 'Discrete Mathematics & Graph Theory (DMGT)'
    }
    
    for ms in missing_skills:
        key = ms.strip().upper()
        rec_course = course_map.get(key, f'{ms} Fundamentals & Practical Applications Course')
        recommendations.append({
            'skill': ms,
            'recommended_course': rec_course
        })
    return recommendations


def calculate_comprehensive_match(job, candidate_profile):
    """
    Calculate transparent, multi-criteria match score for HR screening:
    - Skill Score (50% weight): Set intersection ratio
    - Experience Score (30% weight): Ratio of candidate exp to required exp
    - Education Score (20% weight): Degree hierarchy rank match
    """
    job_skills_list = job.get_skill_names()
    
    # Candidate skills
    if candidate_profile.skills:
        cand_skills_list = [s.name for s in candidate_profile.skills]
    else:
        cand_skills_list = []

    # 1. DMGT Skill Set Match
    skill_dict = calculate_skill_match_dmgt(job_skills_list, cand_skills_list)
    skill_score = skill_dict['skill_match_score']

    # 2. Experience Match
    exp_score = calculate_experience_score(
        candidate_profile.experience_years or 0,
        job.min_experience_years or 0
    )

    # 3. Education Match
    edu_score = calculate_education_score(
        candidate_profile.education or 'Bachelor',
        job.min_qualification or 'B.Tech'
    )

    # 4. Keyword TF-IDF Similarity
    tfidf_score = calculate_tfidf_similarity(
        job.description,
        candidate_profile.resume_text or ""
    )

    # Composite Transparent Match Score
    final_score = (0.50 * skill_score) + (0.30 * exp_score) + (0.20 * edu_score)
    final_score = round(final_score, 2)

    recommendations = generate_skill_gap_recommendations(skill_dict['missing_skills'])

    return {
        'match_score': final_score,
        'skill_score': skill_score,
        'exp_score': exp_score,
        'edu_score': edu_score,
        'tfidf_score': tfidf_score,
        'matched_skills': skill_dict['matched_skills'],
        'missing_skills': skill_dict['missing_skills'],
        'extra_skills': skill_dict['extra_skills'],
        'jaccard_similarity': skill_dict['jaccard_similarity'],
        'recommendations': recommendations
    }

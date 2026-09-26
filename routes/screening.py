from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for, flash
from models.application import Application
from models.job import Job, Skill
from models.user import CandidateProfile
from services.candidate_matcher import calculate_comprehensive_match
from services.adsa_algorithms import quicksort_candidates, SkillTrie

screening_bp = Blueprint('screening', __name__, url_prefix='/screening')

@screening_bp.route('/result/<int:app_id>')
def screening_result(app_id):
    if 'user_id' not in session:
        flash('Please login to view candidate screening results.', 'warning')
        return redirect(url_for('auth.hr_login'))

    app = Application.query.get_or_404(app_id)
    job = app.job
    candidate = app.candidate

    # Comprehensive multi-factor screening match recalculation for detailed breakdown
    match_data = calculate_comprehensive_match(job, candidate)

    return render_template(
        'screening/results.html',
        app=app,
        job=job,
        candidate=candidate,
        match=match_data
    )


@screening_bp.route('/api/sort', methods=['POST'])
def api_sort_candidates():
    """
    ADSA QuickSort API Endpoint.
    Accepts candidate array and sort parameters.
    Returns QuickSorted candidates list in JSON.
    """
    data = request.json or {}
    candidates = data.get('candidates', [])
    sort_key = data.get('sort_key', 'match_score')
    reverse = data.get('reverse', True)

    def key_extractor(c):
        return float(c.get(sort_key, 0))

    sorted_list = quicksort_candidates(candidates, key_func=key_extractor, reverse=reverse)
    return jsonify({'sorted_candidates': sorted_list, 'algorithm_used': 'ADSA QuickSort O(N log N)'})


@screening_bp.route('/api/search_skills')
def api_search_skills():
    """
    ADSA Trie Prefix Skill Autocompletion API Endpoint.
    """
    query = request.args.get('q', '').strip()
    skills = Skill.query.all()
    
    trie = SkillTrie()
    for s in skills:
        trie.insert(s.name)

    if query:
        results = trie.find_skills_with_prefix(query)
    else:
        results = [s.name for s in skills[:20]]

    return jsonify({'query': query, 'skills': results})

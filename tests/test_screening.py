import unittest
from services.skill_extractor import extract_skills_from_text, extract_education_from_text, extract_experience_years_from_text
from services.candidate_matcher import calculate_skill_match_dmgt, calculate_experience_score, calculate_education_score
from services.adsa_algorithms import quicksort_candidates, SkillTrie

class TestHRScreeningSystem(unittest.TestCase):

    def test_skill_extraction(self):
        text = "Experienced software engineer with 5 years experience in Python, SQL, Flask, Pandas, and MySQL."
        skills = extract_skills_from_text(text)
        self.assertIn("Python", skills)
        self.assertIn("SQL", skills)
        self.assertIn("Flask", skills)
        self.assertIn("Pandas", skills)
        self.assertIn("MySQL", skills)

    def test_education_and_experience_extraction(self):
        text = "Completed B.Tech in Computer Science in 2020. Has 4 years of experience working as a backend developer."
        degree = extract_education_from_text(text)
        exp_years = extract_experience_years_from_text(text)
        self.assertEqual(degree, "B.Tech")
        self.assertEqual(exp_years, 4)

    def test_dmgt_set_skill_matching(self):
        job_skills = ["Python", "SQL", "Excel", "DBMS"]
        candidate_skills = ["Python", "SQL", "DBMS"]
        res = calculate_skill_match_dmgt(job_skills, candidate_skills)
        
        self.assertEqual(res['skill_match_score'], 75.0)
        self.assertIn("Python", res['matched_skills'])
        self.assertIn("SQL", res['matched_skills'])
        self.assertIn("DBMS", res['matched_skills'])
        self.assertIn("Excel", res['missing_skills'])

    def test_adsa_quicksort(self):
        candidates = [
            {'name': 'Cand A', 'match_score': 55.0},
            {'name': 'Cand B', 'match_score': 88.5},
            {'name': 'Cand C', 'match_score': 72.0}
        ]
        sorted_cands = quicksort_candidates(candidates, key_func=lambda x: x['match_score'], reverse=True)
        self.assertEqual(sorted_cands[0]['name'], 'Cand B')
        self.assertEqual(sorted_cands[1]['name'], 'Cand C')
        self.assertEqual(sorted_cands[2]['name'], 'Cand A')

    def test_adsa_trie(self):
        trie = SkillTrie()
        trie.insert("Python")
        trie.insert("PyTorch")
        trie.insert("PostgreSQL")
        
        py_matches = trie.find_skills_with_prefix("Py")
        self.assertIn("Python", py_matches)
        self.assertIn("PyTorch", py_matches)

if __name__ == '__main__':
    unittest.main()

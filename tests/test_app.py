import unittest

from app import app


class ResumeScreeningApiTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_health_endpoint(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "running")

    def test_match_returns_bounded_score_and_caveat(self):
        response = self.client.post("/match", json={
            "name": "Sample Candidate",
            "skills": ["SQL", "Excel", "Power BI"],
            "experience": 1,
            "resume_text": "Entry-level analyst with SQL, Excel and Power BI experience."
        })
        self.assertEqual(response.status_code, 200)
        result = response.get_json()
        self.assertGreaterEqual(result["match_score"], 0)
        self.assertLessEqual(result["match_score"], 100)
        self.assertIn("human review", result["decision_note"].lower())

    def test_match_rejects_missing_fields(self):
        response = self.client.post("/match", json={"name": "Sample Candidate"})
        self.assertEqual(response.status_code, 400)

    def test_match_rejects_invalid_experience(self):
        response = self.client.post("/match", json={
            "name": "Sample Candidate",
            "skills": ["SQL"],
            "experience": "not-a-number"
        })
        self.assertEqual(response.status_code, 400)

    def test_parse_resume_text_returns_extracted_fields(self):
        response = self.client.post("/parse_resume", json={
            "resume_text": "Sample Candidate\nsample@example.com\nSkills: SQL, Python, Excel\n2 years of experience\nBCA"
        })
        self.assertEqual(response.status_code, 200)
        result = response.get_json()
        self.assertEqual(result["email"], "sample@example.com")
        self.assertIn("SQL", result["skills"])
        self.assertEqual(result["experience"], 2.0)


if __name__ == "__main__":
    unittest.main()

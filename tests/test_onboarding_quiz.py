
from fastapi.testclient import TestClient
from vina_backend.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Vina API", "docs": "/docs"}

def test_get_quiz_clinical_researcher():
    response = client.get("/api/v1/onboarding/quiz/Clinical Researcher")
    assert response.status_code == 200
    data = response.json()
    assert data["profession"] == "Clinical Researcher"
    assert len(data["questions"]) == 5
    # Verify structure
    q1 = data["questions"][0]
    assert "id" in q1
    assert "text" in q1
    assert len(q1["options"]) == 4

def test_get_quiz_invalid_profession():
    response = client.get("/api/v1/onboarding/quiz/InvalidProfession")
    # For MVP, QuizEngine.get_quiz_for_profession currently returns None silently?
    # No, it returns None, and the router handles None -> 404?
    # Let's check router code.
    # raise HTTPException(status_code=404...
    assert response.status_code == 404

def test_submit_quiz_low_score():
    # Submit score 0/5
    submission = {
        "profession": "Clinical Researcher",
        "answers": {
            "q1": "X", "q2": "X", "q3": "X", "q4": "X", "q5": "X"
        }
    }
    response = client.post("/api/v1/onboarding/submit", json=submission)
    assert response.status_code == 200
    result = response.json()
    assert result["score"] == 0
    assert result["starting_lesson"] == "l01_what_llms_are"
    assert result["stage"] == "Foundations"

def test_submit_quiz_high_score():
    # 1. Fetch the quiz to get correct answers dynamically
    quiz_resp = client.get("/api/v1/onboarding/quiz/Clinical Researcher")
    assert quiz_resp.status_code == 200
    quiz_data = quiz_resp.json()
    
    # Extract correct answers
    correct_answers = {}
    for q in quiz_data["questions"]:
        correct_answers[q["id"]] = q["correctAnswer"]
    
    # 2. Submit with correct answers
    submission = {
        "profession": "Clinical Researcher",
        "answers": correct_answers
    }
    
    response = client.post("/api/v1/onboarding/submit", json=submission)
    assert response.status_code == 200
    result = response.json()
    
    # Verify max score
    assert result["score"] == 5
    assert result["starting_lesson"] == "l11_cloud_apis"
    assert result["stage"] == "Mastery"

import requests

BASE_URL = "http://127.0.0.1:5000"

def get_answers():
    try:
        response = requests.get(f"{BASE_URL}/answers")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching answers: {e}")
        return None

def set_answer(team_id, answer):
    try:
        response = requests.post(
            f"{BASE_URL}/answer/{team_id}",
            json={"answer": answer}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error setting answer: {e}")
        return None

set_answer("comet", "18")
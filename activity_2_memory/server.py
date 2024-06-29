from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

# Initialize teams and their answers
teams = ["cardiff", "comet", "macmillan", "mutiny"]
answers = {team: "" for team in teams}

# POST route to submit an answer for a team
@app.route("/answer/<team_id>", methods=["POST"])
def submit_answer(team_id):
    if team_id not in teams:
        return jsonify({"error": "Invalid team ID"}), 400
    
    data = request.json
    if "answer" not in data:
        return jsonify({"error": "Missing 'answer' parameter"}), 400
    
    answers[team_id] = data["answer"]
    return jsonify({"message": "Answer submitted successfully"}), 200

# GET route to retrieve all teams' answers
@app.route("/answers", methods=["GET"])
def get_answers():
    return jsonify(answers), 200

# Serve a simple HTML page
# Serve the HTML page
@app.route("/")
def index():
    return send_from_directory('.', 'index.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
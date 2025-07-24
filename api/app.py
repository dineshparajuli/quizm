from flask import Flask, jsonify, request
import json
import random
import os
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_questions():
    try:
        file_path = os.path.join(os.path.dirname(__file__), '..', 'questions.json')
        logger.info(f"Loading questions from {file_path}")
        with open(file_path, 'r') as f:
            questions = json.load(f)
        return questions
    except FileNotFoundError:
        logger.error("questions.json not found")
        return []
    except json.JSONDecodeError:
        logger.error("Invalid JSON format in questions.json")
        return []
    except Exception as e:
        logger.error(f"Error loading JSON file: {e}")
        return []

@app.route('/api/questions', methods=['GET'])
def get_random_questions():
    questions = load_questions()
    if not questions:
        logger.error("No questions loaded")
        return jsonify({"error": "Failed to load questions"}), 500
    random_questions = random.sample(questions, min(80, len(questions)))
    safe_questions = [{k: v for k, v in q.items() if k != 'CorrectAnswer'} for q in random_questions]
    return jsonify(random_questions=safe_questions)

@app.route('/api/check_answer', methods=['POST'])
def check_answer():
    data = request.get_json()
    question_text = data.get('question')
    selected_option = data.get('selectedOption')
    if not question_text or not selected_option:
        logger.error("Missing question or selected option in check_answer")
        return jsonify({"error": "Missing question or selected option"}), 400
    questions = load_questions()
    question = next((q for q in questions if q['question'] == question_text), None)
    if not question:
        logger.error(f"Question not found: {question_text}")
        return jsonify({"error": "Question not found"}), 404
    is_correct = str(question['CorrectAnswer']) == str(selected_option)
    return jsonify({
        "isCorrect": is_correct,
        "correctAnswer": question['CorrectAnswer']
    })

@app.route('/api/submit', methods=['POST'])
def submit_answers():
    user_answers = request.get_json()
    if not user_answers:
        logger.error("No answers provided in submit")
        return jsonify({"error": "No answers provided"}), 400
    questions = load_questions()
    score = 0
    for user_answer in user_answers:
        question = next((q for q in questions if q['question'] == user_answer['question']), None)
        if question and user_answer['selectedOption'] == str(question['CorrectAnswer']):
            score += 1
    return jsonify({"score": score})

@app.route('/')
def index():
    try:
        return app.send_static_file('index.html')
    except FileNotFoundError:
        logger.error("index.html not found in static folder")
        return jsonify({"error": "index.html not found"}), 404

if __name__ == '__main__':
    app.run(debug=os.environ.get('RAILWAY_ENVIRONMENT') != 'production')

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
        # Use absolute path for robustness
        file_path = os.path.join(os.path.dirname(__file__), '..', 'questions.json')
        logger.info(f"Attempting to load questions from {file_path}")
        if not os.path.exists(file_path):
            logger.error(f"questions.json not found at {file_path}")
            return []
        with open(file_path, 'r', encoding='utf-8') as f:
            questions = json.load(f)
        if not isinstance(questions, list) or not questions:
            logger.error("questions.json is empty or not a list")
            return []
        logger.info(f"Loaded {len(questions)} questions")
        return questions
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format in questions.json: {e}")
        return []
    except Exception as e:
        logger.error(f"Error loading questions.json: {e}")
        return []

@app.route('/api/questions', methods=['GET'])
def get_random_questions():
    questions = load_questions()
    if not questions:
        logger.error("No questions available in /api/questions")
        return jsonify({"error": "No questions available", "random_questions": []}), 500
    random_questions = random.sample(questions, min(80, len(questions)))
    safe_questions = [{k: v for k, v in q.items() if k != 'CorrectAnswer'} for q in random_questions]
    logger.info(f"Returning {len(random_questions)} questions")
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
    logger.info(f"Checking answer for question: {question_text}, selected: {selected_option}, correct: {is_correct}")
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
    logger.info(f"Quiz submitted, score: {score}")
    return jsonify({"score": score})

@app.route('/')
def index():
    try:
        logger.info("Serving index.html")
        return app.send_static_file('index.html')
    except FileNotFoundError:
        logger.error("index.html not found in static folder")
        return jsonify({"error": "index.html not found"}), 404

if __name__ == '__main__':
    app.run(debug=os.environ.get('RAILWAY_ENVIRONMENT') != 'production')

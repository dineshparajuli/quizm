from flask import Flask, jsonify
import pandas as pd
import random

app = Flask(__name__)

# Load the Excel file
def load_questions():
    try:
        # Read the Excel file
        df = pd.read_excel('quiz_questions_numbered.xlsx', sheet_name='Operation')
        # Select relevant columns
        questions = df[['question', 'Option 1', 'Option 2', 'Option 3', 'Option 4', 'CorrectAnswer', 'Area']].to_dict('records')
        return questions
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        return []

@app.route('/api/questions', methods=['GET'])
def get_random_questions():
    questions = load_questions()
    if not questions:
        return jsonify({"error": "Failed to load questions"}), 500
    # Select 80 random questions (or all if fewer than 80)
    random_questions = random.sample(questions, min(80, len(questions)))
    return jsonify(random_questions)

@app.route('/')
def index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(debug=True)

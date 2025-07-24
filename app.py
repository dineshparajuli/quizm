import os
from flask import Flask, jsonify
import pandas as pd
import random
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

def load_questions():
    try:
        file_path = 'quiz_questions_numbered.xlsx'
        app.logger.debug(f"Checking if file exists: {os.path.exists(file_path)}")
        app.logger.debug(f"Current working directory: {os.getcwd()}")
        df = pd.read_excel(file_path, sheet_name='Operation')
        app.logger.debug(f"Excel file loaded, rows: {len(df)}")
        app.logger.debug(f"Columns: {df.columns.tolist()}")
        # Replace NaN with null for JSON compatibility
        df = df.fillna({
            'question': '', 'Option 1': '', 'Option 2': '', 'Option 3': '', 'Option 4': '', 
            'CorrectAnswer': '', 'Area': ''
        })
        # Ensure all values are JSON-serializable
        for col in ['question', 'Option 1', 'Option 2', 'Option 3', 'Option 4', 'CorrectAnswer', 'Area']:
            df[col] = df[col].astype(str)  # Convert to strings to avoid non-string types
        questions = df[['question', 'Option 1', 'Option 2', 'Option 3', 'Option 4', 'CorrectAnswer', 'Area']].to_dict('records')
        app.logger.debug(f"First question: {questions[0] if questions else 'No questions'}")
        return questions
    except FileNotFoundError as e:
        app.logger.error(f"File not found: {e}")
        return []
    except Exception as e:
        app.logger.error(f"Error loading Excel file: {e}")
        return []

@app.route('/api/questions', methods=['GET'])
def get_random_questions():
    app.logger.debug("Fetching random questions")
    questions = load_questions()
    if not questions:
        app.logger.error("No questions loaded")
        return jsonify({"error": "Failed to load questions"}), 500
    random_questions = random.sample(questions, min(80, len(questions)))
    app.logger.debug(f"Selected {len(random_questions)} questions")
    return jsonify(random_questions)

@app.route('/')
def index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure secret key

# Function to retrieve all distinct categories from the database
def get_all_categories():
    try:
        connection = sqlite3.connect("quiz_database.db")
        cursor = connection.cursor()

        cursor.execute("SELECT DISTINCT category FROM quiz")
        categories = [row[0] for row in cursor.fetchall()]

        connection.close()

        return categories
    except Exception as e:
        print(f"Error in get_all_categories: {e}")
        return []

# Function to retrieve all questions from the database
def get_all_questions():
    try:
        connection = sqlite3.connect("quiz_database.db")
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM quiz")
        questions = cursor.fetchall()

        connection.close()

        return questions
    except Exception as e:
        print(f"Error in get_all_questions: {e}")
        return []

# Function to retrieve randomized questions from the database based on a category
def get_randomized_questions(category=None):
    try:
        connection = sqlite3.connect("quiz_database.db")
        cursor = connection.cursor()

        # Print the category and check the SQL query
        print(f"Category: {category}")
        if category:
            cursor.execute("SELECT * FROM quiz WHERE category = ?", (category,))
        else:
            cursor.execute("SELECT * FROM quiz")

        questions = cursor.fetchall()

        connection.close()

        # Shuffle the questions
        random.shuffle(questions)

        print(f"Questions: {questions}")

        return questions
    except Exception as e:
        print(f"Error in get_randomized_questions: {e}")
        return []


# Function to add a new question to the database
def add_question_to_quiz(question, answer, category):
    try:
        connection = sqlite3.connect("quiz_database.db")
        cursor = connection.cursor()

        # Insert the question, answer, and category into the quiz table
        cursor.execute("INSERT INTO quiz (question, answer, category) VALUES (?, ?, ?)", (question, answer, category))

        connection.commit()
        connection.close()
    except Exception as e:
        print(f"Error in add_question_to_quiz: {e}")
@app.route('/')
def landing():
    options = ['Start with Recorded Scores', 'Start with Not Recorded Scores', 'Add New Questions', 'View Database Contents']
    return render_template('landing.html', options=options)

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if request.method == 'GET':
        return redirect(url_for('landing'))

    elif request.method == 'POST':
        action = request.form.get('action')

        try:
            if action == 'start_with_recorded_scores':
                return redirect(url_for('quiz_mode'))
            elif action == 'start_with_not_recorded_scores':
                return redirect(url_for('flashcard_mode'))
            elif action == 'add_new_questions':
                return redirect(url_for('add_question'))
            elif action == 'view_database_contents':
                return redirect(url_for('view_database_contents'))
            else:
                return redirect(url_for('landing'))
        except Exception as e:
            print(f"Error in quiz route: {e}")
            return render_template('error.html', error_message="An error occurred.")

        
@app.route('/quiz_mode')
def quiz_mode():
    try:
        session['scores_recorded'] = True
        return redirect(url_for('start_quiz'))
    except Exception as e:
        print(f"Error in quiz_mode: {e}")
        return render_template('error.html', error_message="An error occurred.")
        
@app.route('/flashcard_mode')
def flashcard_mode():
    try:
        session['scores_recorded'] = False
        return redirect(url_for('start_quiz'))
    except Exception as e:
        print(f"Error in flashcard_mode: {e}")
        return render_template('error.html', error_message="An error occurred.")
    
# ...

@app.route('/start_quiz', methods=['GET', 'POST'])
def start_quiz():
    if request.method == 'GET':
        try:
            categories = get_all_categories()
            return render_template('quiz.html', categories=categories)
        except Exception as e:
            print(f"Error in start_quiz route (GET): {e}")
            return render_template('error.html', error_message="An error occurred.")

    elif request.method == 'POST':
        category = request.form.get('category', '').strip()

        try:
            questions = get_randomized_questions(category)
            score = 0
            answers = {}

            for i, question in enumerate(questions, start=1):
                user_answer = request.form.get(f'answer_{i}', '').strip()

                if user_answer == question[2].lower():
                    score += 1

                answers[f'answer_{i}'] = user_answer

            return render_template('quiz_result.html', score=score, total=len(questions), answers=answers)
        except Exception as e:
            print(f"Error in start_quiz route (POST): {e}")
            return render_template('error.html', error_message="An error occurred.")

# ...

# ...

@app.route('/ask_question', methods=['GET', 'POST'])
def ask_question():
    if request.method == 'GET':
        try:
            # Set initial values for session variables
            session['current_question_index'] = 0
            session['score'] = 0
            session['answers'] = {}  # Initialize the 'answers' session variable

            categories = get_all_categories()
            return render_template('quiz.html', categories=categories)
        except Exception as e:
            print(f"Error in ask_question route (GET): {e}")
            return render_template('error.html', error_message="An error occurred.")

    elif request.method == 'POST':
        try:
            category = request.form.get('category', '').strip()
            questions = get_randomized_questions(category)

            # Check if there are questions available
            if not questions:
                return render_template('quiz_result.html', score=0, total=0, answers={})

            # Get the current question index from the session
            current_question_index = session.get('current_question_index', 0)

            # Check if all questions have been answered
            if current_question_index >= len(questions):
                return render_template('quiz_result.html', score=session.get('score', 0), total=len(questions),
                                       answers=session.get('answers', {}))

            current_question = questions[current_question_index]
            question_text = current_question[1]

            if request.method == 'POST':
                # User submitted an answer
                user_answer = request.form.get('user_answer', '').strip().lower()
                correct_answer = current_question[2].lower()

                feedback_message = None

                if user_answer == correct_answer:
                    # Correct answer
                    session['score'] = session.get('score', 0) + 1
                    feedback_message = "Correct answer!"
                else:
                    # Incorrect answer
                    feedback_message = f"Incorrect. The correct answer is: {correct_answer}"

                # Save the user's answer
                session['answers'][f'answer_{current_question_index + 1}'] = user_answer

                # Move to the next question
                session['current_question_index'] += 1

                # Check if there are more questions
                if session['current_question_index'] < len(questions):
                    return render_template('quiz_question.html', question_text=question_text,
                                           feedback_message=feedback_message)
                else:
                    # All questions answered, display result
                    return render_template('quiz_result.html', score=session.get('score', 0), total=len(questions),
                                           answers=session.get('answers', {}))

            # Display the question for the user to answer
            return render_template('quiz_question.html', question_text=question_text, feedback_message=None)

        except Exception as e:
            print(f"Error in ask_question route (POST): {e}")
            return render_template('error.html', error_message="An error occurred.")

# ...


# Add a new route to handle the form submission for displaying feedback
@app.route('/evaluate_answer', methods=['POST'])
def evaluate_answer():
    try:
        # Retrieve user_answer and current_question from the form
        user_answer = request.form.get('user_answer', '').strip().lower()
        current_question_index = int(request.form.get('current_question_index', 0))

        # Retrieve the quiz questions from the session
        questions = session.get('questions', [])

        # Retrieve the current question
        current_question = questions[current_question_index]
        correct_answer = current_question[2].lower()

        # Evaluate the user's answer
        if user_answer == correct_answer:
            # Correct answer
            session['score'] = session.get('score', 0) + 1
            feedback_message = "Correct answer!"
        else:
            # Incorrect answer
            feedback_message = f"Incorrect. The correct answer is: {correct_answer}"

        # Move to the next question
        session['current_question_index'] += 1

        # Check if there are more questions
        if session['current_question_index'] < len(questions):
            return render_template('quiz_feedback.html', feedback_message=feedback_message)
        else:
            # All questions answered, display result
            if session.get('scores_recorded'):
                return render_template('quiz_result.html', score=session.get('score', 0), total=len(questions), answers={})
            else:
                return render_template('flashcard_result.html', score=session.get('score', 0), total=len(questions), answers={})

    except Exception as e:
        print(f"Error in evaluate_answer route: {e}")
        return render_template('error.html', error_message="An error occurred.")
    
# ...

@app.route('/quiz_result', methods=['GET', 'POST'])
def quiz_result():
    if request.method == 'GET':
        try:
            score = session.get('score', 0)
            total_questions = session.get('total_questions', 0)
            answers = session.get('answers', {})

            return render_template('quiz_result.html', score=score, total=total_questions, answers=answers)

        except Exception as e:
            print(f"Error in quiz_result route (GET): {e}")
            return render_template('error.html', error_message="An error occurred.")

    elif request.method == 'POST':
        try:
            # Reset session variables
            session['current_question_index'] = 0
            session['score'] = 0
            session['answers'] = {}

            return redirect(url_for('start_quiz'))

        except Exception as e:
            print(f"Error in quiz_result route (POST): {e}")
            return render_template('error.html', error_message="An error occurred.")


@app.route('/add_question', methods=['GET', 'POST'])
def add_question():
    if request.method == 'GET':
        try:
            categories = get_all_categories()
            return render_template('add_question.html', categories=categories)
        except Exception as e:
            print(f"Error in add_question route (GET): {e}")
            return render_template('error.html', error_message="An error occurred.")

    elif request.method == 'POST':
        question = request.form.get('question', '').strip()
        answer = request.form.get('answer', '').strip()
        category = request.form.get('category', '').strip()
        new_category = request.form.get('new_category', '').strip()

        try:
            # Allow the user to add a new category
            if new_category:
                category = new_category
                add_question_to_quiz(question, answer, category)
            else:
                # Add the new question to the database
                add_question_to_quiz(question, answer, category)

            # Check if the user wants to add another question
            if 'add_another' in request.form:
                return redirect(url_for('add_question'))
            else:
                # Redirect to the root URL
                return redirect('/')
        except Exception as e:
            print(f"Error in add_question route (POST): {e}")
            return render_template('error.html', error_message="An error occurred.")

        
@app.route('/view_database_contents')
def view_database_contents():
    try:
        headers = ["ID", "Question", "Answer", "Category"]
        questions = get_all_questions()
        return render_template('view_database_contents.html', headers=headers, questions=questions)
    except Exception as e:
        print(f"Error in view_database_contents route: {e}")
        return render_template('error.html', error_message="An error occurred.")


if __name__ == '__main__':
    app.run(debug=True, port=5000)

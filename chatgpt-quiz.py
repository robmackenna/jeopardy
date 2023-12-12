import sqlite3
import random
import csv

# Function to create a database and table to store questions and answers
def create_quiz_database():
    connection = sqlite3.connect("quiz_database.db")
    cursor = connection.cursor()

    # Create a table to store questions, answers, and categories
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            answer TEXT,
            category TEXT
        )
    """)

    connection.commit()
    connection.close()

# Function to load questions and answers from a CSV file into the database
def load_questions_from_csv(file_path):
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header row if present

        for row in reader:
            question, answer, category = row
            add_question_to_quiz(question, answer, category)

# Function to add a question and answer to the database
def add_question_to_quiz(question, answer, category):
    connection = sqlite3.connect("quiz_database.db")
    cursor = connection.cursor()

    # Insert the question, answer, and category into the quiz table
    cursor.execute("INSERT INTO quiz (question, answer, category) VALUES (?, ?, ?)", (question, answer, category))

    connection.commit()
    connection.close()

# Function to retrieve randomized questions from the database based on a category
def get_randomized_questions(category=None):
    connection = sqlite3.connect("quiz_database.db")
    cursor = connection.cursor()

    # Retrieve randomized questions from the quiz table based on the category
    if category:
        cursor.execute("SELECT * FROM quiz WHERE category = ?", (category,))
    else:
        cursor.execute("SELECT * FROM quiz")

    questions = cursor.fetchall()

    connection.close()

    # Shuffle the questions
    random.shuffle(questions)

    return questions

# Function to conduct the quiz with randomized questions
def conduct_randomized_quiz():
    # Ask the user for a category or leave it empty for all categories
    category = input("Enter a category (or leave empty for all categories): ").strip().lower()

    questions = get_randomized_questions(category)
    score = 0
    category_scores = {}

    for question in questions:
        user_answer = input(f"Category: {question[3]}\nQ: {question[1]}\nYour Answer: ").strip().lower()

        if user_answer == question[2].lower():
            print("Correct!\n")
            score += 1
            # Update category-wise score
            category_scores[question[3]] = category_scores.get(question[3], 0) + 1
        else:
            print(f"Wrong! The correct answer is: {question[2]}\n")

    print(f"\nQuiz completed! Your score: {score}/{len(questions)}")

    # Display category-wise scores
    print("\nCategory-wise Scores:")
    for category, category_score in category_scores.items():
        print(f"{category}: {category_score}/{len([q for q in questions if q[3] == category])}")

if __name__ == "__main__":
    # Create the database
    create_quiz_database()

    # Load questions from a CSV file into the database
    csv_file_path = "questions_and_answers.csv"
    load_questions_from_csv(csv_file_path)

    # Conduct the randomized quiz
    conduct_randomized_quiz()

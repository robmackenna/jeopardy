import sqlite3
import csv
import os

def create_and_populate_database(csv_filename):
    try:
        database_exists = os.path.exists("quiz_database.db")

        # Connect to the SQLite database (it will be created if it doesn't exist)
        with sqlite3.connect("quiz_database.db") as connection:
            cursor = connection.cursor()

            # Create the 'quiz' table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quiz (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    category TEXT NOT NULL
                )
            ''')

            # Create the 'categories' table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL
                )
            ''')

            # Commit the changes
            connection.commit()

            if not database_exists:
                print("Empty database created successfully.")

            # Check if the CSV file exists
            if os.path.exists(csv_filename):
                # Read and insert data from the CSV file
                with open(csv_filename, 'r') as csv_file:
                    csv_reader = csv.reader(csv_file)
                    next(csv_reader)  # Skip the header row

                    for row in csv_reader:
                        question, answer, category = map(str.strip, row)

                        # Insert data into the 'quiz' table
                        cursor.execute('''
                            INSERT INTO quiz (question, answer, category) VALUES (?, ?, ?)
                        ''', (question, answer, category))

                        # Insert the category into the 'categories' table if it doesn't exist
                        cursor.execute('''
                            INSERT OR IGNORE INTO categories (category) VALUES (?)
                        ''', (category,))

                # Commit the changes after data insertion
                connection.commit()

                if not database_exists:
                    print("Data inserted successfully.")

            else:
                print(f"CSV file '{csv_filename}' not found. Created an empty database.")

    except Exception as e:
        print(f"Error creating and populating the database: {e}")

if __name__ == '__main__':
    csv_filename = '/home/rob/Documents/projects/jeopardy/jeopardy.csv'
    create_and_populate_database(csv_filename)

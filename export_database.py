import sqlite3
import csv
import os
from datetime import datetime

def export_quiz_data_to_csv(output_filename):
    try:
        # Connect to the SQLite database
        with sqlite3.connect("quiz_database.db") as connection:
            cursor = connection.cursor()

            # Retrieve data from the 'quiz' table
            cursor.execute("SELECT * FROM quiz")
            quiz_data = cursor.fetchall()

            # Check if there is data to export
            if not quiz_data:
                print("No data to export.")
                return

            # Create an empty CSV file if it doesn't exist
            if not os.path.exists(output_filename):
                with open(output_filename, 'w', newline='') as empty_csv_file:
                    # Write an empty header row
                    header = ['id', 'question', 'answer', 'category']
                    csv.writer(empty_csv_file).writerow(header)

                print(f"Empty file created: {output_filename}")

            # Back up existing file
            elif os.path.exists(output_filename):
                backup_filename = f"{output_filename[:-4]}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
                os.rename(output_filename, backup_filename)
                print(f"Existing file backed up to {backup_filename}.")

            # Write data to CSV file
            with open(output_filename, 'w', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)

                # Write header row
                header = ['id', 'question', 'answer', 'category']
                csv_writer.writerow(header)

                # Write data rows
                csv_writer.writerows(quiz_data)

            print(f"Data exported to {output_filename} successfully.")

    except Exception as e:
        print(f"Error exporting data to CSV: {e}")

if __name__ == '__main__':
    output_filename = '/home/rob/Documents/projects/jeopardy/jeopardy_data.csv'
    export_quiz_data_to_csv(output_filename)

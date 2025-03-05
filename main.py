import mysql.connector
from mysql.connector import Error
from abc import ABCMeta, abstractmethod
import secrets

# Database Setup
def connect_to_db():
    try:
        conn = mysql.connector.connect(
                host="127.0.0.1",
                user="root",
                passwd="admin",
                database="dbreg"
        )
        if conn.is_connected():
            return conn, conn.cursor()
    except Error as e:
        print(f"Database connection error: {e}")
        exit()

conn, cursor = connect_to_db()

# Registration
def register_user():
    name = input("Enter your name: ")
    username = input("Create a username: ")
    password = input("Create a password: ")

    while True:
        role = input("Enter your role (Teacher/Student): ").capitalize()
        if role in ['Teacher', 'Student']:
            break
        else:
            print("Invalid role. Please enter 'Teacher' or 'Student'.")

    cursor.execute('INSERT INTO Users (name, username, password, role) VALUES (%s, %s, %s, %s)', (name, username, password, role))
    conn.commit()
    print(f"{role} registered successfully.")

# Login
def login():
    username = input("Username: ")
    password = input("Password: ")

    cursor.execute('SELECT * FROM Users WHERE username = %s AND password = %s', (username, password))
    user = cursor.fetchone()

    if user:
        print(f"\nWelcome {user[1]}! Logged in as {user[4]}.")
        if user[4] == 'Teacher':
            teacher_menu(user)
        elif user[4] == 'Student':
            student_menu(user)
    else:
        print("Invalid credentials.")

# Teacher Menu
def teacher_menu(user):
    while True:
        print("\n--- Teacher Menu ---")
        print("1. Add Subject")
        print("2. Add Grades")
        print("3. Logout")
        choice = input("Select an option: ")

        if choice == '1':
            name = input("Subject Name: ")
            description = input("Subject Description: ")
            schedule = input("Schedule: ")
            cursor.execute('INSERT INTO Subjects (name, description, schedule, teacher_id) VALUES (%s, %s, %s, %s)', (name, description, schedule, user[0]))
            conn.commit()
            print("Subject added successfully.")

        elif choice == '2':
            cursor.execute('SELECT id, name FROM Subjects WHERE teacher_id = %s', (user[0],))
            subjects = cursor.fetchall()
            if not subjects:
                print("No subjects found.")
                continue
            print("Your Subjects:")
            for subj in subjects:
                print(f"{subj[0]}: {subj[1]}")

            subject_id = int(input("Enter subject ID to add grades: "))
            cursor.execute('SELECT id, name FROM Users WHERE role = "Student"')
            students = cursor.fetchall()
            if not students:
                print("No students found.")
                continue
            print("Students:")
            for student in students:
                print(f"{student[0]}: {student[1]}")
            student_id = int(input("Enter student ID: "))
            grade = float(input("Enter grade: "))
            cursor.execute('INSERT INTO Enrollments (student_id, subject_id, grade) VALUES (%s, %s, %s)', (student_id, subject_id, grade))
            conn.commit()
            print("Grade added successfully.")

        elif choice == '3':
            print("Logged out.")
            break
        else:
            print("Invalid option.")

# Student Menu
def student_menu(user):
    while True:
        print("\n--- Student Menu ---")
        print("1. View Schedule")
        print("2. View Enrolled Subjects")
        print("3. View Grades")
        print("4. Logout")
        choice = input("Select an option: ")

        if choice == '1':
            cursor.execute('''
                SELECT s.name, s.schedule FROM Subjects s
                JOIN Enrollments e ON s.id = e.subject_id
                WHERE e.student_id = %s
            ''', (user[0],))
            schedule = cursor.fetchall()
            if schedule:
                print("\nYour Schedule:")
                for subj in schedule:
                    print(f"{subj[0]} - {subj[1]}")
            else:
                print("No enrolled subjects.")

        elif choice == '2':
            cursor.execute('''
                SELECT s.name FROM Subjects s
                JOIN Enrollments e ON s.id = e.subject_id
                WHERE e.student_id = %s
            ''', (user[0],))
            subjects = cursor.fetchall()
            if subjects:
                print("\nEnrolled Subjects:")
                for subj in subjects:
                    print(subj[0])
            else:
                print("No enrolled subjects.")

        elif choice == '3':
            cursor.execute('''
                SELECT s.name, e.grade FROM Subjects s
                JOIN Enrollments e ON s.id = e.subject_id
                WHERE e.student_id = %s
            ''', (user[0],))
            grades = cursor.fetchall()
            if grades:
                print("\nYour Grades:")
                for subj, grade in grades:
                    print(f"{subj}: {grade}")
            else:
                print("No grades available.")

        elif choice == '4':
            print("Logged out.")
            break
        else:
            print("Invalid option.")

# Main Menu
def main_menu():
    while True:
        print("\n--- Welcome to School Management System ---")
        print("1. Login")
        print("2. Register")
        print("3. Exit")
        choice = input("Select an option: ")

        if choice == '1':
            login()
        elif choice == '2':
            register_user()
        elif choice == '3':
            print("Thank you for using the system. Goodbye!")
            break
        else:
            print("Invalid option.")

if __name__ == "_main_":
    try:
        main_menu()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

main_menu()
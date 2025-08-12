"""
db.py — Handles all database operations for the habit tracker.
Requires: sqlite3, datetime, timedelta
Used by: main.py, analytics.py
"""

import sqlite3
import os
from datetime import datetime, timedelta 


def get_db(name=None):
    """
    Connect to the SQLite database.

    :param name: The name of the database file.
    :return: A database connection object.
    """
    if name is None:
        # Check if we're in test mode
        name = os.getenv('DB_PATH', 'habits.db')  # Default to habits.db
    
    db = sqlite3.connect(name)
    return db

def create_tables(db=None):
    """
    Create the necessary tables in the database.
    
    :param db: Optional database connection. If None, uses get_db().
    """
    if db is None:
        db = get_db()  # Use default database for normal operation
    
    cur = db.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY,
            task TEXT NOT NULL,
            periodicity TEXT NOT NULL,
            creation_date TEXT NOT NULL,
            streak INTEGER DEFAULT 0
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            completion_date TEXT NOT NULL,
            FOREIGN KEY (habit_id) REFERENCES habits (id)
        )
    """)
    db.commit()
#Create habit functions

def add_habit(db, task: str, periodicity: str):
    """
    Add a new habit to the database if it doesn't already exist.
    :param db: The database connection.
    :param task: The task or name of the habit.
    :param periodicity: The periodicity of the habit ("daily" or "weekly" or "monthly").
    :return: True if habit was added, False if it already exists.
    """
    cur = db.cursor()
    create_tables(db)  # Ensure tables exist

    cur.execute(
        "INSERT INTO habits (task, periodicity, creation_date) VALUES (?, ?, ?)",
        (task.strip(), periodicity.strip(), str(datetime.now().date()))
    )
    db.commit()
    print(f"Successfully added habit: '{task}' ({periodicity})")
    
def check_habit_exists(db, task: str, periodicity: str):
    """
    Check if a habit already exists in the database.

    :param db: The database connection.
    :param task: The task or name of the habit.
    :param periodicity: The periodicity of the habit ("daily", "weekly", "monthly").
    :return: True if the habit exists, False otherwise.
    """
    cur = db.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM habits WHERE LOWER(task) = LOWER(?) AND LOWER(periodicity) = LOWER(?)",
        (task.strip(), periodicity.strip())
    )
    return cur.fetchone()[0] > 0
    
#Check off functions

def add_completion(db, habit_id: int, completion_date: str = None):
    """
    Add a completion date for a habit and update streak count if necessary.

    :param db: The database connection.
    :param habit_id: The ID of the habit.
    :param completion_date: The date the habit was completed (default: current date).
    """
    today = datetime.now().date()

    if not completion_date:
        completion_date = str(datetime.now().date())

    cur = db.cursor()
    
    #Retrieve habit name  
    cur.execute("SELECT * FROM habits WHERE id=?", (habit_id,))
    row = cur.fetchone()
    if not row:
        print("Habit not found.")
        return
    
    habit_name = row[1]
    habit_data = get_habit_data(db, habit_name)
    if not habit_data:
        print(f"Habit '{habit_name}' not found.")
        return
    periodicity = habit_data['periodicity']
    
    verify = check_last_completion(db, habit_name)

    if not verify:
        print(f"\nHabit {habit_name} already checked for {periodicity} ")
        return
    else:
        cur.execute(
            "INSERT INTO completions (habit_id, completion_date) VALUES (?, ?)",
            (habit_id, completion_date)
        )
        db.commit()
        print (f"Habit checked for the period")

def check_last_completion(db, habit_name, last_completion_date=None):
    """
    Compares the last completion date of a habit with the current date
    and returns whether the habit can be checked off again based on its periodicity.

    :param db: The database connection.
    :param habit_name: The name of the habit to check.
    :param last_completion_date: The date of the last completion.
    :param today: The current date.    
    :param periodicity: The periodicity of the habit ("daily", "weekly", "monthly").

    :return: A dictionary with the periodicity data.
    """
    # Get habit data from the database
    habit_data = get_habit_data(db, habit_name)
    if not habit_data:
        print(f"Habit '{habit_name}' not found.")
        return None
    
    today = datetime.now().date()

    periodicity = habit_data.get('periodicity')
    last_completion_date = habit_data.get('last_completion_date')

    if not last_completion_date:
        return True
    
    
    last_completion_date = datetime.strptime(last_completion_date, "%Y-%m-%d").date()

   
    #Build week range
    start_of_week = today - timedelta(days=today.weekday())  # Start of the week (Monday)
    week = [start_of_week + timedelta(days=i) for i in range(7)]  # Mon–Sun
    
    # Build month range
    start_of_month = today.replace(day=1)  # First day of the current month
    # Get the first day of the next month
    if today.month == 12:
        next_month = today.replace(year=today.year + 1, month=1, day=1)
    else:
        next_month = today.replace(month=today.month + 1, day=1)
    num_days = (next_month - start_of_month).days
    month = [start_of_month + timedelta(days=i) for i in range(num_days)]

    # Check if the habit can be checked off again based on its periodicity
    if not periodicity:
        print("No periodicity provided.")
        return None
    if not last_completion_date:
        return True
    

    if periodicity == "daily":
        if last_completion_date == today:
            return False
        else :
            return True
    elif periodicity == "weekly": 
        if last_completion_date in week:
            return False
        else:
            return True
    elif periodicity == "monthly":
        if last_completion_date in month:
            return False
        else:
            return True

def get_habit_data(db, habit_identifier):
    """
    Retrieve a habit's name, periodicity, current_streak and last completion date.

    :param db: SQLite DB connection
    :param habit_identifier: Either the habit name (str) or ID (int)
    :return: dict with name, periodicity, current_streak and last completion date
    """
    cur = db.cursor()
    if isinstance(habit_identifier, int):
        cur.execute("SELECT id, task, periodicity, creation_date, streak FROM habits WHERE id = ?", (habit_identifier,))
    else:
        cur.execute("SELECT id, task, periodicity, creation_date, streak FROM habits WHERE task = ?", (habit_identifier,))

    habit = cur.fetchone()
    if not habit:
        return {"error": "Habit not found."}

    habit_id, task, periodicity, creation_date, streak = habit

    # Get last completion date
    cur.execute(
        "SELECT completion_date FROM completions WHERE habit_id = ? ORDER BY completion_date DESC LIMIT 1",
        (habit_id,)
    )
    last = cur.fetchone()
    last_completion = last[0] if last else None

    return {
        "id": habit_id,
        "name": task,
        "periodicity": periodicity,
        "current_streak": streak,
        "creation_date": creation_date,
        "last_completion_date": last_completion
    }
   

def get_all_habits(db):
    """
    Retrieve a list of all habits from the database.

    :param db: The database connection.
    :return: A list of all habits as tuples (id, task, periodicity, creation_date, streak).
    """
    cur = db.cursor()
    cur.execute("SELECT * FROM habits")
    habits = cur.fetchall()
    return habits 

def get_habits_list(db):
    """
    Retrieve a list of all habits' names from the database.

    :param db: The database connection.
    :return: A list of all habits.
    """
    cur = db.cursor()
    cur.execute("SELECT * FROM habits")
    habits = cur.fetchall()
    # Convert to a list of dictionaries for easier access
    habit_list = []
    for habit in habits:
        habit_name = habit[1]
        habit_list.append(habit_name)
    return habit_list

def get_completions(db, habit_id: int):
    """
    Retrieve all completion dates for a specific habit.

    :param db: The database connection.
    :param habit_id: The ID of the habit.
    :return: A list of completion dates.
    """
    cur = db.cursor()
    cur.execute("SELECT completion_date FROM completions WHERE habit_id=?", (habit_id,))
    return [row[0] for row in cur.fetchall()]



def delete_habit(db, habit_name):

    """
    Delete a habit and its completion records from the database.
    """
    # Delete completions first to avoid foreign key constraint issues
   
    # Assuming habit_name is unique
    # Delete completions associated with the habit
    db.execute("DELETE FROM habits WHERE task = ?", (habit_name,))
    db.commit()

def reset_database(db):
    """
    Deletes all habits and completions from the database.
    Also resets the ID counters for both tables.
     """
    cur = db.cursor()
    cur.execute("DELETE FROM completions")
    cur.execute("DELETE FROM habits")
    cur.execute("DELETE FROM sqlite_sequence WHERE name='habits'")
    cur.execute("DELETE FROM sqlite_sequence WHERE name='completions'")
    db.commit()
    print("Database reset: All habits and completions deleted, ID counters reset.")



def add_streak_column_if_missing(db):
    cursor = db.cursor()
    # Check if 'streak' column exists
    cursor.execute("PRAGMA table_info(habits)")
    columns = [col[1] for col in cursor.fetchall()]
    if "streak" not in columns:
        cursor.execute("ALTER TABLE habits ADD COLUMN streak INTEGER DEFAULT 0")
        db.commit()




import sqlite3
from datetime import datetime, timedelta 

def get_db(name="my_database.db"):
    """
    Connect to the SQLite database.

    :param name: The name of the database file.
    :return: A database connection object.
    """
    db = sqlite3.connect(name)
    return db

def create_tables(db):
    """
    Create the necessary tables in the database.
    """
    cur = db.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            periodicity TEXT NOT NULL,
            creation_date TEXT NOT NULL
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

def add_habit(db, task: str, periodicity: str):
    """
    Add a new habit to the database.

    :param db: The database connection.
    :param task: The task or name of the habit.
    :param periodicity: The periodicity of the habit ("daily" or "weekly").
    """
    cur = db.cursor()
    cur.execute(
        "INSERT INTO habits (task, periodicity, creation_date) VALUES (?, ?, ?)",
        (task, periodicity, str(datetime.now().date()))
    )
    db.commit()

def add_completion(db, habit_id: int, completion_date: str = None):
    """
    Add a completion date for a habit.

    :param db: The database connection.
    :param habit_id: The ID of the habit.
    :param completion_date: The date the habit was completed (default: current date).
    """
    today = datetime.now().date()

    if not completion_date:
        completion_date = str(datetime.now().date())

    #Get habit periodicity
    cur = db.cursor()
    cur.execute(
        "SELECT periodicity FROM habits WHERE id=?", (habit_id,)
    )
    habit = cur.fetchone()
    if not habit:
        print("Habit not found.")
        return

    periodicity = habit[0]

    # Get last completion date
    cur.execute("SELECT completion_date FROM completions WHERE habit_id=? ORDER BY completion_date DESC LIMIT 1", (habit_id,))
    last_completion = cur.fetchone()
    last_completion_date = datetime.strptime(last_completion[0], "%Y-%m-%d").date() if last_completion else None

  # Determine the period start
    if periodicity == "daily":
        period_start = today
    elif periodicity == "weekly":
        period_start = today - timedelta(days=today.weekday())  # Start of the week (Monday)

    
    # Check if the habit was already completed in the current period
    if last_completion_date and last_completion_date >= period_start:
        print(f"Habit already completed for the current {periodicity} period.")
        return

    cur.execute(
        "INSERT INTO completions (habit_id, completion_date) VALUES (?, ?)",
        (habit_id, completion_date)
    )
    db.commit()
    print (f"Habit checked for {periodicity} period")

def get_all_habits(db):
    """
    Retrieve all habits from the database.

    :param db: The database connection.
    :return: A list of all habits.
    """
    cur = db.cursor()
    cur.execute("SELECT * FROM habits")
    return cur.fetchall()

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

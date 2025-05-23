import sqlite3
from datetime import datetime, timedelta 
import questionary

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
            id INTEGER PRIMARY KEY,
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
    elif periodicity == "monthly":
        period_start = today.replace(day=1)  # First day of the current month
    else:
        print("Unknown periodicity.")
        return
        
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

def select_habit(db):
    # Get list of habit names from the DB
    habits = get_all_habits(db)  # returns e.g. ["Drink Water", "Workout", "Meditate"]

    if not habits:
        print("No habits found. Please add a habit first.")
        return None

    selected = questionary.select(
        "Select a habit:",
        choices = habits
    ).ask()

    return selected

def get_habit_by_name(habit_name):
    """
    Retrieve a habit's name and periodicity from the database.
    Returns a dictionary or None if the habit doesn't exist.
    """

    conn = get_db()

    cursor = conn.execute(
        "SELECT name, periodicity FROM habits WHERE name = ?",
        (habit_name,)
    )
    row = cursor.fetchone()
    if row:
        return {"name": row[0], "periodicity": row[1]}
    return None

def get_periodicity(habit_name):
    """
    Retrieve a habit's periodicity from the database.
    Returns the periodicity or None if the habit doesn't exist.
    """
    conn = get_db()

    cursor = conn.execute(
        "SELECT periodicity FROM habits WHERE task = ?",
        (habit_name,)
    )
    row = cursor.fetchone()
    if row:
        return {"periodicity": row[0]}
    return None

def get_longest_overall_streak(db):
    """
    Retrieve the longest streak across all habits.
    """
    cur = db.cursor()
    cur.execute("SELECT MAX(streak) FROM completions")
    return cur.fetchone()

def get_max_streak_ofHabit( completions, periodicity):
   
    if not completions:
        return 0, None, None, 0

    sorted_dates = sorted(datetime.strptime(d, "%Y-%m-%d").date() for d in completions)
    max_streak = streak = 1
    breaks = 0

    start_date = current_start = sorted_dates[0]
    end_date = sorted_dates[0]

    for i in range(1, len(sorted_dates)):
        expected = timedelta(days=1) if periodicity == "daily" else timedelta(weeks=1)
        if sorted_dates[i] - sorted_dates[i - 1] == expected:
            streak += 1
            end_date = sorted_dates[i]
        else:
            breaks += 1
            if streak > max_streak:
                max_streak = streak
                start_date = current_start
                end_date = sorted_dates[i - 1]
            streak = 1
            current_start = sorted_dates[i]

    # Final check after loop
    if streak > max_streak:
        max_streak = streak
        start_date = current_start
        end_date = sorted_dates[-1]

    return max_streak, start_date, end_date, breaks

def get_greatest_overall_streak(db):
    habits = get_all_habits(db)
    best_streak = 0
    best_habit = None
    best_start = None
    best_end = None
    best_breaks = 0

    for habit in habits:
        habit_id, name, periodicity, _ = habit
        completions = get_completions(db, habit_id)
        streak, start, end, breaks = get_max_streak_ofHabit(completions, periodicity)
        
        if streak > best_streak:
            best_streak = streak
            best_habit = name
            best_start = start
            best_end = end
            best_breaks = breaks

    return {
        "habit": best_habit,
        "streak": best_streak,
        "start_date": best_start,
        "end_date": best_end,
        "breaks": best_breaks
    }

def delete_habit(habit_id):
    """
    Delete a habit and its completion records from the database.
    """
    # Delete completions first to avoid foreign key constraint issues
    conn = get_db()
    # Assuming habit_name is unique
    # Delete completions associated with the habit
    conn.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
    conn.commit()
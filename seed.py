import sqlite3
from datetime import datetime, timedelta
import random
from db import get_db, add_habit, add_completion, reset_database



def seed_demo_data():
    '''
    Wipes and resets database and inserts 5 habits(daily/weekly/monthly)
    Adds  realistic completions (with some randomness)
    Ensure “Read Stoicism” has no breaks for clean streak testing

    : param: None
    : return: None
    '''

     # Connect to the SQLite database
    db = get_db()
    cursor = db.cursor()

    """Sets up a fresh habits.db with realistic checkoffs and a perfect streak for 'Drink Water'."""
  

    habits = [
        ("Drink Water", "daily"),
        ("Workout", "weekly"),
        ("Meditate", "daily"),
        ("Clean Room", "weekly"),
        ("Pay Bills", "monthly")
    ]

    habit_ids = {}
    for name, periodicity in habits:
        add_habit(db, name, periodicity)
        habit_id = db.execute("SELECT id FROM habits WHERE task = ?", (name,)).fetchone()[0]
        habit_ids[name] = habit_id

    start_date = (datetime.now() - timedelta(days=28)).date()
    today = datetime.now().date()

    # Special handling: "Drink Water" gets perfect streak
    habit_id = habit_ids["Drink Water"]
    current_date = start_date
    while current_date <= today:
        add_completion(db, habit_id, current_date.isoformat())
        print(f"Drink Water (perfect streak) on {current_date}")
        current_date += timedelta(days=1)
    

    # Other habits: realistic, imperfect streaks
    for name, periodicity in habits:
        if name == "Drink Water":
            continue  # Already handled

        habit_id = habit_ids[name]
        current_date = start_date

        if periodicity == "daily":
            while current_date <= today:
                if random.random() > 0.1: #
                    add_completion(db, habit_id, current_date.isoformat())
                    print(f"{name} on {current_date} for periodicity {periodicity}")
                current_date += timedelta(days=1)

        elif periodicity == "weekly":
            current_date += timedelta(days=(6 - current_date.weekday()) % 7)  # next Sunday
            while current_date <= today:
                if random.random() > 0.2:
                    add_completion(db, habit_id, current_date.isoformat())
                    print(f"{name} on {current_date} for periodicity {periodicity}")
                current_date += timedelta(days=7)

        elif periodicity == "monthly":
            while current_date <= today:
                add_completion(db, habit_id, current_date.isoformat())
                print(f" {name} on {current_date} for periodicity {periodicity}")
                current_date += timedelta(days=28)

    return db

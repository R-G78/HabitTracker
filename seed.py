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

    reset_database(db)  # Clears and recreates tables
    today = datetime.today().date()

    # Predefined habits
    habits = [
        ("Drink Water", "daily"),           
        ("Workout", "weekly"),             
        ("Read Stoicism", "daily"),         
        ("Clean Room", "weekly"),           
        ("Pay Bills", "monthly")
    ]


    habit_ids = {}

   # Add habits
    for name, periodicity in habits:
        add_habit(db, name, periodicity)
        habit_id = cursor.execute("SELECT id FROM habits WHERE task = ?", (name,)).fetchone()[0]
        habit_ids[name] = habit_id

    # Generate completions
    for name, period in habits:
        habit_id = habit_ids[name] 
        start_date = today - timedelta(days=120)

        completions = []

        if name == "Read Stoicism":
            # Clean daily streak for testing
            for i in range(30):
                completions.append((start_date + timedelta(days=i)).isoformat())

        elif period == "daily":
            current = start_date
            while current <= today:
                if random.random() > 0.1:  # ~90% completion rate
                    completions.append(current.isoformat())
                current += timedelta(days=1)

        elif period == "weekly":
            current = start_date
            while current <= today:
                if random.random() > 0.2:  # ~80% completion rate
                    completions.append(current.isoformat())
                current += timedelta(days=7)

        elif period == "monthly":
            current = start_date
            while current <= today:
                if random.random() > 0.3:  # ~70% completion rate
                    completions.append(current.isoformat())
                current += timedelta(days=30)

        for date in completions:
            add_completion(db, habit_id)
            print(f"Demo data seeded successfully for {habit_id}.")
import os
import pytest 
from db import get_db, create_tables, add_habit, add_completion
from counter import Habit
from datetime import datetime, timedelta
import random
from analyse import get_habits_by_periodicity, get_longest_streak_all, get_longest_streak_habit, calculate_streak


@pytest.fixture
def temp_db():
    """Fixture to create a temporary SQLite database for testing."""
    db_filename = "temp_test.db"
    if os.path.exists(db_filename):
        os.remove(db_filename)
    
    db = get_db(db_filename)
    create_tables(db)
    yield db

    db.close()
    if os.path.exists(db_filename):
        os.remove(db_filename)

def test_create_increment_delete(temp_db):
    """Test creating and deleting a habit in the temporary database."""
    db = temp_db
    # Create a habit
    add_habit(db, "Test Habit", "daily")
    habits = db.execute("SELECT * FROM habits").fetchall()
    assert len(habits) == 1
    assert habits[0][1] == "Test Habit"
    assert habits[0][2] == "daily"
    print ("Test habit created successfully.")

    # Check if the habit exists
    habit = db.execute("SELECT * FROM habits WHERE task = 'Test Habit'").fetchone()
    assert habit is not None
    assert habit[1] == "Test Habit"
    assert habit[2] == "daily"
    print ("Test habit exists in the database.")

    # Increment the habitpytest -s test_independent.py
    habit_id = habit[0]
    add_completion(db, habit_id, datetime.now().strftime("%Y-%m-%d"))
    completions = db.execute("SELECT * FROM completions WHERE habit_id = ?", (habit_id,)).fetchall()
    assert len(completions) == 1

    assert completions[0][1] == habit_id
    print ("Test habit incremented successfully.")

    # Delete the habit
    db.execute("DELETE FROM habits WHERE task = 'Test Habit'")
    db.commit()
    habits = db.execute("SELECT * FROM habits").fetchall()
    assert len(habits) == 0
    print ("Test habit deleted successfully.")
    # Check if the habit is deleted
    habit = db.execute("SELECT * FROM habits WHERE task = 'Test Habit'").fetchone()
    assert habit is None
    print ("Test habit no longer exists in the database.")

@pytest.fixture
def temp_db_setup(temp_db):
    """Setup temporary data for testing."""
    """Sets up a fresh habits.db with 5 habits and 4 months of checkoffs."""
   
    db = temp_db
    

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

    start_date = datetime.now() - timedelta(days=120)
    for offset in range(121):
        current_date = start_date + timedelta(days=offset)
        date_str = current_date.strftime("%Y-%m-%d")
        for name, periodicity in habits:
            habit_id = habit_ids[name]
            if periodicity == "daily" and random.random() < 0.9:
                add_completion(db, habit_id, date_str)
            elif periodicity == "weekly" and current_date.weekday() == 6 and random.random() < 0.95:
                add_completion(db, habit_id, date_str)
            elif periodicity == "monthly" and current_date.day == 1 and random.random() < 0.98:
                add_completion(db, habit_id, date_str)

    return db



def test_increment_constraints(temp_db_setup):
    db = temp_db_setup

    # Get a daily habit with a checkoff
    daily_habit = db.execute("SELECT id FROM habits WHERE periodicity = 'daily'").fetchone()[0]
    daily_date = db.execute("SELECT completion_date FROM completions WHERE habit_id = ?", (daily_habit,)).fetchone()[0]
    
    # Try to check off again on the same day
    result = add_completion(db, daily_habit, daily_date)
    assert not result, "Should not allow checking off a daily habit on the same day again."

    # Get a weekly habit and its checkoff
    weekly_habit = db.execute("SELECT id FROM habits WHERE periodicity = 'weekly'").fetchone()[0]
    weekly_date = db.execute("SELECT completion_date FROM completions WHERE habit_id = ?", (weekly_habit,)).fetchone()[0]
    week_date_obj = datetime.strptime(weekly_date, "%Y-%m-%d")
    same_week_date = (week_date_obj + timedelta(days=2)).strftime("%Y-%m-%d")

    # Try to check off again in the same week
    result = add_completion(db, weekly_habit, same_week_date)
    assert not result, "Should not allow checking off a weekly habit in the same week again."
    # Check if the completion was not added
    completions = db.execute("SELECT * FROM completions WHERE habit_id = ? AND completion_date = ?", (weekly_habit, same_week_date)).fetchall()
    

    # Get a monthly habit and its checkoff
    monthly_habit = db.execute("SELECT id FROM habits WHERE periodicity = 'monthly'").fetchone()[0]
    monthly_date = db.execute("SELECT completion_date FROM completions WHERE habit_id = ?", (monthly_habit,)).fetchone()[0]
    month_date_obj = datetime.strptime(monthly_date, "%Y-%m-%d")
    same_month_date = (month_date_obj + timedelta(days=10)).strftime("%Y-%m-%d")

    # Try to check off again in the same month
    result = add_completion(db, monthly_habit, same_month_date)
    assert not result, "Should not allow checking off a monthly habit in the same month again."
    

def test_show_monthlies(temp_db_setup):
    db = temp_db_setup
    results = db.execute("""
        SELECT habits.task, completions.completion_date
        FROM completions
        JOIN habits ON habits.id = completions.habit_id
        WHERE habits.periodicity = 'monthly'
    """).fetchall()

    print("\nMonthly Checkoffs:")
    for name, date in results:
        print(f"{name} - {date}")

    assert len(results) >= 3  # Should have ~4 if data spans 4 months

def test_analyse_specific_habit():
    pass

def temp_db_close(temp_db):
     db, db_filename = temp_db
     db.close()
     if os.path.exists(db_filename):
         os.remove(db_filename)
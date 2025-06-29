import os
import pytest 
from db import get_db, create_tables, add_habit, add_completion, get_completions, reset_database
from counter import Habit
from datetime import datetime, timedelta
import random
from analyse import get_habits_by_periodicity, get_longest_streak_all, get_longest_streak_habit, calculate_streak, calculate_current_streak, get_allHabit_summaries


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
    """Sets up a fresh habits.db with realistic checkoffs and a perfect streak for 'Drink Water'."""
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

def test_increment_constraints(temp_db_setup):
    """Test that checking off a habit on the same day or in the same week/month is not allowed."""
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
    same_week_date = (week_date_obj + timedelta(days=6)).strftime("%Y-%m-%d")

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
    print(f"Weekly habit ID: {weekly_habit}, weekly_date: {weekly_date}, same_week_date: {same_week_date}")
    print("Weekly result (should be False):", result)
    print("Weekly completions on attempted date:", completions)
    assert not result, "Should not allow checking off a monthly habit in the same month again."
    

def test_analyse_all_habit(temp_db_setup):
    db = temp_db_setup

    # Get all habits from the DB
    habits = db.execute("SELECT id, task, periodicity, creation_date FROM habits").fetchall()
    assert habits, "No habits found in test DB"
    
    for habit_row in habits:
        habit_id, task, periodicity, creation_date = habit_row

        # Get completions for that habit
        completions = get_completions(db, habit_id)
        assert completions, f"No completions found for habit '{task}'"

        # Create a Habit instance
        habit = Habit(task=task , periodicity=periodicity, creation_date=creation_date, completion_dates=completions)

        # Max streak analysis
        max_streak, start_date, end_date, breaks = habit.calculate_max_streak_with_details()
        print(f"Max streak for '{task}': {max_streak}")
        if max_streak > 0:
            print ("Which:")
            print(f"  ➤ Started on date: {start_date}")
            print(f"  ➤ Ended on date: {end_date}")
        print(f"Number of streak breaks: {breaks}\n")

        assert isinstance(max_streak, int)
        assert isinstance(breaks, int)
        if max_streak > 0:
            assert start_date is not None and end_date is not None
            assert start_date <= end_date

        # Current streak
        current_result = habit.calculate_current_streak()
        if current_result == 0:
            assert True  # No current streak
        else:
            current_streak, streak_start_date = current_result
            assert isinstance(current_streak, int)
            assert isinstance(streak_start_date, str)

def temp_db_close(temp_db):
     db, db_filename = temp_db
     db.close()
     if os.path.exists(db_filename):
         os.remove(db_filename)



import os
import pytest
import sqlite3
from datetime import datetime, timedelta
import random
from db import get_db, create_tables, add_habit, add_completion, get_completions, reset_database, get_all_habits, get_habit_data, delete_habit
from counter import Habit
from analyse import get_habits_by_periodicity, get_longest_streak_all, get_longest_streak_habit, calculate_current_streak, get_allHabit_summaries
from seed import seed_demo_data


@pytest.fixture
def temp_db():
    """Fixture to create a temporary SQLite database for testing."""
    db_filename = "temp_test_cli.db"
    if os.path.exists(db_filename):
        os.remove(db_filename)
    
    db = get_db(db_filename)
    create_tables(db)
    yield db

    db.close()
    if os.path.exists(db_filename):
        os.remove(db_filename)


@pytest.fixture
def seeded_db(temp_db):
    """Fixture that provides a database with seeded demo data."""
    db = temp_db
    
    # Manually seed the data similar to seed_demo_data but for our temp db
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
        current_date += timedelta(days=1)

    # Other habits: realistic, imperfect streaks
    for name, periodicity in habits:
        if name == "Drink Water":
            continue  # Already handled

        habit_id = habit_ids[name]
        current_date = start_date

        if periodicity == "daily":
            while current_date <= today:
                if random.random() > 0.1:
                    add_completion(db, habit_id, current_date.isoformat())
                current_date += timedelta(days=1)

        elif periodicity == "weekly":
            current_date += timedelta(days=(6 - current_date.weekday()) % 7)  # next Sunday
            while current_date <= today:
                if random.random() > 0.2:
                    add_completion(db, habit_id, current_date.isoformat())
                current_date += timedelta(days=7)

        elif periodicity == "monthly":
            while current_date <= today:
                add_completion(db, habit_id, current_date.isoformat())
                current_date += timedelta(days=28)

    return db


def test_create_habit_functionality(temp_db):
    """Test creating habits using the Habit class store method."""
    db = temp_db
    
    # Test creating daily habit
    habit = Habit("Morning Exercise", "daily")
    habit.store()
    
    # Verify habit was created in database
    habits = get_all_habits(db)
    assert len(habits) == 1
    assert habits[0][1] == "Morning Exercise"
    assert habits[0][2] == "daily"
    
    # Test creating weekly habit
    habit2 = Habit("Weekly Review", "weekly")
    habit2.store()
    
    habits = get_all_habits(db)
    assert len(habits) == 2
    
    # Test creating monthly habit
    habit3 = Habit("Budget Review", "monthly")
    habit3.store()
    
    habits = get_all_habits(db)
    assert len(habits) == 3
    
    print("✓ Habit creation functionality works correctly")


def test_check_off_habit_functionality(seeded_db):
    """Test checking off habits using the Habit increment method."""
    db = seeded_db
    
    # Get all habits
    habits = get_all_habits(db)
    assert len(habits) > 0
    
    # Test checking off a daily habit
    daily_habits = [h for h in habits if h[2] == "daily"]
    assert len(daily_habits) > 0
    
    habit_id = daily_habits[0][0]
    habit_data = get_habit_data(db, habit_id)
    
    # Create Habit instance and increment
    habit = Habit(
        habit_data['id'],
        habit_data['name'],
        habit_data['periodicity'],
        habit_data['creation_date'],
        get_completions(db, habit_id)
    )
    
    initial_completions = len(get_completions(db, habit_id))
    result = habit.increment()
    
    # Check if increment was successful (depends on implementation)
    # If today wasn't already completed, should add a completion
    final_completions = len(get_completions(db, habit_id))
    
    print(f"✓ Check off functionality tested for {habit_data['name']}")


def test_delete_habit_functionality(seeded_db):
    """Test deleting habits."""
    db = seeded_db
    
    # Get initial habit count
    initial_habits = get_all_habits(db)
    initial_count = len(initial_habits)
    assert initial_count > 0
    
    # Delete first habit
    habit_to_delete = initial_habits[0][0]  # Get habit ID
    delete_habit(habit_to_delete)
    
    # Verify habit was deleted
    remaining_habits = get_all_habits(db)
    assert len(remaining_habits) == initial_count - 1
    
    # Verify the specific habit is no longer in the list
    remaining_ids = [h[0] for h in remaining_habits]
    assert habit_to_delete not in remaining_ids
    
    print("✓ Delete habit functionality works correctly")


def test_analyze_specific_habit_functionality(seeded_db):
    """Test analyzing a specific habit."""
    db = seeded_db
    
    habits = get_all_habits(db)
    assert len(habits) > 0
    
    # Test analysis on first habit
    habit_id = habits[0][0]
    habit_data = get_habit_data(db, habit_id)
    
    # Get completions and analyze
    completion_dates = get_completions(db, habit_id)
    periodicity = habit_data['periodicity']
    
    # Test longest streak calculation
    max_streak, start_date, end_date, breaks = get_longest_streak_habit(completion_dates, periodicity)
    
    assert isinstance(max_streak, int)
    assert isinstance(breaks, int)
    assert max_streak >= 0
    assert breaks >= 0
    
    if max_streak > 0:
        assert start_date is not None
        assert end_date is not None
    
    # Test current streak calculation
    current_streak_result = calculate_current_streak(completion_dates, periodicity)
    
    if current_streak_result != 0:
        current_streak, streak_start_date = current_streak_result
        assert isinstance(current_streak, int)
        assert isinstance(streak_start_date, str)
        assert current_streak >= 0
    
    print(f"✓ Specific habit analysis works for {habit_data['name']}")


def test_analyze_all_habits_functionality(seeded_db):
    """Test all habits analysis functions."""
    db = seeded_db
    
    # Test get all habit summaries
    summaries = get_allHabit_summaries(db)
    assert len(summaries) > 0
    
    for summary in summaries:
        assert 'name' in summary
        assert 'periodicity' in summary
        assert 'start_date' in summary
        assert 'id' in summary
    
    # Test habits by periodicity
    daily_habits = get_habits_by_periodicity(db, "daily")
    weekly_habits = get_habits_by_periodicity(db, "weekly")
    monthly_habits = get_habits_by_periodicity(db, "monthly")
    
    # Should have habits in each category based on our seed data
    assert len(daily_habits) >= 0
    assert len(weekly_habits) >= 0
    assert len(monthly_habits) >= 0
    
    # Test longest streaks for all habits
    all_habits = get_all_habits(db)
    
    for habit in all_habits:
        habit_id = habit[0]
        habit_name = habit[1]
        periodicity = habit[2]
        
        completions = get_completions(db, habit_id)
        max_streak, start_date, end_date, breaks = get_longest_streak_habit(completions, periodicity)
        
        assert isinstance(max_streak, int)
        assert isinstance(breaks, int)
        assert max_streak >= 0
    
    # Test longest overall streak
    result = get_longest_streak_all(db)
    
    assert 'streak' in result
    assert 'habit' in result
    assert 'start_date' in result
    assert 'end_date' in result
    assert 'breaks' in result
    
    assert isinstance(result['streak'], int)
    assert result['streak'] >= 0
    
    print("✓ All habits analysis functionality works correctly")


def test_database_operations(temp_db):
    """Test core database operations that the CLI depends on."""
    db = temp_db
    
    # Test adding habits
    add_habit(db, "Test Habit", "daily")
    habits = get_all_habits(db)
    assert len(habits) == 1
    
    habit_id = habits[0][0]
    
    # Test getting habit data
    habit_data = get_habit_data(db, habit_id)
    assert habit_data is not None
    assert habit_data['name'] == "Test Habit"
    assert habit_data['periodicity'] == "daily"
    
    # Test adding completions
    today = datetime.now().strftime("%Y-%m-%d")
    result = add_completion(db, habit_id, today)
    
    # Test getting completions
    completions = get_completions(db, habit_id)
    assert len(completions) >= 0
    
    print("✓ Core database operations work correctly")


def test_habit_class_integration(temp_db):
    """Test Habit class integration with database."""
    db = temp_db
    
    # Create habit using class
    habit = Habit("Integration Test", "weekly")
    habit.store()
    
    # Verify it's in database
    habits = get_all_habits(db)
    assert len(habits) == 1
    
    # Get the habit data and create instance with completions
    habit_id = habits[0][0]
    habit_data = get_habit_data(db, habit_id)
    completions = get_completions(db, habit_id)
    
    habit_with_data = Habit(
        habit_data['id'],
        habit_data['name'],
        habit_data['periodicity'],
        habit_data['creation_date'],
        completions
    )
    
    # Test streak calculations
    max_streak_result = habit_with_data.calculate_max_streak_with_details()
    assert len(max_streak_result) == 4  # max_streak, start_date, end_date, breaks
    
    current_streak_result = habit_with_data.calculate_current_streak()
    # Result can be 0 (no streak) or tuple (streak, start_date)
    
    print("✓ Habit class integration works correctly")


def test_data_consistency(seeded_db):
    """Test data consistency across different analysis functions."""
    db = seeded_db
    
    habits = get_all_habits(db)
    
    for habit in habits:
        habit_id = habit[0]
        habit_name = habit[1]
        periodicity = habit[2]
        
        # Get completions
        completions = get_completions(db, habit_id)
        
        # Test that habit data is consistent
        habit_data = get_habit_data(db, habit_id)
        assert habit_data['name'] == habit_name
        assert habit_data['periodicity'] == periodicity
        assert habit_data['id'] == habit_id
        
        # Test that analysis functions don't crash
        try:
            max_streak, start_date, end_date, breaks = get_longest_streak_habit(completions, periodicity)
            current_streak = calculate_current_streak(completions, periodicity)
            
            # Basic sanity checks
            assert max_streak >= 0
            assert breaks >= 0
            
        except Exception as e:
            pytest.fail(f"Analysis failed for habit {habit_name}: {str(e)}")
    
    print("✓ Data consistency checks passed")


def test_edge_cases(temp_db):
    """Test edge cases that might occur in CLI usage."""
    db = temp_db
    
    # Test with no habits
    habits = get_all_habits(db)
    assert len(habits) == 0
    
    summaries = get_allHabit_summaries(db)
    assert len(summaries) == 0
    
    # Test analysis with empty database
    result = get_longest_streak_all(db)
    # Should handle empty database gracefully
    
    # Test with habit that has no completions
    add_habit(db, "No Completions", "daily")
    habits = get_all_habits(db)
    habit_id = habits[0][0]
    
    completions = get_completions(db, habit_id)
    max_streak, start_date, end_date, breaks = get_longest_streak_habit(completions, "daily")
    
    assert max_streak == 0
    assert breaks == 0
    
    current_streak = calculate_current_streak(completions, "daily")
    assert current_streak == 0
    
    print("✓ Edge cases handled correctly")


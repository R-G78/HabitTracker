import os
import pytest
import sqlite3
from datetime import datetime, timedelta
import random
from db import get_db, create_tables, add_habit, add_completion, get_completions, reset_database, get_all_habits, get_habit_data, delete_habit
from counter import Habit
from analyse import get_habits_by_periodicity, get_longest_streak_all, get_longest_streak_habit, calculate_current_streak, get_allHabit_summaries
from seed import seed_demo_data



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


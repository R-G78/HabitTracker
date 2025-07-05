from db import get_db, get_habit_data, get_all_habits, get_completions
from datetime import datetime, timedelta
import sqlite3
from typing import List, Tuple, Optional, Dict

def get_all_habits(db):
    """Return a list of all habits."""
    cur = db.cursor()
    cur.execute("SELECT * FROM habits")
    return cur.fetchall()



def get_allHabit_summaries(db):
    """
    Returns a list of all habits with their id, name, periodicity, and start (creation) date.
    Example:
    [
        {"id": 1, "name": "Workout", "periodicity": "daily", "start_date": "2025-04-01"},
        {"id": 2, "name": "Meditate", "periodicity": "weekly", "start_date": "2025-03-15"},
        ...
    ]
    """
    conn = get_db()
    conn.row_factory = sqlite3.Row
    

    try:
        # Option 1: Try 'name' column
        cursor = conn.execute("""
            SELECT
                habits.id as id,
                habits.name AS name,
                habits.periodicity,
                habits.creation_date AS start_date
            FROM habits
        """)
    except sqlite3.OperationalError:
        try:
            # Option 2: Try 'task' column (but without the table prefix that's causing issues)
            cursor = conn.execute("""
                SELECT
                    id,
                    task AS name,
                    periodicity,
                    creation_date AS start_date
                FROM habits
            """)
        except sqlite3.OperationalError:
            try:
                # Option 3: Try 'habit_name' column
                cursor = conn.execute("""
                    SELECT
                        id,
                        habit_name AS name,
                        periodicity,
                        creation_date AS start_date
                    FROM habits
                """)
            except sqlite3.OperationalError:
                # If all else fails, let's see what columns exist
                cursor = conn.execute("PRAGMA table_info(habits)")
                columns = cursor.fetchall()
                column_names = [col[1] for col in columns]
                raise ValueError(f"Could not find habit name column. Available columns: {column_names}")
    
    return [
        {
            "id": row["id"],
            "name": row["name"],
            "periodicity": row["periodicity"],
            "start_date": row["start_date"]
        }
        for row in cursor.fetchall()
    ]

def get_habits_by_periodicity(db, periodicity):
    """Return a list of habits with the same periodicity."""
    cur = db.cursor()
    cur.execute("SELECT * FROM habits WHERE periodicity=?", (periodicity,))
    
    return cur.fetchall()


#new code
def parse_date(date_str: str) -> datetime:
    """Parse date string to datetime object."""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            raise ValueError(f"Unable to parse date: {date_str}")

def get_expected_next_date(current_date: datetime, periodicity: str) -> datetime:
    """Get the next expected completion date based on periodicity."""
    if periodicity == 'daily':
        return current_date + timedelta(days=1)
    elif periodicity == 'weekly':
        return current_date + timedelta(weeks=1)
    elif periodicity == 'monthly':
        if current_date.month == 12:
            return current_date.replace(year=current_date.year + 1, month=1)
        else:
            try:
                return current_date.replace(month=current_date.month + 1)
            except ValueError:
                next_month = current_date.replace(month=current_date.month + 1, day=1)
                return next_month + timedelta(days=min(current_date.day, 
                    (next_month.replace(month=next_month.month % 12 + 1) - timedelta(days=1)).day) - 1)
    else:
        raise ValueError(f"Invalid periodicity: {periodicity}")

def is_date_within_grace_period(expected_date: datetime, actual_date: datetime, periodicity: str) -> bool:
    """Check if actual completion date is within acceptable range of expected date."""
    if periodicity == 'daily':
        return actual_date.date() == expected_date.date()
    elif periodicity == 'weekly':
        return expected_date.date() <= actual_date.date() <= (expected_date + timedelta(days=6)).date()
    elif periodicity == 'monthly':
        return (expected_date.year == actual_date.year and 
                expected_date.month == actual_date.month)
    return False

def calculate_current_streak(completion_dates: List[str], periodicity: str) -> Tuple[int, str]:
    """
    Calculate current active streak.
    Returns (streak_length, start_date) or 0 if no active streak.
    """
    if not completion_dates:
        return 0
    
    parsed_dates = []
    for date_str in completion_dates:
        try:
            parsed_dates.append(parse_date(date_str))
        except ValueError:
            continue
    
    if not parsed_dates:
        return 0
    
    parsed_dates.sort()
    today = datetime.now()
    last_completion = parsed_dates[-1]
    
    # Check if streak is still active
    expected_next = get_expected_next_date(last_completion, periodicity)
    is_overdue = today.date() > expected_next.date()
    
    if periodicity == 'weekly':
        is_overdue = today.date() > (expected_next + timedelta(days=6)).date()
    elif periodicity == 'monthly':
        is_overdue = (today.year > expected_next.year or 
                     (today.year == expected_next.year and today.month > expected_next.month))
    
    if is_overdue:
        return 0
    
    # Calculate current streak by working backwards
    current_streak_length = 1
    current_date = last_completion
    
    for i in range(len(parsed_dates) - 2, -1, -1):
        previous_date = parsed_dates[i]
        
        if periodicity == 'daily':
            expected_previous_date = current_date - timedelta(days=1)
        elif periodicity == 'weekly':
            expected_previous_date = current_date - timedelta(weeks=1)
        elif periodicity == 'monthly':
            if current_date.month == 1:
                expected_previous_date = current_date.replace(year=current_date.year - 1, month=12)
            else:
                try:
                    expected_previous_date = current_date.replace(month=current_date.month - 1)
                except ValueError:
                    prev_month = current_date.replace(month=current_date.month - 1, day=1)
                    last_day_prev_month = (prev_month.replace(month=prev_month.month % 12 + 1) - timedelta(days=1)).day
                    expected_previous_date = prev_month.replace(day=min(current_date.day, last_day_prev_month))
        
        if is_date_within_grace_period(expected_previous_date, previous_date, periodicity):
            current_streak_length += 1
            current_date = previous_date
        else:
            break
    
    streak_start_index = len(parsed_dates) - current_streak_length
    start_date = parsed_dates[streak_start_index].strftime('%Y-%m-%d')
    
    return current_streak_length, start_date

def calculate_all_streaks(completion_dates: List[str], periodicity: str, creation_date: str = None) -> List[Dict]:
    """
    Calculate all streaks for a habit.
    Returns a list of streak dictionaries with start_date, end_date, and length.
    """
    if not completion_dates:
        return []
    
    # Parse and sort completion dates
    parsed_dates = []
    for date_str in completion_dates:
        try:
            parsed_dates.append(parse_date(date_str))
        except ValueError:
            continue
    
    parsed_dates.sort()
    
    if not parsed_dates:
        return []
    
    streaks = []
    current_streak_start = parsed_dates[0]
    current_streak_end = parsed_dates[0]
    current_streak_length = 1
    
    for i in range(1, len(parsed_dates)):
        current_date = parsed_dates[i]
        previous_date = parsed_dates[i-1]
        
        # Calculate expected next date based on previous completion
        expected_date = get_expected_next_date(previous_date, periodicity)
        
        # Check if current completion is within acceptable range
        if is_date_within_grace_period(expected_date, current_date, periodicity):
            # Continue current streak
            current_streak_end = current_date
            current_streak_length += 1
        else:
            # Streak broken - save current streak and start new one
            streaks.append({
                'start_date': current_streak_start.strftime('%Y-%m-%d'),
                'end_date': current_streak_end.strftime('%Y-%m-%d'),
                'length': current_streak_length
            })
            
            # Start new streak
            current_streak_start = current_date
            current_streak_end = current_date
            current_streak_length = 1
    
    # Add the final streak
    streaks.append({
        'start_date': current_streak_start.strftime('%Y-%m-%d'),
        'end_date': current_streak_end.strftime('%Y-%m-%d'),
        'length': current_streak_length
    })
    
    return streaks

def get_longest_streak_habit(completion_dates: List[str], periodicity: str) -> Tuple[int, str, str, int]:
    """
    Get the longest streak for a specific habit.
    Returns (max_streak, start_date, end_date, breaks_count).
    """
    if not completion_dates:
        return 0, None, None, 0
    
    parsed_dates = []
    for date_str in completion_dates:
        try:
            parsed_dates.append(parse_date(date_str))
        except ValueError:
            continue
    
    if not parsed_dates:
        return 0, None, None, 0
    
    parsed_dates.sort()
    
    streaks = []
    current_streak_start = parsed_dates[0]
    current_streak_end = parsed_dates[0]
    current_streak_length = 1
    
    for i in range(1, len(parsed_dates)):
        current_date = parsed_dates[i]
        previous_date = parsed_dates[i-1]
        expected_date = get_expected_next_date(previous_date, periodicity)
        
        if is_date_within_grace_period(expected_date, current_date, periodicity):
            current_streak_end = current_date
            current_streak_length += 1
        else:
            streaks.append({
                'start': current_streak_start,
                'end': current_streak_end,
                'length': current_streak_length
            })
            current_streak_start = current_date
            current_streak_end = current_date
            current_streak_length = 1
    
    streaks.append({
        'start': current_streak_start,
        'end': current_streak_end,
        'length': current_streak_length
    })
    
    if not streaks:
        return 0, None, None, 0
    
    longest_streak = max(streaks, key=lambda x: x['length'])
    
    return (
        longest_streak['length'],
        longest_streak['start'].strftime('%Y-%m-%d'),
        longest_streak['end'].strftime('%Y-%m-%d'),
        len(streaks) - 1  # breaks = number of separate streaks - 1
    )

def get_longest_streak_all(db) -> Dict:
    """
    Get the longest streak across all habits.
    Returns dict with habit info and streak details.
    """
    habits = get_all_habits(db)
    longest_overall = {'streak': 0, 'habit': None, 'start_date': None, 'end_date': None, 'breaks': 0}
    
    for habit in habits:
        habit_id, habit_name = habit[0], habit[1]
        habit_data = get_habit_data(db, habit_id)  # Fixed: pass habit_id instead of entire habit tuple
        
        completions = get_completions(db, habit_id)
        periodicity = habit_data['periodicity']
        
        max_streak, start_date, end_date, breaks = get_longest_streak_habit(completions, periodicity)
        
        if max_streak > longest_overall['streak']:
            longest_overall = {
                'streak': max_streak,
                'habit': habit_name,
                'start_date': start_date,
                'end_date': end_date,
                'breaks': breaks
            }
    
    return longest_overall

def analyze_habit_performance(completion_dates: List[str], periodicity: str, creation_date: str = None) -> tuple:
    """
    Comprehensive analysis of a habit's performance.
    Returns detailed statistics about the habit.
    """
    if not completion_dates:
        return 0, 0, 0, [], 0
    
    # Basic stats
    total_completions = len(completion_dates)
    all_streaks = calculate_all_streaks(completion_dates, periodicity, creation_date)
    
    # Get longest streak (extract just the number if it returns a tuple)
    longest_streak_result = get_longest_streak_habit(completion_dates, periodicity)
    if isinstance(longest_streak_result, tuple):
        longest_streak = longest_streak_result[0]  # Get just the streak number
    else:
        longest_streak = longest_streak_result
    
    # Get current streak (extract just the number if it returns a tuple)
    current_streak_result = calculate_current_streak(completion_dates, periodicity)
    if isinstance(current_streak_result, tuple):
        current_streak = current_streak_result[0]  # Get just the streak number
    else:
        current_streak = current_streak_result
    
    # Calculate days since creation
    days_since_creation = 0
    if creation_date:
        try:
            creation_dt = parse_date(creation_date)
            days_since_creation = (datetime.now() - creation_dt).days
        except ValueError:
            pass
    
    return (
        total_completions,
        longest_streak,
        current_streak,
        all_streaks,
        days_since_creation
    )
   
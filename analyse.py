from db import get_db
from datetime import datetime, timedelta

def get_all_habits(db):
    """Return a list of all habits."""
    cur = db.cursor()
    cur.execute("SELECT * FROM habits")
    return cur.fetchall()

def get_allHabit_summaries(db):
    """
    Returns a list of all habits with their name, periodicity,start (creation) date and last_completion_date. 
    Example:
    [
        {"name": "Workout", "periodicity": "daily", "start_date": "2025-04-01", "last_completion_date": "2025-04-07"},
        {"name": "Meditate", "periodicity": "weekly", "start_date": "2025-03-15", "last_completion_date": "2025-04-05"},
        ...
    ]
    """
    conn = get_db()
    cursor = conn.execute("SELECT * , periodicity, creation_date FROM habits")
    cursor = conn.execute(
        "SELECT *, completion_date FROM completions "
        "JOIN habits ON completions.habit_id = habits.id "
        "ORDER BY creation_date DESC"
    )
    return [
        {"name": row[0], "periodicity": row[1], "start_date": row[2], "last_completion_date": row[3]}
        for row in cursor.fetchall()
    ]

def get_habits_by_periodicity(db, periodicity):
    """Return a list of habits with the same periodicity."""
    cur = db.cursor()
    cur.execute("SELECT * FROM habits WHERE periodicity=?", (periodicity,))
    
    return cur.fetchall()

def get_longest_streak_all(db):
    """Return the longest streak across all habits."""
    cur = db.cursor()
    cur.execute("SELECT habit_id, MAX(streak) FROM completions GROUP BY habit_id")
    return cur.fetchone()

def get_longest_streak_habit(db, habit_id):
    """Return the longest streak for a specific habit."""
    cur = db.cursor()
    cur.execute("SELECT MAX(streak) FROM completions WHERE habit_id=?", (habit_id,))
    return cur.fetchone()


def calculate_streak(completions):

    """
    Calculate the longest streak of consecutive completions.
    :param completions: List of completion dates (strings in 'YYYY-MM-DD' format).
    :return: Longest streak in days.
    """
    if not completions:
        return 0

    # Sort the completions in ascending order
    completions_sorted = sorted(completions)

    longest_streak = 1
    current_streak = 1

    for i in range(1, len(completions_sorted)):
        prev_date = datetime.strptime(completions_sorted[i - 1], "%Y-%m-%d")
        curr_date = datetime.strptime(completions_sorted[i], "%Y-%m-%d")

        # Check if the current date is exactly one day after the previous date
        if curr_date == prev_date + timedelta(days=1):
            current_streak += 1
            if current_streak > longest_streak:
                longest_streak = current_streak
        else:
            current_streak = 1

    return longest_streak

def calculate_current_streak(self):
    """Calculate the current ongoing streak for the habit."""
    if not self.completion_dates:
        return 0

    # Convert dates to datetime.date objects and sort
    sorted_dates = sorted(
        [datetime.strptime(d, "%Y-%m-%d").date() for d in self.completion_dates]
    )
    
    streak = 1
    streak_start = sorted_dates[0]
    last_valid_date = sorted_dates[0]

    for i in range(1, len(sorted_dates)):
        current_date = sorted_dates[i]

        if self.periodicity == "daily":
            expected_previous = current_date - timedelta(days=1)
        elif self.periodicity == "weekly":
            expected_previous = current_date - timedelta(weeks=1)
        else:
            raise ValueError(f"Unsupported periodicity: {self.periodicity}")

        if last_valid_date == expected_previous:
            streak += 1
        else:
            # Break happened
            streak = 1  # reset streak starting from here
        last_valid_date = current_date

    # Check if the current streak is still ongoing
    today = datetime.today().date()
    if self.periodicity == "daily" and (today - last_valid_date).days > 1:
        return 0
    elif self.periodicity == "weekly" and (today - last_valid_date).days > 7:
        return 0

    return streak, streak_start.strftime("%Y-%m-%d")


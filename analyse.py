from db import get_db

def get_all_habits(db):
    """Return a list of all habits."""
    cur = db.cursor()
    cur.execute("SELECT * FROM habits")
    return cur.fetchall()

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
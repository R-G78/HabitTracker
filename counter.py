from datetime import datetime, timedelta
import sqlite3
from db import get_db, add_habit, add_completion

   
class Habit:
    def __init__(self, task: str, periodicity: str, id=None, habit_streak: int = 0, creation_date: str = None, completion_dates=None):
        self.task = task
        self.periodicity = periodicity
        self.id = id
        self.streak = habit_streak  # Current streak count
        self.creation_date = creation_date or str(datetime.now().date())
        self.completion_dates = completion_dates  # List of dates when the habit was checked off

    def store(self):
        """Stores a new habit in the database."""
        db = get_db()
        add_habit(db, self.task, self.periodicity)
        
    def increment(self):
        """Mark the habit as completed for the current period."""
        db = get_db()
        add_completion(db, self.task, datetime.now().strftime("%Y-%m-%d"))
        self.update_current_streak()


    def update_current_streak(self):
        """Update the current streak attribute of the habit and sync with the database."""
        result = self.calculate_current_streak()
        self.streak = result[0] if isinstance(result, tuple) else 0

        # Update the database
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE habits SET streak = ? WHERE id = ?",
            (self.streak, self.task)
        )
        conn.commit()

    
    def calculate_max_streak_with_details(self): 
        """Calculate the maximum streak with start/end dates and number of breaks."""
        if not self.completion_dates:
            return 0, None, None, 0

        sorted_dates = sorted(self.completion_dates)
        max_streak = 0
        current_streak = 1
        breaks = 0

        max_streak_start = max_streak_end = datetime.strptime(sorted_dates[0], "%Y-%m-%d").date()
        current_streak_start = max_streak_start

        for i in range(1, len(sorted_dates)):
            current_date = datetime.strptime(sorted_dates[i], "%Y-%m-%d").date()
            previous_date = datetime.strptime(sorted_dates[i - 1], "%Y-%m-%d").date()

            if self.periodicity == "daily":
                is_continuous = current_date == previous_date + timedelta(days=1)
            elif self.periodicity == "weekly":
                is_continuous = 6 <= (current_date - previous_date).days <= 8
            elif self.periodicity == "monthly":
                is_continuous = 28 <= (current_date - previous_date).days <= 31
            else:
                raise ValueError(f"Unsupported periodicity: {self.periodicity}")

            if is_continuous:
                current_streak += 1
            else:
                # Break occurred
                breaks += 1
                if current_streak > max_streak:
                    max_streak = current_streak
                    max_streak_start = current_streak_start
                    max_streak_end = previous_date
                current_streak = 1
                current_streak_start = current_date

        # Final streak check
        if current_streak > max_streak:
            max_streak = current_streak
            max_streak_start = current_streak_start
            max_streak_end = datetime.strptime(sorted_dates[-1], "%Y-%m-%d").date()

        return max_streak, max_streak_start, max_streak_end, breaks  
    
    def calculate_current_streak(self):
        """Calculate the current ongoing streak for the habit."""
    
        if not self.completion_dates:
            return 0

        sorted_dates = sorted(
            [datetime.strptime(d, "%Y-%m-%d").date() for d in self.completion_dates]
        )

        today = datetime.today().date()
        last_date = sorted_dates[-1]

        # Check if the last completion is within the allowed "current" window
        if self.periodicity == "daily" and (today - last_date).days > 1:
            return 0
        elif self.periodicity == "weekly" and (today - last_date).days > 7:
            return 0
        elif self.periodicity == "monthly" and (today.month != last_date.month or today.year != last_date.year):
            return 0

        # Start counting backwards for streak
        streak = 1
        for i in range(len(sorted_dates) - 2, -1, -1):
            current = sorted_dates[i]
            next_date = sorted_dates[i + 1]
            delta = (next_date - current).days

            if self.periodicity == "daily" and delta == 1:
                streak += 1
            elif self.periodicity == "weekly" and 6 <= delta <= 8:
                streak += 1
            elif self.periodicity == "monthly" and 28 <= delta <= 31:
                streak += 1
            else:
                break

        return streak, sorted_dates[-streak].strftime("%Y-%m-%d")
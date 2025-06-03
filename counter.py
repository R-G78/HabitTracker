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
        """Store the habit in the database."""
        # This method should implement the logic to store the habit in a database
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
                expected_previous = current_date - timedelta(days=1)
            elif self.periodicity == "weekly":
                expected_previous = current_date - timedelta(weeks=1)
            elif self.periodicity == "monthly":
                expected_previous = previous_date + timedelta(days=30)
            else:
                raise ValueError(f"Unsupported periodicity: {self.periodicity}")

            if previous_date == expected_previous:
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

        # Convert dates to datetime.date objects and sort
        sorted_dates = sorted(
            [datetime.strptime(d, "%Y-%m-%d").date() for d in self.completion_dates]
        )
        
        streak = 1
        streak_start = sorted_dates[0]
        last_valid_date = sorted_dates[0]

        for i in range(1, len(sorted_dates)):
            current_date = sorted_dates[i]

            delta = (current_date - last_valid_date).days

            if self.periodicity == "daily" and delta == 1:
                streak += 1
            elif self.periodicity == "weekly" and 1 <= delta <= 7:
                streak += 1
            elif self.periodicity == "monthly" and 28 <= delta <= 31:
                streak += 1
            else:
                streak = 1
                last_valid_date = current_date

        # Check if the current streak is still ongoing
        today = datetime.today().date()
        if self.periodicity == "daily" and (today - last_valid_date).days > 1:
            return 0
        elif self.periodicity == "weekly" and (today - last_valid_date).days > 7:
            return 0
        elif self.periodicity == "monthly" and (today.month != last_valid_date.month or today.year != last_valid_date.year):
            return 0

        return streak, streak_start.strftime("%Y-%m-%d")

   
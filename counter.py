"""
counter.py
--------
Defines the Habit class, the core domain model for HabitTracker.

Each Habit instance represents a single trackable habit and encapsulates:
    - Its metadata (name, periodicity, creation date)
    - Its completion history
    - All streak calculation logic (current streak, max streak, breaks)
    - Methods to persist itself and its completions to the database

"""

from datetime import datetime, timedelta
from typing import Tuple
from db import get_db, add_habit, check_habit_exists, add_completion
from analyse import calculate_current_streak

   
class Habit:
    def __init__(self, task: str, periodicity: str, id=None, habit_streak: int = 0, creation_date: str = None, completion_dates=None):
        self.task = task
        self.periodicity = periodicity
        self.id = id
        self.streak = habit_streak  # Current streak count
        self.creation_date = creation_date or str(datetime.now().date())
        self.completion_dates = completion_dates  # List of dates when the habit was checked off

    def store(self, db):
        """
        Stores a new habit in the database.
        If the habit already exists, it will not be added again.
        """
        
        check_exists = check_habit_exists(db, self.task, self.periodicity)
        if check_exists:
            print(f"Habit '{self.task}' with {self.periodicity} periodicity already exists!\n")
            print("Creation cancelled")
            return False   
        
        else:
            print(f"Adding habit '{self.task}' with {self.periodicity} periodicity.")
        
            add_habit(db, self.task, self.periodicity)
    
    def increment(self, db):#increment
        """Mark the habit as completed for the current period and updates the streak count."""
        add_completion(db, self.task, datetime.now().strftime("%Y-%m-%d"))
        self.update_current_streak(db)

    def update_current_streak(self, db):
        """Update the current streak attribute of the habit and sync with the database."""
        if db is None:
            raise ValueError("A database connection must be provided.")

        result = self.calculate_current_streak()
        self.streak = result[0]

        cursor = db.cursor()
        cursor.execute(
            "UPDATE habits SET streak = ? WHERE id = ?",
            (self.streak, self.id)
        )
        db.commit()
        
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
    
    def calculate_current_streak(self) -> Tuple[int, str]:
        return calculate_current_streak(self.completion_dates, self.periodicity)
        #habit.updatecurrent_streak
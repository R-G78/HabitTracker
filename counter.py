from datetime import datetime, timedelta

class Habit:
    def __init__(self, task: str, periodicity: str, creation_date: str = None):
        self.task = task
        self.periodicity = periodicity  # "daily" or "weekly" "monthly"
        self.creation_date = creation_date or str(datetime.now().date())
        self.completion_dates = []  # List of dates when the habit was checked off
    
    import sqlite3
from datetime import datetime

class Habit:
    def __init__(self, habit_id, task, periodicity, creation_date, last_completion_date=None):
        self.habit_id = habit_id
        self.task = task
        self.periodicity = periodicity
        self.creation_date = creation_date
        self.last_completion_date = last_completion_date

    @classmethod
    def from_db(cls, db, habit_id):
        """Create a Habit instance from the database using its ID."""
        cur = db.cursor()
        cur.execute("SELECT id, task, periodicity, creation_date FROM habits WHERE id=?", (habit_id,))
        row = cur.fetchone()

        if not row:
            raise ValueError(f"Habit with ID {habit_id} not found.")

        cur.execute(
            "SELECT completion_date FROM completions WHERE habit_id=? ORDER BY completion_date DESC LIMIT 1",
            (habit_id,)
        )
        last_completion = cur.fetchone()
        last_completion_date = last_completion[0] if last_completion else None

        return cls(
            habit_id=row[0],
            task=row[1],
            periodicity=row[2],
            creation_date=row[3],
            last_completion_date=last_completion_date
        )
    
    def check_off(self):
        """Mark the habit as completed for the current period."""
        today = str(datetime.now().date())
        if today not in self.completion_dates:
            self.completion_dates.append(today)
            print(f"Habit '{self.task}' checked off for {today}.")
        else:
            print(f"Habit '{self.task}' already checked off for {today}.")


    def calculate_max_streak_with_details(self): 
        """Calculate the maximum streak with start/end dates and number of breaks."""
        if not self.completion_dates:
            return 0, None, None, 0

        sorted_dates = sorted(self.completion_dates)
        max_streak = 1
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
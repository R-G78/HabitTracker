from datetime import datetime, timedelta

class Habit:
    def __init__(self, task: str, periodicity: str, creation_date: str = None):
        self.task = task
        self.periodicity = periodicity  # "daily" or "weekly"
        self.creation_date = creation_date or str(datetime.now().date())
        self.completion_dates = []  # List of dates when the habit was checked off

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
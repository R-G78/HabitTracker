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

    def calculate_streak(self):
        """Calculate the current streak for the habit."""
        if not self.completion_dates:
            return 0

        sorted_dates = sorted(self.completion_dates)
        streak = 1
        max_streak = 1

        for i in range(1, len(sorted_dates)):
            current_date = datetime.strptime(sorted_dates[i], "%Y-%m-%d").date()
            previous_date = datetime.strptime(sorted_dates[i - 1], "%Y-%m-%d").date()

           #if self.periodicity == "daily":
                #if (current_date - previous_date) == timedelta(days=1):
                    #streak += 1
                #else:
                    #max_streak = max(max_streak, streak)
                    #streak = 1
            #elif self.periodicity == "weekly":
                #if (current_date - previous_date) <= timedelta(weeks=1):
                    #streak += 1
                #else:
                    #max_streak = max(max_streak, streak)
                    #streak = 1

        #return max(max_streak, streak)
            
            if self.periodicity == "daily":
                expected_previous = current_date - timedelta(days=1)
            elif self.periodicity == "weekly":
                expected_previous = current_date - timedelta(weeks=1)

            if previous_date == expected_previous:
                streak += 1
            else:
                max_streak = max(max_streak, streak)
                streak = 1

        return max(max_streak, streak)

    def is_habit_broken(self):
        """Check if the habit is broken for the current period."""
        #today = datetime.now().date()
        #last_completion = (
            #datetime.strptime(self.completion_dates[-1], "%Y-%m-%d").date()
            #if self.completion_dates
            #else None
        #)

        #if not last_completion:
            #return True

        #if self.periodicity == "daily":
            #return (today - last_completion) > timedelta(days=1)
        #elif self.periodicity == "weekly":
            #return (today - last_completion) > timedelta(weeks=1)
    
        """Check if the habit streak is broken."""
        today = datetime.now().date()
        if not self.completion_dates:
            return True  # No completions means the streak is broken

        last_completion = datetime.strptime(self.completion_dates[-1], "%Y-%m-%d").date()

        if self.periodicity == "daily":
            return (today - last_completion) > timedelta(days=1)
        elif self.periodicity == "weekly":
            return (today - last_completion) > timedelta(weeks=1)    

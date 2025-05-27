from datetime import datetime, timedelta
from db import get_habit_data

def check_last_completion(db, habit_name):
    """
    Compares the last completion date of a habit with the current date
    and returns whether the habit can be checked off again based on its periodicity.

    :param db: The database connection.
    :param habit_name: The name of the habit to check.
    :param last_completion_date: The date of the last completion.
    :param today: The current date.    
    :param periodicity: The periodicity of the habit ("daily", "weekly", "monthly").

    :return: A dictionary with the periodicity data.
    """
    # Get habit data from the database
    habit_data = get_habit_data(db, habit_name)
    if not habit_data:
        print(f"Habit '{habit_name}' not found.")
        return None
    
    today = datetime.now().date()

    periodicity = habit_data.get('periodicity')
    last_completion_date = habit_data.get('last_completion_date')

    if not periodicity:
        print("No periodicity provided for the habit.")
        return None
    
    
   
    start_of_week = today - timedelta(days=today.weekday())  # Start of the week (Monday)
    week = [start_of_week + timedelta(days=i) for i in range(7)]  # Mon–Sun

    start_of_month = today.replace(day=1)  # First day of the current month
    # Get the first day of the next month
    if today.month == 12:
        next_month = today.replace(year=today.year + 1, month=1, day=1)
    else:
        next_month = today.replace(month=today.month + 1, day=1)
    num_days = (next_month - start_of_month).days
    month = [start_of_month + timedelta(days=i) for i in range(num_days)]

    # Check if the habit can be checked off again based on its periodicity
    if not periodicity:
        print("No periodicity provided.")
        return None
    if not last_completion_date:
        return True
    

    if periodicity == "daily":
        if last_completion_date == today:
            return False 
        else :
            return True
    elif periodicity == "weekly":
        # last_ompletion, days_of week 
        if last_completion_date in week:
            return False
        else:
            return True
    elif periodicity == "monthly":
        # last_completion, month
        if last_completion_date in month:
            return False
        else:
            return True



   



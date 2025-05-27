
import questionary
from db import get_db, add_habit, add_completion, get_all_habits, get_completions, select_habit, get_habit_data, delete_habit, get_greatest_overall_streak, get_max_streak_ofHabit, get_periodicity 
from counter import Habit
from analyse import calculate_streak, calculate_current_streak, get_allHabit_summaries, get_habits_by_periodicity, get_longest_streak_all, get_longest_streak_habit

def cli():
    db = get_db()
    print("Welcome to the Habit Tracker!")

    while True:
        choice = questionary.select(
            "What do you want to do?",
            choices=["Create Habit", "Check Off Habit", "Analyze Habits", "Delete Habit", "Exit"]
        ).ask()

        if choice == "Exit":
            print("Goodbye!")
            break

        elif choice == "Create Habit":
            task = questionary.text("What is the name of your habit?").ask()
            periodicity = questionary.select(
                "What is the periodicity of your habit?",
                choices=["daily", "weekly", "monthly"]
            ).ask()
            add_habit(db, task, periodicity)
            print(f"Habit '{task}' with periodicity {periodicity} bas been created successfully!")

        elif choice == "Check Off Habit":

            habits = get_all_habits(db)
            if not habits:
                print("No habits found. Please create a habit first.")
                continue

            habit_choices = [f"{habit[0]}: {habit[1]} ({habit[2]})" for habit in habits]
            selected_habit = questionary.select(
                "Select a habit to check off:",
                choices=habit_choices
            ).ask()

            habit_id = int(selected_habit.split(":")[0])
            add_completion(db, habit_id)
            print(f"Habit '{selected_habit}' checked off!")

        elif choice == "Delete Habit":
            all_habits = get_all_habits(db)  # Assume this returns a list of tuples like (id, name, periodicity, date)

            if not all_habits:
                print(" No habits to delete.")
                continue
            
            # Format choices for display but still keep the id for deletion
            choices = [
                questionary.Choice(title=f"{habit[1]} ({habit[2]}) — started {habit[3]}", value=habit[0])
                for habit in all_habits
            ]
            
            habit_to_delete = questionary.select(
                "Select a habit to delete:",
                choices=choices
            ).ask()

            confirm = questionary.confirm(
                f"Are you sure you want to delete '{habit_to_delete}' and all its data?"
            ).ask()

            if confirm:
                delete_habit(habit_to_delete)
                print(f"Habit '{habit_to_delete}' deleted.")
            else:
                print("Deletion cancelled.")

        
        elif choice == "Analyze Habits":
            habits = get_all_habits(db)
            if not habits:
                print("No habits found. Please create a habit first.")
                continue

            choices = questionary.select(
                "Habit Analysis Options",
                choices=["Analyse a specific habit", "Analyze all habits"]
            ).ask()
        
            if choices == "Analyse a specific habit":
                habit_name = select_habit(db)

                if habit_name: 
                    habit_data = get_habit_by_name(habit_name)
                    completion_dates = get_completions(habit_name)

                    habit = Habit(habit_data['name'], habit_data['periodicity'], completion_dates)
                    max_streak, start_date, end_date, breaks = habit.calculate_max_streak_with_details()

                    print(f"\n Max streak for '{habit.name}': {max_streak}")
                    if max_streak > 1:
                        print(f"  ➤ Start date: {start_date}")
                        print(f"  ➤ End date: {end_date}")
                    print(f"Number of streak breaks: {breaks}\n")

                    # Calculate current streak
                    current_streak, start_date = habit.calculate_current_streak()
                    print(f"The current streak of the habit {habit} : {current_streak} days, since {start_date}")
                
            elif choices == "Analyze all habits":
                choice = questionary.select(
                    "What would you like to know?",
                    choices=["Return a list of all currently tracked habits", "Return a list of habits with the same periodicity", "Longest run streak of every Habit", "Longest overall habit streak", "Exit"]
                ).ask ()

                if choice == "Exit":
                    print ("Goodbye!")
                    break

                elif choice == "Return a list of all currently tracked habits":
                    
                    print("\n=== All Habits ===")
                    summaries = get_allHabit_summaries(db)
                    for habit in summaries:
                        print(f"{habit['name']} — {habit['periodicity']} — started on {habit['start_date']}")
                    continue    

                elif choice == "Return a list of habits with the same periodicity":
                    periodicity = questionary.select(
                        "What is the periodicity of the habits you want to see?",
                        choices=["daily", "weekly"]
                    ).ask()

                    same_period_habits = get_habits_by_periodicity(db, periodicity)
                    
                    if same_period_habits:
                        print(f"\nHabits with {periodicity} periodicity:")
                        for habit in same_period_habits:
                            print(f"- {habit[1]}")
                    else:
                        print(f"No habits found with {periodicity} periodicity.")
                    

                elif choice == "Longest run streak of every Habit":
                    habits = get_all_habits(db)
            
                    for habit in habits:
                        completions = get_completions(db, habit[0])
                        periodicity = get_periodicity(habit[0])
                        max_streak, start_date, end_date, breaks = get_max_streak_ofHabit( completions, periodicity)
                        print(f"Longest streak for '{habit[0]}': {max_streak} days")
                        print(f"From {start_date} to {end_date}")
                    

                elif choice == "Longest overall habit streak":
                    # Get the longest overall streak from the database
                    result = get_greatest_overall_streak(db)
                    print(f" Longest streak: {result['streak']} days for '{result['habit']}'")
                    print(f"From {result['start_date']} to {result['end_date']}")
                    print(f" Streaks were broken {result['breaks']} times")


            
        

if __name__ == "__main__":
    cli()
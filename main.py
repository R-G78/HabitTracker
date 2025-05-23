
import questionary
from db import get_db, add_habit, add_completion, get_all_habits, get_completions, select_habit, get_habit_by_name, delete_habit
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
                choices=["daily", "weekly"]
            ).ask()
            add_habit(db, task, periodicity)
            print(f"Habit '{task}' created successfully!")

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
            habits = [str(get_all_habits(db))]
            if not habits:
                print("No habits found. Please create a habit first.")
                continue

            choices = questionary.select(
                "Habit Analysis Options",
                choices=["Analyse a specific habit", "Analyze all habits"]
            ).ask()
        
            if choices == "Analyse a specific habit":
                habit_name = select_habit()

                if habit_name: 
                    habit_data = get_habit_by_name(habit_name)
                    completion_dates = db.get_completion_dates(habit_name)

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
                    choices=["Return a list of all currently tracked habits", "Return a list of habits with the same periodicity", "Longest run streak of all habits", "Longest overall habit streak", "Exit"]
                ).ask ()

                if choice == "Exit":
                    print ("Goodbye!")
                    break

                elif choice == "Return a list of all currently tracked habits":
                    
                    print("\n=== All Habits ===")
                    summaries = get_allHabit_summaries(db)
                    for habit in summaries:
                        print(f"📌 {habit['name']} — {habit['periodicity']} — started on {habit['start_date']}")
                        

                elif choice == "Return a list of habits with the same periodicity":
                    pass

                elif choice == "Longest run streak of all habits":
                    pass 

                elif choice == "Longest overall habit streak":
                    pass


            
            # NEW ANALYSE FUNCTIONALITY
            # This is the new functionality added to the CLI for habit analysis
            #The user can choose whether they want to analyse one habit or all habits
            print("\n=== Habit Analysis ===")
            print("1. Analyze a specific habit")
            print("2. Analyze all habits")
            analysis_choice = input("Choose an option (1/2): ")

            if analysis_choice == "1":
                # Analyze a specific habit
                habit_name = input("Enter the habit name: ").strip()
                habit = next((h for h in habits if h[1].lower() == habit_name.lower()), None)

                if habit:
                    completions = get_completions(db, habit[0])
                    streak = calculate_streak(completions)
                    print(f"\nAnalysis for '{habit[1]}':")
                    print(f"Completions: {len(completions)}")
                    print(f"Longest streak: {streak} days")
                else:
                    print(f"Habit '{habit_name}' not found.")





            #PRIOR ANALYSE FUNCTIONALITY
            # New functionality
            print("\n=== Analytics ===")
            print("1. List habits with the same periodicity")
            print("2. Longest run streak of all habits")
            print("3. Longest streak of a specific habit")
            print("4. Return a list of all currently tracked habits")
            analytics_choice = input("Choose an option (1/2/3/4): ")

            if analytics_choice == "1":
                # List habits with the same periodicity
                periodicity = input("Enter the periodicity (daily/weekly/monthly): ").strip().lower()
                same_period_habits = [habit for habit in habits if habit[2].lower() == periodicity]
                
                if same_period_habits:
                    print(f"\nHabits with {periodicity} periodicity:")
                    for habit in same_period_habits:
                        print(f"- {habit[1]}")
                else:
                    print(f"No habits found with {periodicity} periodicity.")

            elif analytics_choice == "2":
                # Longest run streak of all habits
                longest_streak = 0
                longest_streak_habit = None

                for habit in habits:
                    completions = get_completions(db, habit[0])
                    streak = calculate_streak(completions)
                    if streak > longest_streak:
                        longest_streak = streak
                        longest_streak_habit = habit[1]

                if longest_streak_habit:
                    print(f"\nLongest run streak: {longest_streak} days (Habit: {longest_streak_habit})")
                else:
                    print("No streaks found.")

            elif analytics_choice == "3":
                # Longest streak of a specific habit
                habit_name = input("Enter the habit name: ").strip()
                habit = next((h for h in habits if h[1].lower() == habit_name.lower()), None)

                if habit:
                    completions = get_completions(db, habit[0])
                    streak = calculate_streak(completions)
                    print(f"\nLongest streak for '{habit[1]}': {streak} days")
                else:
                    print(f"Habit '{habit_name}' not found.")

            elif analytics_choice == "4":

                print("\n=== All Habits ===")
                for habit in habits:
                    completions = get_completions(db, habit[0])
                    print(f"{habit[0]}: {habit[1]} ({habit[2]}) - Completions: {len(completions)}")



            else:
                print("Invalid choice. Please try again.")
            
        

if __name__ == "__main__":
    cli()
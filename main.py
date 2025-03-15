
import questionary
from db import get_db, add_habit, add_completion, get_all_habits, get_completions
from counter import Habit
from analyse import calculate_streak

def cli():
    db = get_db()
    print("Welcome to the Habit Tracker!")

    while True:
        choice = questionary.select(
            "What do you want to do?",
            choices=["Create Habit", "Check Off Habit", "Analyze Habits", "Exit"]
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

        
        elif choice == "Analyze Habits":
            habits = get_all_habits(db)
            if not habits:
                print("No habits found. Please create a habit first.")
                continue

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
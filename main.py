
import questionary
from db import get_db, get_all_habits, get_completions, get_habit_data, delete_habit, reset_database 
from counter import Habit
from analyse import   calculate_current_streak, get_allHabit_summaries, get_habits_by_periodicity, get_longest_streak_all, get_longest_streak_habit
from seed import seed_demo_data

def cli():
    

    
    print("\n Welcome to the Habit Tracker\n")
    db = get_db()  
    choice = questionary.select(
        "Would you like to start with demo data or a clean slate?",
        choices=[
            "Use demo data (preloaded habits and completions)",
            "Clear database and start fresh",
            "Continue with existing data"
        ]
    ).ask()

    if choice == "Use demo data (preloaded habits and completions)":
        seed_demo_data()
    
        print("Demo data loaded. You're good to go!\n")

    elif choice == "Clear database and start fresh":
        confirm = questionary.confirm(
            "Are you sure you want to clear the database? This will delete all existing habits and completions."
        ).ask()
        if confirm:
            reset_database(db)
            print("Database cleared. You can now create your own habits.\n")
        else:
            print("Database not cleared. Continuing with existing data.\n")

    elif choice == "Continue with existing data":
        print("Continuing with existing data. You can manage your habits.\n")
    
    
    # Main loop for the CLI
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
            habit = Habit(task, periodicity)
            habit.store()
            print(f"Habit '{task}' with periodicity {periodicity} bas been created successfully!")

        elif choice == "Check Off Habit": 

            habits = get_all_habits(db)
            if not habits:
                print("No habits found. Please create a habit first.")
                continue

            # Create a mapping: display index → real habit ID
            index_to_id = {}
            habit_choices = []

            for idx, habit in enumerate(habits, start=1):
                index_to_id[str(idx)] = habit[0]  
                habit_choices.append(f"{idx}: {habit[1]} ({habit[2]})")  

            selected_habit = questionary.select(
                "Select a habit to check off:",
                choices=habit_choices
            ).ask()

        # Extract index from selection and look up real habit_id
            selected_index = selected_habit.split(":")[0]  # e.g., "2" from "2: Fly (daily)"
            habit_id = index_to_id[selected_index] 

            data = get_habit_data(db, habit_id)
            habit = Habit(
                data['id'],
                data['name'],
                data['periodicity'], 
                data['creation_date'], 
                get_completions(db, habit_id))
            habit.increment()

            
        elif choice == "Delete Habit":
            all_habits = get_all_habits(db)  # Assume this returns a list of tuples like (id, name, periodicity, date)

            if not all_habits:
                print(" No habits to delete.")
                continue

            choices = [
                questionary.Choice(
                    title=f"{i} — {habit[1]} ({habit[2]}) — started {habit[3]}",
                    value=habit[0]  # keeps the original habit_id
                )
                for i, habit in enumerate(all_habits, 1)
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
                habits = get_all_habits(db)
                if not habits:
                    print("No habits found.")
                    continue

                # Display cleanly indexed choices
                choices = [
                    questionary.Choice(title=f"{i} — {habit[1]} ({habit[2]})", value=habit[0])
                    for i, habit in enumerate(habits, 1)
                ]

                selected_habit_id = questionary.select(
                    "Select a habit to analyse:",
                    choices=choices
                ).ask()

                if selected_habit_id: 
                    habit_data = get_habit_data(db, selected_habit_id) 
                    if not habit_data:
                        print(f"Habit ID '{selected_habit_id}' not found.")
                        continue
                    
                    habit = Habit(
                        habit_data['id'],
                        habit_data['name'],
                        habit_data['periodicity'],
                        habit_data['creation_date'],
                        get_completions(db, selected_habit_id)
                    )

                    completion_dates = get_completions(db, selected_habit_id)
                    periodicity = habit_data['periodicity']
                    
                    if periodicity is None:
                        print(f"Error: Could not find periodicity for habit ID '{selected_habit_id}'")
                        continue

                    max_streak, start_date, end_date, breaks = get_longest_streak_habit(completion_dates, periodicity)

                    print(f"\nMax streak for '{habit_data['name']}': {max_streak}")
                    if max_streak > 0:
                        print(f"  ➤ Start date: {start_date}")
                        print(f"  ➤ End date: {end_date}")
                    print(f"Number of streak breaks: {breaks}\n")

        
                    #Calculate streak
                    current_streak_result = calculate_current_streak(completion_dates, periodicity)
                    if current_streak_result == 0:
                        print("No current streak.")
                    else:
                        current_streak, start_date = current_streak_result
                        print(f"Current streak: {current_streak} (since {start_date})")
                    

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

                    index_to_id = {}

                    for i, habit in enumerate(summaries, 1):
                        print(f"{i} — {habit['name']} — {habit['periodicity']} — started on {habit['start_date']}")
                        index_to_id[i] = habit['id']  # store mapping of display index → actual DB habit_id   
                        continue 

                elif choice == "Return a list of habits with the same periodicity":
                    periodicity = questionary.select(
                        "What is the periodicity of the habits you want to see?",
                        choices=["daily", "weekly", "monthly"]
                    ).ask()

                    same_period_habits = get_habits_by_periodicity(db, periodicity)

                    if same_period_habits:
                        print(f"\nHabits with {periodicity} periodicity:")
                        for i, habit in enumerate(same_period_habits, 1):
                            # habit is assumed to be tuple (id, name, periodicity, creation_date)
                            print(f"{i} — {habit[1]} (started on {habit[3]})")
                    else:
                        print(f"No habits found with {periodicity} periodicity.")

                elif choice == "Longest run streak of every Habit":
                    habits = get_all_habits(db)
                    
                    if not habits:
                        print("No habits found.")
                        continue
                    
                    print(f"\n=== Longest Streaks for All Habits ===")
                    
                    for habit in habits:
                        # Extract data directly from the habit tuple
                        # Assuming habit tuple structure: (id, name, periodicity, creation_date, ...)
                        habit_id = habit[0]
                        habit_name = habit[1]
                        periodicity = habit[2]  # Get periodicity directly from tuple
                        
                        completions = get_completions(db, habit_id)
                        
                        if periodicity is None:
                            print(f"Error: Could not find periodicity for habit '{habit_name}'")
                            continue
                        
                        # get_longest_streak_habit returns 4 values: (length, start_date, end_date, breaks)
                        max_streak, start_date, end_date, breaks = get_longest_streak_habit(completions, periodicity)
                        
                       
                        print(f"Longest streak for '{habit_name}-{(periodicity)}': {max_streak} ")
                        if start_date and end_date:
                            print(f"  From {start_date} to {end_date}")
                            print(f"  Number of streak breaks: {breaks}")
                        else:
                            print("  No completions found")
                        print()  
                    

                elif choice == "Longest overall habit streak":
                    # Get the longest overall streak from the database
                    result = get_longest_streak_all(db)
                    print(f" Longest streak: {result['streak']} days for '{result['habit']}'")
                    print(f"From {result['start_date']} to {result['end_date']}")
                    print(f" Streaks were broken {result['breaks']} times")


                
            

if __name__ == "__main__":
    cli()


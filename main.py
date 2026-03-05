"""
Habit Tracker - Main CLI Module

This module provides the command-line interface for the habit tracking application.
It handles user interactions, menu navigation, and coordinates between different
components of the system.

Author: Renee I. Njiru
Date: 2026-02-18
"""

# Third-party imports
import questionary 

# Local imports 
from db import get_db, create_tables, get_all_habits, get_completions, get_habit_data, delete_habit, reset_database 
from counter import Habit
from analyse import   calculate_current_streak, get_allHabit_summaries, get_habits_by_periodicity, get_longest_streak_habit, analyze_habit_performance, get_longest_streak_all
from seed import seed_demo_data

def cli():
    
    print("\n Welcome to the Habit Tracker\n")
    db = get_db()  # Connect to the database
    
    choice = questionary.select(
        "Would you like to start with demo data or a clean slate?",
        choices=[
            "Use demo data (preloaded habits and completions)",
            "Clear database and start fresh",
            "Continue with existing data"
        ]
    ).ask()

    if choice == "Use demo data (preloaded habits and completions)":


    
        confirm = questionary.confirm(
            """
            Are you sure you want to load demo data? 
            This will overwrite any existing habits and completions.
            Do you want to proceed?"""

        ).ask()
        if not confirm:
            print("Demo data not loaded. Continuing with existing data.\n")
            return
        else:
            print ("Clearing database...")
            reset_database(db)
            print("Loading demo data...\n")
            create_tables()
            seed_demo_data()
            print("""Demo data loaded successfully.
                   You're good to go!""")

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
        print("""You can now continue where you left off.
               \nHappy Tracking!""")
    
    
    # Main loop for the CLI
    while True:
        choice = questionary.select(
            "\nWhat do you want to do?",
            choices=["Create Habit", "Check Off Habit", "Analyze Habits", "Delete Habit", "Exit"]
        ).ask()

        if choice == "Exit":
            print("Goodbye!")
            break

        elif choice == "Create Habit": 
            task = questionary.text("What is the name of your habit?").ask()
            if not task:
                print("Habit name cannot be empty. Please try again.")
                continue
            
            while True:
                
                periodicity = questionary.select(
                    "What is the periodicity of your habit?",
                    choices=["daily", "weekly", "monthly", "Other"]
                ).ask()
                if periodicity == "Other":
                    print("\nCurrently, only daily, weekly, and monthly periodicities are supported.")
                else: 
                    break

            habit = Habit(task, periodicity)
            habit.store(db)
            if habit.store:
                print("\nYour habit has been created successfully. \nYou can now check it off as you complete it.")
                
           
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
            
            habit.increment(db)
            

            
        elif choice == "Delete Habit":
            all_habits = get_all_habits(db)  

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

            # Add exit option
            choices.append(questionary.Choice(title="Exit (go back to main menu)", value="exit"))
                
            habit_to_delete = questionary.select(
                "Select a habit to delete:",
                choices=choices
            ).ask()

            # Check if user chose to exit
            if habit_to_delete == "exit":
                print("Returning to main menu.")
                continue

            confirm = questionary.confirm(
                f"Are you sure you want to delete '{habit_to_delete}' and all its data?"
            ).ask()

            if confirm:
                delete_habit(db, habit_to_delete)
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

                print(f"\nAnalyzing habit ID: {selected_habit_id}\n")
                print("This is all you need to know about this habit:\n")

                if selected_habit_id: 
                    habit_data = get_habit_data(db, selected_habit_id) 
                    if not habit_data:
                        print(f"Habit ID '{selected_habit_id}' not found.")
                        continue
                    
                    habit = Habit(
                        habit_data['name'],
                        habit_data['periodicity'],
                        habit_data['id'],
                        habit_data['current_streak'],
                        habit_data['creation_date'],
                        get_completions(db, selected_habit_id)
                    )

                    completion_dates = get_completions(db, selected_habit_id)
                    created_date = habit_data['creation_date']
                    periodicity = habit_data['periodicity']
                    
                    if periodicity is None:
                        print(f"Error: Could not find periodicity for habit ID '{selected_habit_id}'")
                        continue

                    total_completions, longest_streak, current_streak, all_streaks, days_since_creation = analyze_habit_performance(completion_dates, periodicity, created_date)

                    print(f"Name: {habit_data['name']}")
                    print(f"Periodicity: {habit_data['periodicity']}")
                    print(f"Creation Date: {habit_data['creation_date']}")
                    print(f"Days Since Creation: {days_since_creation}")
                    print() #for readability
                    print(f"Total Completions: {total_completions}")
                    print(f"Longest Streak: {longest_streak}")
                    print(f"Current Streak: {current_streak}")
                    print() #for readability               
                    print("All Streaks:")
                    if all_streaks:
                        for i, streak in enumerate(all_streaks, 1):
                            print(f"  {i}. Start: {streak['start_date']}, End: {streak['end_date']}, Length: {streak['length']}")
                    else:
                        print("  No streaks found")
                    
                    max_streak, start_date, end_date, breaks = get_longest_streak_habit(completion_dates, periodicity)

                    print(f"\nMax streak for '{habit_data['name']}': {max_streak}")
                    if max_streak > 0:
                        print(f"  ➤ Start date: {start_date}")
                        print(f"  ➤ End date: {end_date}")
                        print() # for readability
                    print(f"Number of streak breaks: {breaks}\n")
            
                    #Calculate current streak
                    current_streak_result= habit.calculate_current_streak()
                    if current_streak_result == 0:
                        print("No current streak.")
                    else:
                        current_streak, start_date = current_streak_result
                        print(f"Current streak: {current_streak} (since {start_date})")

                    
            elif choices == "Analyze all habits":
                choice = questionary.select(
                    "What would you like to know?",
                    choices=["Return a list of all currently tracked habits", "Return a list of habits with the same periodicity", "Return the longest run streak of every Habit","Longest overall habit streak", "Exit"]
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

                elif choice == "Return the longest run streak of every Habit":
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
                    print("\n=== Longest Overall Habit Streak ===")
                    result = get_longest_streak_all(db)
                    print(f" Longest streak: {result['streak']} days for '{result['habit']}'")
                    print(f"From {result['start_date']} to {result['end_date']}")
                    print(f" Streaks were broken {result['breaks']} times")
                    print()  # Add a newline for better readability


                 
                     
                    

if __name__ == "__main__":
    cli()


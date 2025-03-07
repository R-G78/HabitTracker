import questionary
from db import get_db, create_counters_table, lookup_counter
from counter import Counter
from analyse import calculate_count

def cli():
    db = get_db()
    print("DEBUG: Database connection established")
    confirm = questionary.confirm("Are you ready?").ask()
    print(f"DEBUG: confirm = {confirm}")

    if confirm:
        run = True
        
        while run:
            print("DEBUG: Inside the while loop")
            choice = questionary.select(
                "What do you want to do?",
                choices=["Create", "Increment", "Analyse", "Exit"]
            ).ask() 
            print(f"DEBUG: choice = {choice}") 
            
            #Check if exit was selected then break the loop 
            if choice == "Exit":
                print ("Goodbye!")
                run = False
                continue #Skip the name prompt and exit the loop


            name = questionary.text("What is the name of your counter?").ask()
            
            if choice == "Create":
                description = questionary.text("What is the description of your counter?").ask()
                count = 0
                print(f"DEBUG: description = {description}")
    
                create = questionary.confirm(f"Do you want to create this counter {name}:{description}?").ask()
            
                if create == True:
                    counter_exists = lookup_counter(db, name)
                    
                    if counter_exists == True:
                        print(f"Counter '{name}' already exists. Counter creation cancelled")
                        break 
                    else:
                        print(f"The counter '{name}' with description '{description}' and current count {count} will be created")
                        print("DEBUG: Creating counters table...")
                        counter = Counter(name, description, count)
                        create_counters_table(db)   
                        counter.store(db)
                        print(f"Counter '{name}' created successfully")
                else:
                    continue 

            elif choice == "Increment":
            
                # Fetch the counter from the DB based on the name
                counter = Counter.load(db, name)
                try:
                    if counter:
                        # Increment the counter and add an event
                        counter.increment(db)

                        # Increment the counter and add an event
                        count = calculate_count(db, name)
                        print (f"Counter'{name} has been incremented. New count:{counter.count} " )
                    else:
                        print(f"There exists no counter with the name: {name}")

                except Exception as e:
                    print(f"Error incrementing counter: {e}")

            elif choice == "Analyse":

                confirmation = questionary.select("What do you want to do?", choices = )
                counter = Counter.load(db,name)

                if counter:
                    count = calculate_count(db, name)
                    print(f"Count for {name}: {count}")
                else:
                    print(f"There exists no counter with the name: {name}")
    else:
        print("Come back when you are ready! GOODBYE!")        
             
   

if __name__ == '__main__':
    cli()


import questionary
from db import get_db, add_habit, add_completion
from habit import Habit

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
            habit_id = questionary.text("Enter the ID of the habit you want to check off:").ask()
            add_completion(db, int(habit_id))
            print(f"Habit with ID {habit_id} checked off!")

        elif choice == "Analyze Habits":
            # Implement analytics functionality here
            print("Analytics functionality coming soon!")


if __name__ == '__main__':
    cli()


import questionary
from db import get_db, add_habit, add_completion, get_all_habits, get_completions
from habit import Habit

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

            print("\n=== All Habits ===")
            for habit in habits:
                completions = get_completions(db, habit[0])
                print(f"{habit[0]}: {habit[1]} ({habit[2]}) - Completions: {len(completions)}")

            # Add more analytics functionality here
            print("\nAnalytics functionality coming soon!")

if __name__ == "__main__":
    cli()
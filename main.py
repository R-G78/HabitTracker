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



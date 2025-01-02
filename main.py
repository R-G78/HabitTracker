import questionary
from db import get_db
from counter import Counter
from analyse import calculate_count

def cli():
    db = get_db()
    confirm = questionary.confirm("Are you ready?").ask()

    if confirm:
        run = True
        while run:
            choice = questionary.select(
                "What do you want to do?",
                choices=["Create", "Increment", "Analyse", "Exit"]
            ).ask()  
            
            #Check if exit was selected then break the loop 
            if choice == "Exit":
                print ("Goodbye!")
                run = False
                continue #Skip the name prompt and exit the loop


            name = questionary.text("What is the name of your counter?").ask()
            
            if choice == "Create":
                description = questionary.text("What is the description of your counter?").ask()
                count = 0
                counter = Counter(name, description)
                counter.store(db)

            elif choice == "Increment":
            
                # Fetch the counter from the DB based on the name
                counter = Counter.load(db, name)
                if counter:
                    name = questionary.text("What is the name of your counter?").ask()
            
                    Counter.increment(name)
                    Counter.add_event(db)
                    count = calculate_count(db, name)
                    print (f"Counter'{name} has been incremented. New count:{counter.count} " )
                else:
                    print(f"There exists no counter with the name: {name}")

            elif choice == "Analyse":
                counter = Counter.load(db,name)

                if counter:
                    count = calculate_count(db, name)
                    print(f"Count for {name}: {count}")
                else:
                    (f"There exists no counter with the name: {name}")
    else:
        print("Come back when you are ready! GOODBYE!")        
             
   

if __name__ == '__main__':
    cli()



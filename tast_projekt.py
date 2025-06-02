import os
import uuid
from counter import Counter
from db import get_db, add_counter, increment_counter, get_counter_data
from analyse import calculate_count
import sqlite3



class TestCounter:
    
    def setup_method(self):
        # Generate a unique test database filename
        self.db_filename = "test_{}.db".format(str(uuid.uuid4()))  # Unique test db for each test run
        
        # Initialize a clean database with the specific filename
        self.db = get_db(self.db_filename)
        
        self.create_tables_if_not_exists()  # Ensure tables are created
        
        self.clear_database()  # Ensure the database is clean
        
        # Add initial counter and increment events
        add_counter(self.db, "test_counter", "test_description")
        print("Initial counter added: test_counter with description 'test_description'")
        
        increment_counter(self.db, "test_counter", "2024-12-07")
        increment_counter(self.db, "test_counter", "2024-12-08")
        increment_counter(self.db, "test_counter", "2024-12-10")
        increment_counter(self.db, "test_counter", "2024-12-11")
        increment_counter(self.db, "test_counter", "2024-12-12")
        
        # Debugging: Print out the data to confirm it has been added
        print("Database contents after adding increments:")
        data = get_counter_data(self.db, "test_counter")
        for row in data:
            print(row)  # Display the rows in the counter_events table

    def create_tables_if_not_exists(self):
        cursor = self.db.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS counter (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT                
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS counter_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            counter_id TEXT NOT NULL,
            event_date TEXT NOT NULL,
            UNIQUE (counter_id, event_date) 
        );
        """)
        self.db.commit()

    def clear_database(self):
        """Helper function to clear all relevant data from the database."""
        cursor = self.db.cursor()
        try:
            cursor.execute("DELETE FROM counter")  # Replace 'counter' with your actual table name
            cursor.execute("DELETE FROM counter_events")  # Clear the events table
            self.db.commit()
        except sqlite3.OperationalError as e:
            print("Error clearing database:", e)
            self.db.rollback()  # Ensure to roll back any incomplete operations

    def test_counter(self):
        # Test the Counter class functionality
        counter = Counter("test_counter_1", "test_description_1")
        counter.store(self.db)  # Store the counter

        # Increment and add events
        counter.increment()
        

        # Debugging output
        print("After first increment and add_event:")
        print(f"Count: {calculate_count(self.db, 'test_counter_1')}")

        # Reset and increment
        counter.reset()
        print("After reset:")
        print(f"Count: {calculate_count(self.db, 'test_counter_1')}")

        counter.increment()
        print("After second increment:")
        print(f"Count: {calculate_count(self.db, 'test_counter_1')}")

        # Assert expected values
        assert calculate_count(self.db, "test_counter_1") == 1

    def test_db_counter(self):
        # Verify data in the database
        data = get_counter_data(self.db, "test_counter")
        print("Data from get_counter_data:", data)  # Debugging output
        for row in data:
            print(f"Row: {row}")  # Print each row collected
        
        assert len(data) == 5  # Ensure 5 unique entries exist

        count = calculate_count(self.db, "test_counter")
        print(f"Total count: {count}")  # Print the total count
        assert count == 5  # Verify total count matches

    def teardown_method(self):
        # Close and remove the test database
        if hasattr (self, 'db') and self.db:
            self.db.close()
        # Remove the test database using the filename stored earlier
        if os.path.exists(self.db_filename):
            os.remove(self.db_filename)  # Remove the unique test db after the test

import pytest
from unittest.mock import patch, MagicMock
from cli import main
from counter import Counter
from db import get_db, add_counter, increment_counter, get_counter_data
from analyse import calculate_count

# Mock database fixture
@pytest.fixture
def mock_db():
    db_mock = MagicMock()
    return db_mock

@patch("cli.get_db")
@patch("cli.questionary")
@patch("cli.Counter")
@patch("cli.create_counters_table")
def test_cli_create(mock_create_counters_table, mock_counter, mock_questionary, mock_get_db, mock_db):
    """Test the 'Create' option in the CLI"""
    mock_get_db.return_value = mock_db
    mock_questionary.confirm.side_effect = [True, True]  # Ready and confirm create
    mock_questionary.select.side_effect = ["Create", "Exit"]
    mock_questionary.text.side_effect = ["test_counter", "test_description"]

    cli()

    mock_create_counters_table.assert_called_once_with(mock_db)
    mock_counter.return_value.store.assert_called_once_with(mock_db)


@patch("cli.get_db")
@patch("cli.questionary")
@patch("cli.Counter")
def test_cli_increment(mock_counter, mock_questionary, mock_get_db, mock_db):
    """Test the 'Increment' option in the CLI"""
    mock_get_db.return_value = mock_db
    mock_counter.load.return_value = Counter("test_counter", "test_description")
    mock_counter.load.return_value.count = 0
    mock_questionary.confirm.return_value.ask.return_value = True
    mock_questionary.select.side_effect = ["Increment", "Exit"]
    mock_questionary.text.side_effect = ["test_counter"]

    cli()

    mock_counter.load.assert_called_once_with(mock_db, "test_counter")
    mock_counter.load.return_value.increment.assert_called_once_with(mock_db)


@patch("cli.get_db")
@patch("cli.questionary")
@patch("cli.Counter")
@patch("cli.calculate_count")
def test_cli_analyse(mock_calculate_count, mock_counter, mock_questionary, mock_get_db, mock_db):
    """Test the 'Analyse' option in the CLI"""
    mock_get_db.return_value = mock_db
    mock_calculate_count.return_value = 5
    mock_counter.load.return_value = Counter("test_counter", "test_description")
    mock_questionary.select.side_effect = ["Analyse", "Exit"]
    mock_questionary.text.side_effect = ["test_counter"]

    cli()

    mock_counter.load.assert_called_once_with(mock_db, "test_counter")
    mock_calculate_count.assert_called_once_with(mock_db, "test_counter")


@patch("cli.get_db")
@patch("cli.questionary")
def test_cli_exit(mock_questionary, mock_get_db):
    """Test the 'Exit' option in the CLI"""
    mock_get_db.return_value = None
    mock_questionary.confirm.return_value.ask.return_value = True
    mock_questionary.select.side_effect = ["Exit"]

    cli()

    mock_questionary.select.assert_called_once_with(
        "What do you want to do?",
        choices=["Create", "Increment", "Analyse", "Exit"]
    )


@patch("counter.calculate_count")
@patch("db.add_counter")
@patch("db.increment_counter")
def test_counter_class(mock_increment_counter, mock_add_counter, mock_calculate_count, mock_db):
    """Test the Counter class functionality"""
    counter = Counter("test_counter", "test_description")

    # Test storing the counter
    counter.store(mock_db)
    mock_add_counter.assert_called_once_with(mock_db, "test_counter", "test_description")

    # Test incrementing the counter
    counter.increment(mock_db)
    mock_increment_counter.assert_called_once_with(mock_db, "test_counter")

    # Test resetting the counter
    counter.reset()
    assert counter.count == 0

    # Test calculating the count
    mock_calculate_count.return_value = 10
    assert calculate_count(mock_db, "test_counter") == 10


@patch("db.get_counter_data")
def test_calculate_count(mock_get_counter_data, mock_db):
    """Test the calculate_count function"""
    mock_get_counter_data.return_value = [1, 2, 3]
    count = calculate_count(mock_db, "test_counter")
    assert count == 3


def test_database_operations(mock_db):
    """Test database interactions"""
    add_counter(mock_db, "test_counter", "test_description")
    increment_counter(mock_db, "test_counter", "2024-12-07")
    increment_counter(mock_db, "test_counter", "2024-12-08")

    count = calculate_count(mock_db, "test_counter")
    assert count == 2


    #counter.py original code
    from db import add_counter, increment_counter
import sqlite3

class Counter:

    def __init__(self, name: str, description: str, count: int):
        self.name = name
        self.description = description
        self.count = count
        

    def increment(self, db):
        print(f"DEBUG: DB={db}, name={self.name}")
        try:
            """Increment the counter and update the database"""
            self.count += 1 
            increment_counter(db, self.name)
            print(f"Counter '{self.name}' incremented")
        except sqlite3.DatabaseError as err:
            print(f"Error incrementing Counter: {err}")    

    def reset(self):
        """Reset the counter to 0"""
        self.count = 0

    def __str__(self):
        return f"{self.name}:{self.count}"
    
    #db class counter? make*

    def store(self, db):
        try:
            print("DEBUG: Checking if the counter exists...")
            cur = db.cursor()
            cur.execute("SELECT name FROM counter WHERE name= ?", (self.name,))
            if cur.fetchone():
                print(f"Counter '{self.name}' already exists")
                return 
            else:
                add_counter(db, self.name, self.description)
                print(f"Counter '{self.name}' stored successfully")
        except sqlite3.DatabaseError as err:
            print(f"Error storing Counter: {err}")
            
                         

    def add_event(self, db, date: str= None):
        try:
            increment_counter(db, self.name, date)
            print(f"Event added to counter '{self.name}'")
        except sqlite3.DatabaseError as err:
            print(f"Error adding event to Counter: {err}")

    @classmethod
    def load (db, name):   ##delete 
        """Load a counter from the database by name"""
        cur = db.cursor()
        try:
            cur.execute("SELECT name, description FROM counter WHERE name = ?", (name,))
            result = cur.fetchone()
            if result:
                print(f"Counter '{name}' found")
            
            else:
                print(f"No counter with the name '{name}' exists. Please create a new counter")
                return None
        except sqlite3.DatabaseError as err:
            print (f"Error loading Counter:{err}")
            return None
        
    @staticmethod
    def list_all_counters(db):
        """List all counters in the database"""
        try:
            cur = db.cursor()
            cur.execute("SELECT name, description FROM counter")
            counter = cur.fetchall()
            if counter:
                print("These are the existing counter:")
                for name, description in counter:
                    print(f"- {name}: {description}")
            else:
                print("There are no counter in the database")
        except sqlite3.DatabaseError as err:
            print(f"Error loading counter from database: {err}")       







#db.py original code 
#replace habits with counter
#replave tasks with description

import sqlite3
from datetime import date 



def get_db(name = "my_database.db"):

    # Connect to the SQLite database file specified by 'name'
    print("Opening database connection...")
    db = sqlite3.connect(name, timeout=5)
    print("Database connection opened.")

    # Ensure the database schema is set up correctly
    #create_habits_table(db)

    # Return the database connection object
    return db

def create_habits_table(db):
    #Create habit and tracker tables

    print(f"DEBUG: Database connection: {db}")
    print("Opening cursor...")
    cur = db.cursor()

    print("Creating habit table...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS habits (
        id INTERGER PRIMARY KEY AUTOINCREMENT,
        task TEXT,
        count INTEGER NOT NULL DEFAULT 0
        )
    """)
    print ("habit table created successfully")
   
   
    # Check if the `habit` table exists
    cur.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='habit'
    """)
    table_exists = cur.fetchone()

    if table_exists:
        print("The `habit` table exists.")
    else:
        print("The `habit` table does not exist.")


    # Check the table schema
    cur.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='habit'
    """)
    table_exists = cur.fetchone()

    if table_exists:
        print("The `habit` table exists.")
        
        # Check the table schema
        cur.execute("PRAGMA table_info(habit)")
        columns = cur.fetchall()
        
        print("Columns in the `habit` table:")
        for column in columns:
            print(column)
    else:
        print("The `habit` table does not exist.")



    print("Creating tracker table...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tracker(
        date TEXT NOT NULL,
        currentCount INTEGER NOT NULL,
        habitName TEXT NOT NULL,
        FOREIGN KEY(habitName) REFERENCES habit(name) ON DELETE CASCADE
        )
    """)
    print("Tracker table created successfully")

    
    #Updates the currentCount column in the tracker table with the count column in the habit table
    cur.execute("""
        UPDATE tracker
        SET currentCount = (
            SELECT count
            FROM habit
            WHERE habitName = name
        )
        
    """)

    cur.execute(""" 
    CREATE TRIGGER IF NOT EXISTS update_tracker_count
    AFTER UPDATE OF count ON habit
    FOR EACH ROW
    BEGIN
        UPDATE tracker
        SET currentCount = NEW.count
        WHERE habitName = NEW.name;
    END
    """)

    print("Committing changes...")
    db.commit()
    print("Tables committed successfully")

def add_habit(db, name, task, count=0):
    #Add a habit to habit table in database
    try:
        print("DEBUG: Adding habit to the database...")
        cur = db.cursor()
        cur.execute(
            "INSERT INTO habit (name, task, count) VALUES(?, ?, ?)", 
            (name, task, count)
        )
        db.commit()
        print("DEBUG: habit added successfully")
        #return "habit added successfully"
    except sqlite3.IntegrityError:
        cur.execute("UPDATE habit SET task=? WHERE name=?", (description, name))
    

def increment_habit(db, name, event_date=None):
    cur= db.cursor()
    exist_habit = lookup_habit(db, name)
    if exist_habit:
       cur.execute("UPDATE habit SET count = count + 1 WHERE name=?", (name,)) 
       cur.execute("INSERT INTO tracker (date, currentCount, habitName) VALUES(?, (SELECT count FROM habit WHERE name=?), ?)", (event_date, name, name))
       db.commit()
       data = calculate_count(db, name)
       print(f"habit '{name}' incremented. New count: {data}")
    else:
        print(f"habit '{name}' does not exist")
        return False
    
    if not event_date:
        from datetime import date 
        event_date = str(date.today())
    else:
        pass

    db.commit()
    return "habit incremented successfully"

def get_habit_data(db, name):
    #Get the data from the habit table
    cur= db.cursor()
    cur.execute ("SELECT * FROM tracker WHERE habitName=? ORDER BY date ASC",(name,))      
    return cur.fetchall()

def calculate_count(db, name):
    data = get_habit_data(db, name)
    count = len(data)       
    return count

def printTable (db, table):
    cur = db.cursor()
    cur.execute(f"SELECT * FROM {table}")
    print(cur.fetchall())

def lookup_habit(db, name):
    print(f"DEBUG: Looking up habit '{name}'")
    try:
        cur = db.cursor()
        cur.execute("SELECT * FROM habit WHERE name=?", (name,))
        habit_exists = cur.fetchone()
        if habit_exists:
            print(f"habit '{name}' already exists")
            return True
        else:
            return False
    except sqlite3.DatabaseError as err:
        print(f"Error looking up habit: {err}")
        return False

def delete_habits_table(db, name):
    cur = db.cursor()
    cur.execute("DELETE FROM habit WHERE name=?", (name,))
    db.commit()
    return "habit deleted successfully"
    

#analyse.py original code

from db import get_counter_data

#def calculate_count(db, counter):
"""
Calculate the count of the counter

:param db: an initialized sqlite3 database connection
:param counter: name of the counter present in the DB
:return: length of the counter increment events 

"""
    #data = get_counter_data(db, counter)
    #return len(data)

#main.py original code
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




#old streak counter
def calculate_streak(self):
        """Calculate the current streak for the habit."""
        if not self.completion_dates:
            return 0
        
        if is_habit_broken(self):
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



def test_increment(temp_db):
    db, db_filename = temp_db
    create_counters_table(db)
    add_counter(db, "test_counter1", "test_description1")
    counter = Counter("test_counter1", "test_description1", 0)
    counter.store(db)
    increment_counter(db, "test_counter1", "2025-01-01")
    counter.count += 1 
    increment_counter(db, "test_counter1", "2025-01-02")
    counter.count += 1
    assert counter.name == "test_counter1"
    assert counter.description == "test_description1"
    assert counter.count == 2
    db.close()
    if os.path.exists(db_filename):
        os.remove(db_filename)

        def seed_demo_data():
    '''
    Wipes and resets database and inserts 5 habits(daily/weekly/monthly)
    Adds  realistic completions (with some randomness)
    Ensure “Read Stoicism” has no breaks for clean streak testing

    : param: None
    : return: None
    '''
    # Connect to the SQLite database
    conn = get_db()
    cursor = conn.cursor()

    # Reset tables if they exist
    cursor.execute("DELETE FROM completions")
    cursor.execute("DELETE FROM habits")
    conn.commit()

    # Predefined habits
    habits = [
        ("Drink Water", "daily"),           # Frequent habit
        ("Workout", "weekly"),              # Normal habit
        ("Read Stoicism", "daily"),         # This one will have NO breaks
        ("Clean Room", "weekly"),           
        ("Pay Bills", "monthly")
    ]

    habit_ids = {}
    today = datetime.today()

    # Add habits
    for name, periodicity in habits:
        add_habit(conn, name, periodicity)
        habit_id = cursor.execute("SELECT id FROM habits WHERE task = ?", (name,)).fetchone()[0]
        habit_ids[name] = habit_id

    # Backfill completions for the past 4 weeks
    start_date = today - timedelta(days=28)
    for offset in range(29):
        date = start_date + timedelta(days=offset)
        date_str = date.strftime("%Y-%m-%d")

        for name, periodicity in habits:
            habit_id = habit_ids[name]

            # "Read Stoicism" will have no breaks
            if name == "Read Stoicism":
                if periodicity == "daily":
                    add_completion(conn, habit_id, date_str)

            elif periodicity == "daily":
                if random.random() < 0.9:
                    add_completion(conn, habit_id, date_str)

            elif periodicity == "weekly" and date.weekday() == 6:  # Sundays
                if random.random() < 0.95:
                    add_completion(conn, habit_id, date_str)

            elif periodicity == "monthly" and date.day == 1:
                add_completion(conn, habit_id, date_str)

    conn.commit()
    conn.close()
    print("✅ Demo data seeded successfully.")
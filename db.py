import sqlite3
from datetime import date , timedelta



def get_db(name = "my_database.db"):

    # Connect to the SQLite database file specified by 'name'
    print("Opening database connection...")
    db = sqlite3.connect(name, timeout=5)
    print("Database connection opened.")

    # Ensure the database schema is set up correctly
    #create_habits_table(db)

    # Return the database connection object
    return db

def create_tables(db):
    cur = db.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            periodicity TEXT NOT NULL,
            creation_date TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            completion_date TEXT NOT NULL,
            FOREIGN KEY (habit_id) REFERENCES habits (id)
        )
    """)
    db.commit()

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
    


import sqlite3
from datetime import datetime

def get_db(name="my_database.db"):
    """
    Connect to the SQLite database.

    :param name: The name of the database file.
    :return: A database connection object.
    """
    db = sqlite3.connect(name)
    create_tables(db)
    return db

def create_tables(db):
    """
    Create the necessary tables in the database.
    """
    cur = db.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            periodicity TEXT NOT NULL,
            creation_date TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            completion_date TEXT NOT NULL,
            FOREIGN KEY (habit_id) REFERENCES habits (id)
        )
    """)
    db.commit()

def add_habit(db, task: str, periodicity: str):
    """
    Add a new habit to the database.

    :param db: The database connection.
    :param task: The task or name of the habit.
    :param periodicity: The periodicity of the habit ("daily" or "weekly").
    """
    cur = db.cursor()
    cur.execute(
        "INSERT INTO habits (task, periodicity, creation_date) VALUES (?, ?, ?)",
        (task, periodicity, str(datetime.now().date()))
    )
    db.commit()

def add_completion(db, habit_id: int, completion_date: str = None):
    """
    Add a completion date for a habit.

    :param db: The database connection.
    :param habit_id: The ID of the habit.
    :param completion_date: The date the habit was completed (default: current date).
    """
    if not completion_date:
        completion_date = str(datetime.now().date())

    cur = db.cursor()
    cur.execute(
        "INSERT INTO completions (habit_id, completion_date) VALUES (?, ?)",
        (habit_id, completion_date)
    )
    db.commit()


import sqlite3
from datetime import datetime

def get_db(name="my_database.db"):
    """
    Connect to the SQLite database.

    :param name: The name of the database file.
    :return: A database connection object.
    """
    db = sqlite3.connect(name)
    create_tables(db)
    return db

def create_tables(db):
    """
    Create the necessary tables in the database.
    """
    cur = db.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            periodicity TEXT NOT NULL,
            creation_date TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            completion_date TEXT NOT NULL,
            FOREIGN KEY (habit_id) REFERENCES habits (id)
        )
    """)
    db.commit()

def add_habit(db, task: str, periodicity: str):
    """
    Add a new habit to the database.

    :param db: The database connection.
    :param task: The task or name of the habit.
    :param periodicity: The periodicity of the habit ("daily" or "weekly").
    """
    cur = db.cursor()
    cur.execute(
        "INSERT INTO habits (task, periodicity, creation_date) VALUES (?, ?, ?)",
        (task, periodicity, str(datetime.now().date()))
    )
    db.commit()

def add_completion(db, habit_id: int, completion_date: str = None):
    """
    Add a completion date for a habit.

    :param db: The database connection.
    :param habit_id: The ID of the habit.
    :param completion_date: The date the habit was completed (default: current date).
    """
    today = datetime.now().date()

    if not completion_date:
        completion_date = str(datetime.now().date())

    #Get habit periodicity
    cur = db.cursor()
    cur.execute(
        "SELECT periodicity FROM habits WHERE id=?", (habit_id,)
    )
    habit = cur.fetchone()
    if not habit:
        print("Habit not found.")
        return

    periodicity = habit[0]

    # Get last completion date
    cur.execute("SELECT completion_date FROM completions WHERE habit_id=? ORDER BY completion_date DESC LIMIT 1", (habit_id,))
    last_completion = cur.fetchone()
    last_completion_date = datetime.strptime(last_completion[0], "%Y-%m-%d").date() if last_completion else None

  # Determine the period start
    if periodicity == "daily":
        period_start = today
    elif periodicity == "weekly":
        period_start = today - timedelta(days=today.weekday())  # Start of the week (Monday)

    
    # Check if the habit was already completed in the current period
    if last_completion_date and last_completion_date >= period_start:
        print(f"Habit already completed for the current {periodicity} period.")
        return

    cur.execute(
        "INSERT INTO completions (habit_id, completion_date) VALUES (?, ?)",
        (habit_id, completion_date)
    )
    db.commit()
    print (f"Habit checked for {periodicity} period")

def get_all_habits(db):
    """
    Retrieve all habits from the database.

    :param db: The database connection.
    :return: A list of all habits.
    """
    cur = db.cursor()
    cur.execute("SELECT * FROM habits")
    return cur.fetchall()

def get_completions(db, habit_id: int):
    """
    Retrieve all completion dates for a specific habit.

    :param db: The database connection.
    :param habit_id: The ID of the habit.
    :return: A list of completion dates.
    """
    cur = db.cursor()
    cur.execute("SELECT completion_date FROM completions WHERE habit_id=?", (habit_id,))
    return [row[0] for row in cur.fetchall()]
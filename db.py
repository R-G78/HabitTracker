import sqlite3
from datetime import date 



def get_db(name = "my_database.db"):

    # Connect to the SQLite database file specified by 'name'
    print("Opening database connection...")
    db = sqlite3.connect(name, timeout=5)
    print("Database connection opened.")

    # Ensure the database schema is set up correctly
    #create_counters_table(db)

    # Return the database connection object
    return db

def create_counters_table(db):
    #Create counter and tracker tables

    print(f"DEBUG: Database connection: {db}")
    print("Opening cursor...")
    cur = db.cursor()

    print("Creating counter table...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS counter( 
        name TEXT PRIMARY KEY, 
        description TEXT,
        count INTEGER NOT NULL DEFAULT 0
        )
    """)
    print ("Counter table created successfully")
   
   
    # Check if the `counter` table exists
    cur.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='counter'
    """)
    table_exists = cur.fetchone()

    if table_exists:
        print("The `counter` table exists.")
    else:
        print("The `counter` table does not exist.")


    # Check the table schema
    cur.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='counter'
    """)
    table_exists = cur.fetchone()

    if table_exists:
        print("The `counter` table exists.")
        
        # Check the table schema
        cur.execute("PRAGMA table_info(counter)")
        columns = cur.fetchall()
        
        print("Columns in the `counter` table:")
        for column in columns:
            print(column)
    else:
        print("The `counter` table does not exist.")



    print("Creating tracker table...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tracker(
        date TEXT NOT NULL,
        currentCount INTEGER NOT NULL,
        counterName TEXT NOT NULL,
        FOREIGN KEY(counterName) REFERENCES counter(name) ON DELETE CASCADE
        )
    """)
    print("Tracker table created successfully")

    
    #Updates the currentCount column in the tracker table with the count column in the counter table
    cur.execute("""
        UPDATE tracker
        SET currentCount = (
            SELECT count
            FROM counter
            WHERE counterName = name
        )
        
    """)

    cur.execute(""" 
    CREATE TRIGGER IF NOT EXISTS update_tracker_count
    AFTER UPDATE OF count ON counter
    FOR EACH ROW
    BEGIN
        UPDATE tracker
        SET currentCount = NEW.count
        WHERE counterName = NEW.name;
    END
    """)

    print("Committing changes...")
    db.commit()
    print("Tables committed successfully")

def add_counter(db, name, description, count=0):
    #Add a counter to counter table in database
    try:
        print("DEBUG: Adding counter to the database...")
        cur = db.cursor()
        cur.execute(
            "INSERT INTO counter (name, description, count) VALUES(?, ?, ?)", 
            (name, description, count)
        )
        db.commit()
        print("DEBUG: Counter added successfully")
        #return "Counter added successfully"
    except sqlite3.IntegrityError:
        cur.execute("UPDATE counter SET description=? WHERE name=?", (description, name))
    

def increment_counter(db, name, event_date=None):
    cur= db.cursor()
    exist_counter = lookup_counter(db, name)
    if exist_counter:
       cur.execute("UPDATE counter SET count = count + 1 WHERE name=?", (name,)) 
       cur.execute("INSERT INTO tracker (date, currentCount, counterName) VALUES(?, (SELECT count FROM counter WHERE name=?), ?)", (event_date, name, name))
       db.commit()
       data = calculate_count(db, name)
       print(f"Counter '{name}' incremented. New count: {data}")
    else:
        print(f"Counter '{name}' does not exist")
        return False
    
    if not event_date:
        from datetime import date 
        event_date = str(date.today())
    else:
        pass

    db.commit()
    return "Counter incremented successfully"

def get_counter_data(db, name):
    #Get the data from the counter table
    cur= db.cursor()
    cur.execute ("SELECT * FROM tracker WHERE counterName=? ORDER BY date ASC",(name,))      
    return cur.fetchall()

def calculate_count(db, name):
    data = get_counter_data(db, name)
    count = len(data)       
    return count

def printTable (db, table):
    cur = db.cursor()
    cur.execute(f"SELECT * FROM {table}")
    print(cur.fetchall())

def lookup_counter(db, name):
    print(f"DEBUG: Looking up counter '{name}'")
    try:
        cur = db.cursor()
        cur.execute("SELECT * FROM counter WHERE name=?", (name,))
        counter_exists = cur.fetchone()
        if counter_exists:
            print(f"Counter '{name}' already exists")
            return True
        else:
            return False
    except sqlite3.DatabaseError as err:
        print(f"Error looking up Counter: {err}")
        return False

def delete_counters_table(db, name):
    cur = db.cursor()
    cur.execute("DELETE FROM counter WHERE name=?", (name,))
    db.commit()
    return "Counter deleted successfully"
    

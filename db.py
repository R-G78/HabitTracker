import sqlite3
from datetime import date 

def get_db(name = "my_database.db"):

    # Connect to the SQLite database file specified by 'name'
    print("Opening database connection...")
    db = sqlite3.connect(name, timeout=5)
    print("Database connection opened.")

    # Ensure the database schema is set up correctly
    create_counters_table(db)

    # Return the database connection object
    return db

def create_counters_table(db):
    print(f"DEBUG: Database connection: {db}")
    print("Opening cursor...")
    cur = db.cursor()

    print("Crrating counter table...")
    cur.execute("""CREATE TABLE IF NOT EXISTS counter( 
        name TEXT PRIMARY KEY, 
        description TEXT)""")
    print ("Counter table created successfully")

    print("Creating tracker table...")
    cur.execute("""CREATE TABLE IF NOT EXISTS tracker(
        date TEXT NOT NULL,
        counterName TEXT NOT NULL,
        FOREIGN KEY(counterName) REFERENCES counter(name) ON DELETE CASCADE)""")
    print("Tracker table created successfully")

    print("Committing changes...")
    db.commit()
    print("Tables committed successfully")

def add_counter(db, name, description):
    try:
        print("DEBUG: Adding counter to the database...")
        cur = db.cursor()
        cur.execute(""""
            INSERT INTO counter (name, description)
            VALUES(?, ?)
        """, (name, description))
        db.commit()
        print("DEBUG: Counter added successfully")
        #return "Counter added successfully"
    except sqlite3.IntegrityError:
        cur.execute("UPDATE counter SET description=? WHERE name=?", (description, name))
    

def increment_counter(db, name, event_date=None):
    cur= db.cursor()
    cur.execute("SELECT * FROM counter WHERE name=?", (name,))
    if not cur.fetchone():
        return "Counter does not exist"
    
    if not event_date:
        from datetime import date 
        event_date = str(date.today())

    cur.execute("INSERT INTO tracker (date, counterName) VALUES(?, ?)", (event_date, name))
    db.commit()
    return "Counter incremented successfully"

def get_counter_data(db, name):
    cur= db.cursor()
    cur.execute ("SELECT * FROM tracker WHERE counterName=? ORDER BY date ASC",(name,))      
    return cur.fetchall()

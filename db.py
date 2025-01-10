import sqlite3
from datetime import date 

def get_db(name = "main.db"):

    #Path to my SQLite database file
    db_path = "my_database.db"

    # Connect to the SQLite database file specified by 'name'
    db = sqlite3.connect(db_path)

    # Ensure the database schema is set up correctly
    create_counters_table(db)

    # Return the database connection object
    return db

def create_counters_table(db):
    cur = db.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS counter( 
        name TEXT PRIMARY KEY, 
        description TEXT)""")

    cur.execute("""CREATE TABLE IF NOT EXISTS tracker(
        date TEXT NOT NULL,
        counterName TEXT NOT NULL,
        FOREIGN KEY(counterName) REFERENCES counter(name) ON DELETE CASCADE)""")
    
    db.commit()


def add_counter(db, name, description):
    
    cur = db.cursor()
    try:
        cur.execute("INSERT INTO counter VALUES(?, ?)", (name, description))
        db.commit()
        return "Counter added successfully"
    except sqlite3.IntegrityError:
        cur.execute("UPDATE counter SET description=? WHERE name=?", (description, name))
    

def increment_counter(db, name, event_date=None):
    cur= db.cursor()
    cur.excecute("SELECT * FROM counter WHERE name=?", (name,))
    if not cur.fetchone():
        return "Counter does not exist"
    
    if not event_date:
        from datetime import date 
        event_date = str(date.today())

    cur.execute("INSERT INTO tracker VALUES(?, ?)", (event_date, name))
    db.commit()
    return "Counter incremented successfully"

def get_counter_data(db, name):
    cur= db.cursor()
    cur.execute("SELECT * FROM tracker WHERE counterName=? ORDER BY date ASC", (name,))
    return cur.fetchall()

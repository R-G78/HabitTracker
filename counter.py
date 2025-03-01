from db import add_counter, increment_counter
from analyse import calculate_count
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
    def load (db, name):
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




from db import add_counter, increment_counter
from analyse import calculate_count
import sqlite3

class Counter:

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.count = 0
        

    def increment(self):
        try:
            """Increment the counter and update the database"""
            self.count += 1 
            increment_counter(self.name)
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
            cur = db.cursor()
            cur.execute("SELECT name FROM counters WHERE name= ?", (self.name,))
            if cur.fetchone():
                print(f"Counter '{self.name}' already exists")
                return 
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
    def load (cls, db, name):
        """Load a counter from the database by name"""
        cur = db.cursor()
        try:
            cur.execute("SELECT name, description FROM counters WHERE name = ?", (name,))
            result = cur.fetchone()
            if result:
                name, description  = result
                counter = cls(name, description) # Create a Counter object
                counter.count = calculate_count(db, name) #Initialize count 
                print(f"Counter '{name}' loaded")
                return counter
            
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
            cur.execute("SELECT name, description FROM counters")
            counters = cur.fetchall()
            if counters:
                print("These are the existing counters:")
                for name, description in counters:
                    print(f"- {name}: {description}")
            else:
                print("There are no counters in the database")
        except sqlite3.DatabaseError as err:
            print(f"Error loading counters from database: {err}")       




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


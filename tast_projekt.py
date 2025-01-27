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
from cli import cli
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
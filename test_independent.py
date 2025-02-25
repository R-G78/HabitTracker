# Description: This file contains the test cases for the independent functions of the project.

import os
import sqlite3
import pytest
import questionary
from main import cli
from db import get_db, add_counter, increment_counter, get_counter_data, create_counters_table
from counter import Counter
from analyse import calculate_count
from io import StringIO
import sys


@pytest.fixture
def temp_db():
    """Fixture to create a temporary SQLite database for testing."""
    db_filename = "temp_test.db"
    db = get_db(db_filename)
    print ("DEBUG: Opening DB in finction temp_db")
    
    yield db  # Provide the database to the tests

    # Cleanup
    db.close()
    if os.path.exists(db_filename):
        os.remove(db_filename)


def test_create(temp_db, monkeypatch):
    """Test the 'Create' option of the CLI."""
    
    print ("Test Started: test_create")

   #Mock questionary functions
    def mock_confirm(prompt=None):
        print(f"questionary.confirm called with prompt: {prompt}")  # Debugging print
        return True  # Always return True for confirmation

    def mock_select(prompt, choices):
        print(f"questionary.select called with prompt: {prompt}, choices: {choices}")  # Debugging print   
        return "Create"  # Always select "Create"

    def mock_text(prompt):
        print(f"questionary.text called with prompt: {prompt}")
        if "name" in prompt:
            return "test_counter"  #mocking the counter name
        elif "description" in prompt:
            return "test_description" #mocking the counter description
        else:
            return "" #default return
       
    #Apply fake monkeypatches
    #monkeypatch.setattr(questionary, "text", lambda *args, **kwargs: questionary.fake("Test Response"))

    # Apply actual monkeypatches
    monkeypatch.setattr(questionary, "confirm", mock_confirm)
    monkeypatch.setattr(questionary, "select", mock_select)
    monkeypatch.setattr(questionary, "text", mock_text)
   
    # Redirect stdout to capture CLI output
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    print("Test Started: Before Cli")
    #try:
       # cli()
        #print("CLI Execution Finished Normally")
    #except Exception as e:
        #print(f"CLI Execution Error: {e}")
    #print("Test Ended: test_create")  

    print("DEBUG: About to call cli()")  # Add this line
    cli()
    print("DEBUG: cli() call completed")  # Add this line

    # Reset stdout
    output = sys.stdout.getvalue()
    sys.stdout = old_stdout

    # Verify the counter exists in the database
    cursor = temp_db.cursor()
    cursor.execute("SELECT name, description FROM counter WHERE name = ?", ("test_counter",))
    result = cursor.fetchone()

    assert result is not None
    assert result == ("test_counter", "test_description")
    assert "Counter 'test_counter' created" in output


def test_cli_increment(temp_db, monkeypatch):
    """Test the 'Increment' option of the CLI."""
    add_counter(temp_db, "test_counter", "test_description")

    inputs = iter([
        "yes",            # Confirm "Are you ready?"
        "Increment",      # Select "Increment"
        "test_counter",   # Enter counter name
        "Exit"            # Exit CLI
    ])

    def mock_input(prompt):
        return next(inputs)

    monkeypatch.setattr("builtins.input", mock_input)

    # Redirect stdout to capture CLI output
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    cli()

    # Reset stdout
    output = sys.stdout.getvalue()
    sys.stdout = old_stdout

    # Verify the counter was incremented
    cursor = temp_db.cursor()
    cursor.execute("""
    SELECT COUNT(*) FROM tracker WHERE counterName = ?
    """, ("test_counter",))
    result = cursor.fetchone()

    assert result[0] == 1
    assert "Counter'test_counter has been incremented." in output


def test_cli_analyse(temp_db, monkeypatch):
    """Test the 'Analyse' option of the CLI."""
    add_counter(temp_db, "test_counter", "test_description")
    increment_counter(temp_db, "test_counter", "2025-01-01")
    increment_counter(temp_db, "test_counter", "2025-01-02")

    inputs = iter([
        "yes",            # Confirm "Are you ready?"
        "Analyse",        # Select "Analyse"
        "test_counter",   # Enter counter name
        "Exit"            # Exit CLI
    ])

    def mock_input(prompt):
        return next(inputs)

    monkeypatch.setattr("builtins.input", mock_input)

    # Redirect stdout to capture CLI output
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    cli()

    # Reset stdout
    output = sys.stdout.getvalue()
    sys.stdout = old_stdout

    # Verify the count analysis
    assert "Count for test_counter: 2" in output


def test_cli_exit(temp_db, monkeypatch):
    """Test the 'Exit' option of the CLI."""
    inputs = iter([
        "yes",      # Confirm "Are you ready?"
        "Exit"      # Select "Exit"
    ])

    def mock_input(prompt):
        return next(inputs)

    monkeypatch.setattr("builtins.input", mock_input)

    # Redirect stdout to capture CLI output
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    cli()

    # Reset stdout
    output = sys.stdout.getvalue()
    sys.stdout = old_stdout

    # Verify exit message
    assert "Goodbye!" in output


def test_counter_class(temp_db):
    """Test the Counter class functionality."""
    counter = Counter("test_counter", "test_description")

    # Test storing the counter
    counter.store(temp_db)
    cursor = temp_db.cursor()
    cursor.execute("SELECT name, description FROM counter WHERE name = ?", ("test_counter",))
    result = cursor.fetchone()
    assert result == ("test_counter", "test_description")

    # Test incrementing the counter
    counter.increment(temp_db)
    count = calculate_count(temp_db, "test_counter")
    assert count == 1

    # Test resetting the counter
    counter.reset()
    assert counter.count == 0


def test_calculate_count(temp_db):
    """Test the calculate_count function."""
    add_counter(temp_db, "test_counter", "test_description")
    increment_counter(temp_db, "test_counter", "2025-01-01")
    increment_counter(temp_db, "test_counter", "2025-01-02")

    count = calculate_count(temp_db, "test_counter")
    assert count == 2



    """Here’s a detailed breakdown of the new test file without unittest. The file was structured for use with pytest and directly tests the cli.py functionality:

Imports

import os
import sqlite3
import pytest
from counter import Counter
from db import get_db, create_counters_table
from analyse import calculate_count
from cli import cli

	•	os: Used to delete the temporary test database after the tests complete.
	•	sqlite3: To handle SQLite operations for testing purposes.
	•	pytest: A testing framework used to execute test cases and handle assertions.
	•	Application-Specific Imports: Imports functionality from your project, such as Counter, get_db, and cli.

Fixture for Temporary Database

@pytest.fixture
def test_db():
    db_filename = "test_cli.db"
    db = get_db(db_filename)
    create_counters_table(db)
    yield db  # Provide the database connection to tests
    db.close()
    os.remove(db_filename)

	•	This creates a temporary database for the tests (test_cli.db) and ensures it’s cleaned up after the test suite is done.
	•	yield: Allows the test function to use the database. Once the test finishes, the cleanup code (closing the database and removing the file) runs.

Helper Functions

def add_test_data(db):
    cursor = db.cursor()
    cursor.execute("INSERT INTO counter (name, description) VALUES (?, ?)", ("test_counter", "Test Description"))
    db.commit()

	•	Purpose: Preloads test data into the counter table, which is used in the test cases.
	•	Inserts a counter named "test_counter" with a description "Test Description" into the database.

Test: Counter Creation

def test_counter_creation(test_db):
    counter = Counter("new_counter", "New Description")
    counter.store(test_db)
    cursor = test_db.cursor()
    cursor.execute("SELECT name, description FROM counter WHERE name = ?", ("new_counter",))
    result = cursor.fetchone()
    assert result == ("new_counter", "New Description")

	1.	Creates a Counter: Uses the Counter class to create and store a counter named "new_counter".
	2.	Verifies Storage: Queries the database to check if the counter exists with the correct name and description.
	3.	Assertion: Ensures the database entry matches the expected values.

Test: Increment Counter

def test_counter_increment(test_db):
    add_test_data(test_db)
    counter = Counter.load(test_db, "test_counter")
    counter.increment(test_db)
    count = calculate_count(test_db, "test_counter")
    assert count == 1

	1.	Preloads Test Data: Adds a counter named "test_counter" using add_test_data.
	2.	Loads Counter: Retrieves the counter from the database using Counter.load.
	3.	Increments Counter: Calls increment() to simulate an increment event.
	4.	Validates Increment: Uses calculate_count to confirm the counter has been incremented once.

Test: Analyse Counter

def test_analyse_counter(test_db):
    add_test_data(test_db)
    counter = Counter.load(test_db, "test_counter")
    for _ in range(3):
        counter.increment(test_db)
    count = calculate_count(test_db, "test_counter")
    assert count == 3

	1.	Preloads Test Data: Adds a test counter (test_counter).
	2.	Simulates Events: Increments the counter 3 times.
	3.	Checks Total Count: Uses calculate_count to confirm that the counter has been incremented 3 times.

Test: CLI Workflow

def test_cli_workflow(mocker, test_db):
    mocker.patch("questionary.confirm", side_effect=[True, True, False])
    mocker.patch("questionary.select", side_effect=["Create", "Exit"])
    mocker.patch("questionary.text", side_effect=["cli_test_counter", "CLI Test Description"])
    cli()
    cursor = test_db.cursor()
    cursor.execute("SELECT name, description FROM counter WHERE name = ?", ("cli_test_counter",))
    result = cursor.fetchone()
    assert result == ("cli_test_counter", "CLI Test Description")

	1.	Mocks User Input: Replaces questionary prompts with pre-defined responses using side_effect to simulate user interaction.
	•	confirm: Simulates confirming readiness and counter creation.
	•	select: Simulates selecting the "Create" and "Exit" options in the CLI.
	•	text: Simulates entering the counter name and description.
	2.	Runs CLI: Executes the cli() function.
	3.	Verifies Creation: Queries the database to confirm the counter was created with the expected name and description.

Test Cleanup

The test_db fixture ensures the database is closed and removed after the tests. This happens automatically for each test that uses the test_db fixture.

Key Points:
	1.	No unittest: This file relies on pytest for testing and assertions.
	2.	Isolation: Each test uses its own temporary database, ensuring tests don’t interfere with each other.
	3.	Direct Assertions: Tests validate behavior by directly querying the database and comparing results to expected values.
	4.	Simulated CLI Interaction: The test_cli_workflow test demonstrates how to simulate user input for CLI workflows.

Let me know if you have more questions or need further explanation! 😊"""
from db import create_counters_table, add_counter, get_db  
import os
import pytest

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

def test_database_operations(temp_db):
    """Test database operations (create table, add counter)."""
    print("Test Started: test_database_operations")

    # Create the counters table
    create_counters_table(temp_db)
    print("DEBUG: Counters table created")

    # Add a counter to the database
    add_counter(temp_db, "test_counter", "test_description")
    print("DEBUG: Counter added to database")

    # Verify the counter exists in the database
    cursor = temp_db.cursor()
    cursor.execute("SELECT name, description FROM counter WHERE name = ?", ("test_counter",))
    result = cursor.fetchone()

    assert result is not None
    assert result == ("test_counter", "test_description")
    print("Test Passed: Counter exists in database")
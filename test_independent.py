import os
import pytest 
from db import get_db, create_counters_table, add_counter, increment_counter, get_counter_data
from counter import Counter
from analyse import calculate_count 

@pytest.fixture
def temp_db():
    """Fixture to create a temporary SQLite database for testing."""
    db_filename = "temp_test.db"
    db = get_db(db_filename)
    print ("DEBUG: Opening DB in finction temp_db")
    
    yield db  # Provide the database to the tests
    
    db.close()
    if os.path.exists(db_filename):
        os.remove(db_filename)


def test_create():
    db = get_db()
    create_counters_table(db)
    add_counter(db, "test_counter", "test_description")
    counter = Counter("test_counter", "test_description", 0)
    counter.store(db)
    assert counter.name == "test_counter"
    assert counter.description == "test_description"
    assert counter.count == 0

    db.close()


def test_increment():
    pass

def test_analyse():
    pass 

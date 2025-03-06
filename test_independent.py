import os
import pytest 
from db import get_db, create_counters_table, add_counter, increment_counter, get_counter_data
from counter import Counter


@pytest.fixture
def temp_db():
    """Fixture to create a temporary SQLite database for testing."""
    db_filename = "temp_test.db"
    db = get_db(db_filename)
    
    yield db, db_filename  # Provide the database and filename to the tests
    

def test_create(temp_db):
    db, db_filename = temp_db
    create_counters_table(db)
    add_counter(db, "test_counter", "test_description")
    counter = Counter("test_counter", "test_description", 0)
    counter.store(db)
    assert counter.name == "test_counter"
    assert counter.description == "test_description"
    assert counter.count == 0
    db.close()
    if os.path.exists(db_filename):
        os.remove(db_filename)


def test_increment(temp_db):
    db, db_filename = temp_db
    create_counters_table(db)
    add_counter(db, "test_counter1", "test_description1")
    counter = Counter("test_counter1", "test_description1", 0)
    counter.store(db)
    increment_counter(db, "test_counter1", "2025-01-01")
    counter.count += 1 
    increment_counter(db, "test_counter1", "2025-01-02")
    counter.count += 1
    assert counter.name == "test_counter1"
    assert counter.description == "test_description1"
    assert counter.count == 2
    db.close()
    if os.path.exists(db_filename):
        os.remove(db_filename)

def test_analyse():
    pass 


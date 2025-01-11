import os
import sqlite3
import pytest
from counter import Counter
from db import get_db, add_counter, increment_counter, get_counter_data
from analyse import calculate_count

# Test database setup
@pytest.fixture
def test_db():
    db_filename = "test_independent.db"
    db = get_db(db_filename)
    # Ensure a clean state for every test
    yield db
    db.close()
    os.remove(db_filename)

def test_add_and_increment_counter(test_db):
    """Test adding a counter and incrementing it."""
    add_counter(test_db, "test_counter", "Test counter description")
    
    # Verify counter was added
    data = get_counter_data(test_db, "test_counter")
    assert len(data) == 0  # Initially, no increments

    # Increment counter
    increment_counter(test_db, "test_counter", "2025-01-01")
    increment_counter(test_db, "test_counter", "2025-01-02")
    
    # Verify increments
    data = get_counter_data(test_db, "test_counter")
    assert len(data) == 2  # Two increments added
    assert data[0] == ("2025-01-01", "test_counter")
    assert data[1] == ("2025-01-02", "test_counter")

def test_counter_class_store(test_db):
    """Test the Counter class `store` method."""
    counter = Counter("test_counter_class", "A test counter using the Counter class")
    counter.store(test_db)
    
    # Verify counter was stored
    data = get_counter_data(test_db, "test_counter_class")
    assert len(data) == 0  # No increments added yet

    # Add increments using the class method
    counter.increment(test_db, "2025-01-01")
    counter.increment(test_db, "2025-01-02")
    
    # Verify increments
    data = get_counter_data(test_db, "test_counter_class")
    assert len(data) == 2
    assert data[0] == ("2025-01-01", "test_counter_class")
    assert data[1] == ("2025-01-02", "test_counter_class")

def test_analyse_calculate_count(test_db):
    """Test the calculate_count function from analyse."""
    # Add some data
    add_counter(test_db, "habit1", "Description for habit1")
    increment_counter(test_db, "habit1", "2025-01-01")
    increment_counter(test_db, "habit1", "2025-01-01")
    increment_counter(test_db, "habit1", "2025-01-02")
    
    totals = calculate_count(test_db)
    
    # Verify calculated totals
    assert len(totals) == 1
    assert totals["habit1"] == 3  # Two increments on 2025-01-01 and one on 2025-01-02
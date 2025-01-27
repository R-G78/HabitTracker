import pytest 
from unittest.mock import patch, MagicMock
from main import cli
from counter import Counter 
from db import get_db, add_counter, increment_counter, get_counter_data
from analyse import calculate_count

@pytest.fixture
def mock_db():
    db_mock = MagicMock()
    return db_mock

#Test for the create option in the cli
@patch("cli.get_db")
@patch("clo.questionary")
@patch("cli.Counter")    
@patch ("cli.create_counters_table")
def tets_cli_create(mock_create_counters_table, mock_counter, mock_questionary, mock_get_db, mock_db):
    mock_get_db.return_value = mock_db
    mock_questionary.confirm.side_effect = [True, True] #Simulates "Are you ready?" and "Create" confirmations
    mock_questionary.select.side_effect = ["Create", "Exit"]
    mock_questionary.text.side_effect = ["test_counter","test_description"]

    cli()

    mock_create_counters_table.assert_called_once_with(mock_db)
    mock_counter.return_value.store.assert_called_once_with(mock_get_db)

#Test for the increment option in the cli
@patch("cli.get_db")
@patch("cli.questionary")
@patch("cli.Counter")
def test_cli_increment(Mock_counter,mock_questionary, mock_get_db, mock_db):
    mock_get_db.return_value = mock_db
    mock_counter.load.return_value = Counter("test_counter","Test_description")
    mock_counter.load.return_value.count = 0
    mock_questionary.confirm.return_value.ask.return_value = True
    mock_questionary.select.side_effect = ["Increment", "Exit"]
    mock_questionary.text.side_effect = ["test_counter"]

    cli()

    mock_counter.load.assert_called_once_with(mock_db, "test_counter")
    mock_counter.load.return_value.increment.assert_called_once_with(mock_db)

#Test for the analyse option in the cli
@patch("cli.get_db")
@patch("cli.questionary")
def test_cli_exit(mock_questionary, mock_get_db):
    mock_get_db.return_value = None
    mock_questionary.confirm.return_value.ask.return_value = True
    mock_questionary.select.side_effect = ["Exit"]

    cli()
        
    mock_questionary.select.assert_called_once_with(
        "What do you want to do?",
        choices = ["Create", "Increment","Analyse", "Exit"]
    )
    
#Test the Counter class
@patch("counter.calculate_count") 
@patch("db.addcounter")   
@patch("db.increment_counter")

def test_counter_class(mock_increment_counter, mock_add_counter, mock_calculate_count, mock_db):
    counter = Counter("test_counter","test_description")    
    
    #Test storing the counter
    counter.store(mock_db)
    mock_add_counter.assert_called_once_with(mock_db, "test_counter", "test_description")

    #Test incrementing the counter
    counter.increment(mock_db)
    mock_increment_counter.assert_called_once_with(mock_db, "test_counter")

    #Test resetting the counter
    counter.reset()
    assert counter.count == 0

    # Test calculating the count 
    mock_calculate_count.return_value = 10
    assert calculate_count(mock_db, "test_counter") == 10

@patch("db.get_counter_data")
def test_calculate_count(mock_get_counter_data,mock_db):
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


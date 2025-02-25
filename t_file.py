import sqlite3
from db import create_counters_table

db = sqlite3.connect("my_database.db")  # Use an in-memory database
create_counters_table(db)
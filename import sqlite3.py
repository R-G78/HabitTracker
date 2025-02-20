import sqlite3
db = sqlite3.connect("temp_test.db")
print("Connected successfully!")
db.close()
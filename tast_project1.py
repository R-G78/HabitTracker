from counter import Counter
from db import get_db, add_counter, increment_counter, get_counter_data
from analyse import calculate_count

class TestCounter:

    def setup_method(self):
        self.db= get_db("test.db")
        
        add_counter(self.db, "test_counter", "test_description")
        increment_counter(self.db, "test_counter", "2024-12-07")
        increment_counter(self.db, "test_counter", "2024-12-08")

        increment_counter(self.db, "test_counter", "2024-12-09")
        increment_counter(self.db, "test_counter", "2024-12-10")
        increment_counter(self.db, "test_counter", "2024-12-11")
       

    
    

    def test_counter(self):
        counter = Counter("test_counter_1", "test_description_1" )
        counter.store(self.db)


        counter.increment()
        counter.add_event(self.db)
        counter.reset()
        counter.increment()

    
    def test_reset_database(self):
        self.db.execute("DELETE FROM test_counter")
        self.db.commit()
        assert get_counter_data(self.db, "test_counter") is None

    def teardown_method(self):
        import os
        os.remove("test.db")   

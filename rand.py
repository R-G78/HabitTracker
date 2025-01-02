def test_db_counter(self):
        data = get_counter_data(self.db, "test_counter")
        assert len(data) == 5

        count = calculate_count(self.db,"test_counter")
        assert count == 5

def teardown_method(self):
        import os
        os.remove("test.db")   
import sqlite3

class SQL_liteDB:
    def __init__(self):
        self.initialize_db()
        self.ensure_tables_exist()  # Call the function during initialization

    def ensure_tables_exist(self):
        periods = ['day', 'week', 'month', 'season', 'year']  # Define the periods
        for period in periods:
            self.ensure_table_exists(period)  # Check each table

    def ensure_table_exists(self, period):
        # Connect to the SQLite database
        conn = sqlite3.connect('readings.db')

        # Create a cursor
        c = conn.cursor()

        # Define table name based on the period
        table_name = f'{period}_averages'

        # Check if the table already exists
        c.execute(f'''
            SELECT count(name) 
            FROM sqlite_master 
            WHERE type='table' AND name='{table_name}'
        ''')

        # If the count is 1, then table exists
        if c.fetchone()[0] == 1:
            print(f'Table {table_name} already exists.')
        else:
            print(f'Table {table_name} does not exist. Creating it now.')
            # Create the table
            c.execute(f'''
                CREATE TABLE {table_name} (
                    unit INTEGER,
                    parameter TEXT,
                    value REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

        # Commit the changes and close the connection
        conn.commit()
        conn.close()


    def initialize_db(self):
        print("DB ONLINE")
        # Connect to the SQLite database (it will be created if it doesn't exist)
        conn = sqlite3.connect('readings.db')

        # Create a cursor
        c = conn.cursor()

        # Create a table to store the readings
        c.execute('''
            CREATE TABLE IF NOT EXISTS readings (
                unit INTEGER,
                parameter TEXT,
                value REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create a table to store the daily averages
        c.execute('''
            CREATE TABLE IF NOT EXISTS daily_averages (
                unit INTEGER,
                parameter TEXT,
                value REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create a table to store the weekly averages
        c.execute('''
            CREATE TABLE IF NOT EXISTS weekly_averages (
                unit INTEGER,
                parameter TEXT,
                value REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create a table to store the monthly averages
        c.execute('''
            CREATE TABLE IF NOT EXISTS monthly_averages (
                unit INTEGER,
                parameter TEXT,
                value REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create a table to store the seasonal averages
        c.execute('''
            CREATE TABLE IF NOT EXISTS seasonal_averages (
                unit INTEGER,
                parameter TEXT,
                value REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create a table to store the yearly averages
        c.execute('''
            CREATE TABLE IF NOT EXISTS yearly_averages (
                unit INTEGER,
                parameter TEXT,
                value REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

    def store_reading(self, unit, parameter, value):
        # Connect to the SQLite database
        conn = sqlite3.connect('readings.db')

        # Create a cursor
        c = conn.cursor()

        # Insert the reading into the database
        c.execute('INSERT INTO readings (unit, parameter, value) VALUES (?, ?, ?)', (unit, parameter, value))

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

    def store_average(self, period, unit, parameter, value):
        # Connect to the SQLite database
        conn = sqlite3.connect('readings.db')

        # Create a cursor
        c = conn.cursor()

        # Define table name based on the period
        table_name = f'{period}_averages'

        # Insert the average reading into the correct table
        c.execute(f'INSERT INTO {table_name} (unit, parameter, value) VALUES (?, ?, ?)', (unit, parameter, value))

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

    def get_readings(self, unit, parameter):
        # Connect to the SQLite database
        conn = sqlite3.connect('readings.db')

        # Create a cursor
        c = conn.cursor()

        # Query the database for readings
        c.execute('SELECT value, timestamp FROM readings WHERE unit = ? AND parameter = ?', (unit, parameter))

        # Fetch all the readings
        readings = c.fetchall()

        # Close the connection
        conn.close()

        # Return the readings
        return readings

    def get_all_readings(self, period):
        # Connect to the SQLite database
        conn = sqlite3.connect('readings.db')

        # Create a cursor
        c = conn.cursor()

        # Define table name based on the period
        table_name = f'{period}_averages'

        # Query the database for all readings
        c.execute(f'SELECT * FROM {table_name}')

        # Fetch all the readings
        readings = c.fetchall()

        # Close the connection
        conn.close()

        # Return the readings
        return readings

    def query_readings(self, unit, start_time, end_time):
        # Connect to the SQLite database
        conn = sqlite3.connect('readings.db')

        # Create a cursor
        c = conn.cursor()

        # Query the database for readings within the specified time range
        c.execute('''
            SELECT unit, parameter, value, timestamp
            FROM readings
            WHERE unit = ? AND timestamp >= ? AND timestamp <= ?
        ''', (unit, start_time, end_time))

        # Fetch all the readings
        readings = c.fetchall()

        # Close the connection
        conn.close()

        # Return the readings
        return readings
    def get_readings_last_24_hours(self, unit, parameter):
        # Connect to the SQLite database
        conn = sqlite3.connect('readings.db')

        # Create a cursor
        c = conn.cursor()

        # Query the database for readings
        c.execute('''
            SELECT value, timestamp 
            FROM readings 
            WHERE unit = ? AND parameter = ? AND timestamp >= datetime('now', '-1 day')
        ''', (unit, parameter))

        # Fetch all the readings
        readings = c.fetchall()

        # Close the connection
        conn.close()

        # Return the readings
        return readings

    def get_averages(self, period, unit, parameter):
        # Connect to the SQLite database
        conn = sqlite3.connect('readings.db')

        # Create a cursor
        c = conn.cursor()

        # Define table name based on the period
        table_name = f'{period}_averages'

        # Query the database for averages
        c.execute(f'SELECT value, timestamp FROM {table_name} WHERE unit = ? AND parameter = ?', (unit, parameter))

        # Fetch all the averages
        averages = c.fetchall()

        # Close the connection
        conn.close()

        # Return the averages
        return averages

    def clear_data(self, period):
        # Connect to the SQLite database
        conn = sqlite3.connect('readings.db')

        # Create a cursor
        c = conn.cursor()

        # Define table name based on the period
        table_name = f'{period}_averages'

        # Delete all entries from the specified table
        c.execute(f'DELETE FROM {table_name}')

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

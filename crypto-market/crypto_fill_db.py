import psycopg2 as pg
from binance.spot import Spot
import os
import time



class PREPDATA:
    # Initialize variables to be used
    def __init__(self, symbol: str) -> None:
        self.symbol = symbol.upper()
        self.date = ''
        self.open = 0
        self.high = 0
        self.low = 0
        self.close = 0
        self.vol = 0
        self.end = 0
        # The connection parameters below should be modified to match your database settings
        self.db_params = {
            'host': os.environ.get("PGHOST"),
            'database': os.environ.get("PGDBNAME"),
            'user': os.environ.get("PGUSERNAME"),
            'password': os.environ.get("PGDBPASS"),
            'port': os.environ.get("PGDBPORT"),
        }
    
    def __str__(self) -> str:
        return("Symbol: {0}, Date: {1}, Open: {2}, High: {3}, Low:{4}, Close: {5}, Volume: {6}\nParams: {7}".format(
            self.symbol, self.date, self.open, self.high, self.low, self.close, self.vol, self.db_params))
    
    def getData(self, tf: str="4h") -> list:
        # Connect to the Binance API to retrieve data
        url = 'https://api.binance.us'
        the_key = os.environ.get("BINANCE_API_KEY")
        the_secret = os.environ.get("BINANCE_API_SECRET")
        client = Spot(base_url=url, api_key=the_key, api_secret=the_secret)
        
        # Retrieve all data, returns a list with 500 rows of bar data
        data = client.klines(self.symbol, tf)

        # Set the current bar data (unfinished)
        # This is basically a quote since the bar is unfinished
        # The close is the current price 
        bar = data[-1]
        self.date = str(bar[0]) # bar open time in milliseconds
        self.open = float(bar[1])
        self.high = float(bar[2])
        self.low = float(bar[3])
        self.close = float(bar[4])
        self.vol = int(bar[5].split('.')[0])
        self.end = str(bar[6]) # bar close time in milliseconds
        return(data)

    
    def settoDB(self, db_table: str, data: list) -> None:
        # Connect to Postgres SQL database
        conn = pg.connect(**self.db_params)
        cursor = conn.cursor()

        # Query the database to find the highest existing 'id' value
        cursor.execute(f"SELECT MAX(id) FROM {db_table}")
        max_id = cursor.fetchone()[0]  # Get the maximum 'id' value
        
        # Checks the value of max_id and sets max_id value accordingly
        # If max_id is None the database doesn't have any data and will be set to 1
        new_id = 1 if max_id is None else max_id + 1

        # SQL query to insert data
        insert_query = """
            INSERT INTO {0} (id, date, open, high, low, close, vol)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """.format(db_table)

        # Create a new tuple from previous tuple data
        new_data = (new_id, data[0], data[1], data[2], data[3], data[4], data[5])
        try:
            cursor.execute(insert_query, new_data)
            conn.commit()
            print("Data inserted successfully.")
        except Exception as e:
            print(f"Error: {e}")

        cursor.close()
        conn.close()

    
    def pullfromDB(self, db_table: str) -> list:
        try:
            # Connect to the PostgreSQL database
            conn = pg.connect(**self.db_params)
            cursor = conn.cursor()

            # Define the SQL query to retrieve the latest entry
            query = f"SELECT * FROM {db_table}"

            # Run query and fetch all results
            cursor.execute(query)
            all_entries = cursor.fetchall()

            # Commit the transaction and close the connection
            conn.commit()
            cursor.close()
            conn.close()

            return all_entries

        except pg.Error as e:
            print(f"Error: {e}")
            return None


if __name__ == '__main__':
    coin = 'batusdt'
    # Instantiate the PREPDATA class with a stock market ticker to search for
    ticker = PREPDATA(coin)
    
    # Set table to use in Postgres
    db_table = coin

    # Set the results from the search to the class variables
    coin_data = ticker.getData()
    
    # Check the current time in ms
    currtime = str(time.time()*1000)
    
    # Insert results into the database 1 bar at a time as long as it is historical
    # Making sure that the data is a completed bar and not the current unfinished bar
    for bar in coin_data:
       data = (
           str(bar[6]),
           float(bar[1]),
           float(bar[2]),
           float(bar[3]),
           float(bar[4]),
           str(bar[5].split('.')[0])
           )
       if currtime >= str(bar[6]):
           ticker.settoDB(coin, data)

    # Query the database to make sure data was inserted
    # dbz = ticker.pullfromDB(db_table)

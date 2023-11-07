import yfinance as yf
import psycopg2 as pg


class PREPDATA:
    # Initialize variables to be used
    def __init__(self, symbol: str) -> None:
        self.symbol = symbol.upper()
        self.open = 0
        self.high = 0
        self.low = 0
        self.close = 0
        self.vol = 0
        # The connection parameters below should be changed to match your database settings
        self.db_params = {
            'host': 'ENTER_YOUR_POSTGRES_HOST_HERE',
            'database': 'DATABASE_NAME',
            'user': 'DATABASE_USER',
            'password': 'DATABASE_PASSWORD',
            'port': 'DATABASE_PORT',
        }
        # Columns to be dropped from yfinance results
        self.columns = ["Date", "Dividends", "Stock Splits"]
    
    def __str__(self) -> str:
        return("Symbol: {0}, Open: {1}, High: {2}, Low:{3}, Close: {4}, Volume {5}\nParams: {6}".format(
            self.symbol, self.open, self.high, self.low, self.close, self.vol, self.db_params))
    
    def setData(self, tf: int= -1) -> None:
        # Use yfinance to search a ticker
        ticker = yf.Ticker(self.symbol)
        # Retrieve last two days of daily data
        data = ticker.history(period="2d")
        if "Date" in data.index.names:
            data = data.reset_index()
        # Drop unused columns from results
        data.drop(columns=self.columns, inplace=True)
        # Set the most recent daily info
        self.open = float(data["Open"].iloc[tf])
        self.high = float(data["High"].iloc[tf])
        self.low = float(data["Low"].iloc[tf])
        self.close = float(data["Close"].iloc[tf])
        self.vol = int(data["Volume"].iloc[tf])
    
    def settoDB(self, db_table: str) -> None:
        # Connect to Postgres SQL database
        conn = pg.connect(**self.db_params)
        cursor = conn.cursor()

        # Query the database to find the highest existing 'id' value
        cursor.execute(f"SELECT MAX(id) FROM {db_table}")
        max_id = cursor.fetchone()[0]  # Get the maximum 'id' value

        # Checks the value of max_id and sets max_id value accordingly
        # If max_id is None that means the database doesn't have any data and will be set to 1
        new_id = (1, max_id + 1)[max_id is not None]

        insert_query = """
            INSERT INTO {0} (id, open, high, low, close, vol)
            VALUES (%s, %s, %s, %s, %s, %s)
            """.format(db_table)

        # Data to be inserted into database
        data = (new_id, self.open, self.high, self.low, self.close, self.vol)

        try:
            cursor.execute(insert_query, data)
            conn.commit()
            print("Data inserted successfully.")
        except Exception as e:
            print(f"Error: {e}")

        cursor.close()
        conn.close()

    
    def pullfromDB(self, db_table: str):
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
    # Instantiate the PREPDATA class with a stock market ticker to search for
    spy = PREPDATA("SPY")
    
    # Set table to use in Postgres
    db_table = "spydaily"

    # Set the results from the search to the class variables
    spy.setData()
    
    # Check to make sure data was received and set to variables
    print(spy)
    
    # Insert results into the database
    spy.settoDB(db_table)

    # Query the database to make sure data was inserted
    print(spy.pullfromDB(db_table))

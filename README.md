# stock-market
A collection of Python scripts that do things related to the stock market.

[![License: GPL-3.0](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/42u/stock-market.svg)](https://github.com/42U/stock-market)

![Project Image](imgz/stock-market.png)

## Table of Contents
> All files are standalone and may have different dependencies. Each file is listed below and the installation of dependencies are listed within the section for that file.

**click the file you're trying to use for instructions on how to use:**
- [pull_yfinance_insert_postgres.py](#pull_yfinance_insert_postgres)
<!-- 
- [Installation](#installation)
- [Usager](#usager)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)
-->
## pull_yfinance_insert_postgres
#### What does it do?
- This script pulls the most recent day's open, high, low, close data and inserts it into a Postgres database. I use it with a cronjob to add to a time series database that updates everyday after market close.

#### How to use it:
- Basic class structure, uses Yahoo Finance (yfinance) to pull stock market data, and Postgres Python adapter 'psycopg2' library for database interactions.
- Make sure you have the following libraries installed:
```shell
pip install yfinance psycopg2
```
#### Modify
- The script variable for database parameters needs to be modified to work with your Postgres database. Open your favorite text editor and modify the following to your connection settings:
```python
self.db_params = {
            'host': 'ENTER_YOUR_POSTGRES_HOST_HERE',
            'database': 'DATABASE_NAME',
            'user': 'DATABASE_USER',
            'password': 'DATABASE_PASSWORD',
            'port': 'DATABASE_PORT',
        }
```
- By default the script will search for the ticker: SPY
- If you want to search for other tickers then you need to modify the section where 'PREPDATA("SPY")' is called. 

*example for searching 'GM' ticker*
```python
if __name__ == '__main__':
    # Instantiate the PREPDATA class with a stock market ticker to search for
    ticker = PREPDATA("GM")
```
#### Run the script
```shell
python pull_yfinance_insert_postgres.py
```
<!--
## Installation

2. Each Python file may have different dependencies a requirements.txt may be accompanied.
3. Placeholder for dependencies.

```shell
$ pip install psycopg3, yfinance
-->
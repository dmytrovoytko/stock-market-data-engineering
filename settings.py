import os
from dotenv import load_dotenv

# loading environment variables
load_dotenv()

def load_duckdb_settings():
    # using environment variables, including DUCKDB connection settings
    connection = os.environ.get('DUCKDB_CONNECTION', None)
    if connection:
        if DEBUG:
            print('DUCKDB_CONNECTION:', connection)
    else:
        print ('The DUCKDB_CONNECTION environment variable is not defined.\n')
        return None

    return connection

def load_gcp_settings():
    # using environment variables, including Google Cloud credentials
    credentials = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', None)
    if credentials:
        if DEBUG:
            print('GOOGLE_APPLICATION_CREDENTIALS:', credentials)
        if (not os.path.exists(credentials)):
            print (f'The GOOGLE_APPLICATION_CREDENTIALS file {credentials} does not exist.\n')
            return None, None, None
    else:
        print ('The GOOGLE_APPLICATION_CREDENTIALS environment variable is not defined.\n')
        return None, None, None

    project_name = os.environ.get('GCP_PROJECT_NAME', None)
    dataset = os.environ.get('BQ_DATASET', None)
    if DEBUG:
        print(f'GCP Credentials file: {credentials}, GCP_PROJECT_NAME: {project_name}, BQ_DATASET: {dataset}')
    return credentials, project_name, dataset


# show extra information for checking execution
DEBUG = True # False

DATA_DIR = f'./data/'  # ! with '/' at the end!
VISUALS_DIR = './visuals/'

SCRAPE = True # True # False 
START_YEAR = 2020 # 2010
START_DATE = f'{START_YEAR}-01-01'

# define your list like below
tickers_my = [
            "AAPL", "MSFT", "GOOG", "GOOGL", "AMZN", "META", "NFLX", "TSLA", "NVDA", "AMD", "INTC",
            "ADBE", "AVGO", "BRK-B", "CRWD", "CSCO", "DELL", "FDX", "HPE", "HPQ", "IBM", 
            "MU", "MSI", "ORCL", "PLTR", "QCOM", "CRM", "SMCI", "WDC",
            # indexes
            "^SPX", "^SP400", "^SP600", "^NY", "^DJUS", "^NYA", "^XAX", "^IXIC",
            # 
            "VOO", "SPY", 
            # crypto
            "BTC-USD", "ETH-USD", "USDT-USD", 
            ]

tickers_indexes = [ 
            # "^GSPC", ==  "^SPX" 
            "^SPX", "^SP400", "^SP600", "^NY", "^DJUS", "^NYA", "^XAX", "^IXIC",
            "^NDX", "^NDXE", "^NXTQ", "^RUI", "^RUT", "^RUA", 
            "^FTEU1", "^SPEUP", "^N100", "^ISEQ",
            # The ticker for the S&P 500 index is ^GSPC, but it cannot be traded. 
            # SPX and SPY represent options on the S&P 500 index, and they are traded in the market.
            # "VOO", "SWPPX", "IVV", "VFIAX", "SPY", "", 
            ]

tickers_crypto = [
            "BTC-USD", "ETH-USD", "USDT-USD", "XRP-USD", "BNB-USD", "SOL-USD", "USDC-USD", "LTC-USD",
            ]

ticker_sets = {
    # "all": [], # to extract all S&P500 tickers
    "magnificent": ["AAPL", "MSFT", "GOOG", "AMZN", "META", "NVDA", "TSLA",],
    # "crypto": tickers_crypto,
    # "indexes": tickers_indexes,
    "set1": tickers_my,
} 
SELECTED_TICKERS = ticker_sets["magnificent"]                    
SELECTED_TICKERS = ticker_sets["set1"]                    


SAMPLE = 'sample' # export samples to .csv 
PARQUET = 'parquet' # export to .parquet files
DUCKDB = 'duckdb' # export to DuckDB
BIGQUERY = 'bigquery' # export to BigQuery

MODE = os.environ.get('DATAWAREHOUSE', BIGQUERY) # DUCKDB BIGQUERY SAMPLE
CHUNKSIZE = 100_000 # 100_000
SAMPLE_SIZE = 1000


if MODE==DUCKDB:
    DUCKDB_CONNECTION = load_duckdb_settings()
else:
    DUCKDB_CONNECTION = None

if MODE==BIGQUERY:
    GCP_CREDENTIALS, GCP_PROJECT_NAME, BQ_DATASET = load_gcp_settings()
else:    
    GCP_CREDENTIALS, GCP_PROJECT_NAME, BQ_DATASET = None, None, None
import os
from glob import glob
from time import time

import pandas as pd

try:
    from google.cloud import bigquery
    from google.api_core import exceptions
    from google.cloud.bigquery.table import TableConstraints, PrimaryKey
    from google.cloud import storage
except:
    print("! import google.cloud failed")

    class bigquery:
        pass

    pass

from settings import DATA_DIR, DEBUG
from settings import START_YEAR, START_DATE
from settings import GCP_CREDENTIALS, GCP_PROJECT_NAME, BQ_DATASET


def biqquery_get_ticker_records(bq_client, table_name, ticker, start_date=START_DATE, end_date=None):
    # , momentum, volatility
    query = f"SELECT format_timestamp('%Y-%m-%d', date) as date, open, high, low, close, volume, \
                ma_7, ma_10, ma_20, ma_30, ma_100, macd, rsi FROM {BQ_DATASET}.{table_name} \
                WHERE ticker='{ticker}' \
                    AND CAST(date as string format 'YYYY-MM-DD') >= '{start_date}' \
                ORDER BY date ASC;"
    df = bq_client.query_and_wait(query).to_dataframe()
    if DEBUG:
        print("---")
        print(df.head())
        print(df.dtypes)
        print(" Total records:", df.shape[0])
        # df1 = df.copy()
        df["date"] = pd.to_datetime(df["date"], errors="coerce")  # .dt.strftime('%Y-%m-%d')
        # print(df1.head())
    return df


def get_schema(table_name):
    if table_name == "tickers_info":
        # ticker,company,sector,gics_sub-industry,headquarters_location,date_added,cik,founded,state
        schema = [
            bigquery.SchemaField("ticker", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("company", "STRING"),
            bigquery.SchemaField("sector", "STRING"),
            bigquery.SchemaField("location", "STRING"),
            bigquery.SchemaField("founded_year", "INTEGER"),
            bigquery.SchemaField("date_added", "STRING"),
        ]
    elif table_name == "tickers_prices":
        # date,ticker,open,high,low,close,volume
        schema = [
            bigquery.SchemaField("date", "DATE", mode="REQUIRED"),
            bigquery.SchemaField("ticker", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("open", "FLOAT"),
            bigquery.SchemaField("high", "FLOAT"),
            bigquery.SchemaField("low", "FLOAT"),
            bigquery.SchemaField("close", "FLOAT"),
            bigquery.SchemaField("volume", "FLOAT"),
        ]
    elif table_name == "tickers_data":
        # date,ticker,open,high,low,close,volume + indicators + sector
        schema = [
            bigquery.SchemaField("date", "DATE"),
            bigquery.SchemaField("ticker", "STRING"),
            bigquery.SchemaField('open', 'FLOAT'),
            bigquery.SchemaField('high', 'FLOAT'),
            bigquery.SchemaField('low', 'FLOAT'),
            bigquery.SchemaField("close", "FLOAT"),
            bigquery.SchemaField('volume', 'FLOAT'),
            # ma_10,ma_20,ema_20,momentum,volatility,next_day_return
            bigquery.SchemaField("ma_7", "FLOAT"),
            bigquery.SchemaField("ma_10", "FLOAT"),
            bigquery.SchemaField("ma_20", "FLOAT"),
            bigquery.SchemaField("ma_30", "FLOAT"),
            bigquery.SchemaField("ma_100", "FLOAT"),
            # bigquery.SchemaField("ema_20", "FLOAT"),
            bigquery.SchemaField("macd", "FLOAT"),
            bigquery.SchemaField("rsi", "FLOAT"),
            # bigquery.SchemaField("momentum", "FLOAT"),
            # bigquery.SchemaField("volatility", "FLOAT"),
            # bigquery.SchemaField("next_day_return", "FLOAT"),
            bigquery.SchemaField("sector", "STRING"),
        ]
    else:
        schema = [
            # bigquery.SchemaField('partition_date', 'DATE')
            # bigquery.SchemaField('verified_purchase', 'BOOLEAN'),
            # bigquery.SchemaField('review_date', 'TIMESTAMP'),
        ]
    return schema


def bigquery_create_table(bq_client, table_name, table_ref, partitioning={}, clastering=[], primary_key={}):
    schema = get_schema(table_name)
    table = bigquery.Table(table_ref, schema=schema)
    if primary_key:
        table.table_constraints = TableConstraints(primary_key=primary_key, foreign_keys=[])

    if partitioning:
        table.time_partitioning = bigquery.TimePartitioning(
            type_=partitioning["type"],
            field=partitioning["field"],
            expiration_ms=partitioning["expiration_ms"],
        )
    if clastering:
        table.clustering_fields = clastering
    table = bq_client.create_table(table)
    return table


def bigquery_connect():
    # loading environment variables, including Google Cloud credentials

    if not GCP_CREDENTIALS:
        print(f"No GCP credentails found, BigQuery connection failed.\n")
        return None, None
    elif not (GCP_PROJECT_NAME and BQ_DATASET):
        print("BigQuery Dataset parameters not found, connection failed.\n")
        return None, None

    # bq_table = table_name
    # bucket_name = os.environ['GCS_BUCKET']
    # storage_client = storage.Client()

    if DEBUG:
        print(f"\nBigQuery connection: {GCP_PROJECT_NAME}.{BQ_DATASET}")  # .{bq_table}

    try:
        bq_client = bigquery.Client(project=GCP_PROJECT_NAME)
    except Exception as e:
        print(f"Error connecting to BigQuery project {GCP_PROJECT_NAME}.\n{e}")
        return None, None

    # Setup the BigQuery dataset object
    try:
        dataset_ref = bq_client.dataset(BQ_DATASET)
        dataset = bigquery.Dataset(dataset_ref)
        bq_client.get_dataset(dataset_ref)
        if DEBUG:
            print(f" Found dataset {BQ_DATASET}")
    except exceptions.NotFound:
        # no such dataset found - creating it
        try:
            dataset_ref = bq_client.dataset(BQ_DATASET)
            dataset = bq_client.create_dataset(bigquery.Dataset(dataset_ref))
            if DEBUG:
                print(f" Created dataset {dataset.project}.{dataset.dataset_id}")
        except Exception as e:
            print(f"Error creating BigQuery dataset {BQ_DATASET}.\n{e}")
            return None, None

    return bq_client, dataset


def bigquery_get_table(bq_client, dataset, table_name):
    bq_schema = get_schema(table_name)
    try:
        table_ref = dataset.table(table_name)
        table = bq_client.get_table(table_ref)
        if DEBUG:
            print(f" Connected to table {table.project}.{table.dataset_id}.{table.table_id}")
    except:
        # no such table found - creating it
        table_ref = dataset.table(table_name)

        # ALTER TABLE [[project_name.]dataset_name.]table_name
        # ADD PRIMARY KEY(column_list) NOT ENFORCED;
        # Partition by DAY? by Year/Month?  ticker?

        if table_name == "tickers_info":
            primary_key = PrimaryKey(["ticker"])
            partitioning = {}
            clastering = []
        elif table_name == "tickers_prices":
            # primary_key = PrimaryKey(["date", "ticker"])
            primary_key = None
            # partitioning = {
            #     'type': bigquery.TimePartitioningType.MONTH, # YEAR, # MONTH, # DAY,
            #     'field': "date",  # name of column to use for partitioning
            #     'expiration_ms': 1000 * 60 * 60 * 24 * 60*1, # 365days = 1 year  # 60, # 60 days - older records get removed
            # }
            partitioning = {}
            clastering = ["ticker"]
        elif table_name == "tickers_data":
            # primary_key = PrimaryKey(["date", "ticker"])
            primary_key = None
            # partitioning = {
            #     'type': bigquery.TimePartitioningType.MONTH, # YEAR, # MONTH, # DAY,
            #     'field': "date",  # name of column to use for partitioning
            #     'expiration_ms': 1000 * 60 * 60 * 24 * 60*1, # 365days = 1 year  # 60, # 60 days - older records get removed
            # }
            partitioning = {}
            clastering = ["ticker", "sector"]
        else:
            primary_key = None
            partitioning = {}
            clastering = []

        table = bigquery_create_table(bq_client, table_name, table_ref, partitioning, clastering, primary_key)
        if DEBUG:
            print(f" Created table {table.project}.{table.dataset_id}.{table.table_id}")
            if primary_key:
                print(f"  primary key: {primary_key}")
            if partitioning:
                print(f"  partitioning: {partitioning}")
            if clastering:
                print(f"  clastering: {clastering}")

    return table_ref, bq_schema


def load_data_to_bigquery_table(bq_client, table_ref, file_list, schema, description, file_type="csv"):
    t_start0 = time()
    print(f"\nLoading {description} data to {table_ref}...")
    # print(f' Schema: {schema}\n')
    if file_type == "csv":
        source_format = bigquery.SourceFormat.CSV
    elif file_type == "parquet":
        source_format = bigquery.SourceFormat.PARQUET
    else:
        print("!! Unexpected file type {file_type}. Loading aborted.")
        return 1

    job_config_overwrite = bigquery.LoadJobConfig(
        autodetect=True,
        source_format=source_format,
        schema=schema,
        write_disposition="WRITE_TRUNCATE",
        ignore_unknown_values=True,
    )

    job_config_append = bigquery.LoadJobConfig(
        autodetect=True,
        source_format=source_format,
        schema=schema,
        write_disposition="WRITE_APPEND",
        ignore_unknown_values=True,
    )

    t_start = time()
    i = 0
    for file_name in file_list:
        # file type checks
        if file_type == "parquet" and not file_name.endswith("parquet"):
            if DEBUG:
                print(f" File {file_name} is not parquet, skipped.")
            continue
        if file_type == "csv" and not file_name.endswith("csv"):
            if DEBUG:
                print(f" File {file_name} is not CSV, skipped.")
            continue
        # processing
        with open(file_name, "rb") as source_file:
            # # debug types
            # df = pd.read_parquet(file_name, engine='pyarrow')
            # print(f'From parquet columns: {df.columns.tolist()}\n{df.dtypes.to_string()}\n')
            # print(f'{df.head(5).to_string()}\n')

            # we overwrite when loading first file, and append the next files
            job_config = job_config_overwrite if i == 0 else job_config_append
            try:
                job = bq_client.load_table_from_file(source_file, table_ref, job_config=job_config)
                i += 1
                result = job.result()

                # Get the number of rows loaded
                rows_loaded = result.output_rows
                print(f" + {rows_loaded} rows ({i}) loaded to BigQuery ({file_name}), took {(time() - t_start):.3f} second(s)")
                t_start = time()
            except Exception as e:
                print(f"! Error while loading {file_name} to BigQuery {table_ref}.\n{e}")
                return 1
    print(f"\nData loading {description} completed successfully in {(time() - t_start0):.3f} second(s)")
    return 0


def bigquery_load_data(table_name, file_list, description, file_type="csv"):
    print(f"\nLoading: {description} {table_name} {file_list}")
    bq_client, dataset = bigquery_connect()
    if not bq_client:
        return 1

    table_ref, schema = bigquery_get_table(bq_client, dataset, table_name)

    load_data_to_bigquery_table(bq_client, table_ref, file_list, schema, description, file_type)

    t_start = time()
    table = bq_client.get_table(table_ref)
    # print(f'Table description: {table.description}')
    # print(f'Table schema: {table.schema}')
    print(f"Table has {table.num_rows} rows. Request took {(time() - t_start):.3f} second(s)")

    return 0


def bigquery_transform_data(table_name, year=START_YEAR, description=""):
    print(f"\nTransforming: {description} [{table_name}]")
    bq_client, dataset = bigquery_connect()
    if not bq_client:
        return 1

    # creates partitioned, clustered table if not exist
    table_ref, schema = bigquery_get_table(bq_client, dataset, table_name)

    t_start = time()

    table = bq_client.get_table(table_ref)
    # print(f'Table description: {table.description}')
    # print(f'Table schema: {table.schema}')
    print(f"Table has {table.num_rows} rows...")

    # PARTITION BY date
    query = f"""
        CREATE OR REPLACE TABLE {BQ_DATASET}.{table_name}
        (
          date DATE,
          ticker STRING,
          open FLOAT64,
          high FLOAT64,
          low FLOAT64,
          close FLOAT64,
          volume FLOAT64,
          ma_7 FLOAT64,
          ma_10 FLOAT64,
          ma_20 FLOAT64,
          ma_30 FLOAT64,
          ma_100 FLOAT64,
          macd FLOAT64,
          rsi FLOAT64,
          sector STRING
        )
        CLUSTER BY ticker, sector  
         AS 
          (

        WITH prices AS (
          SELECT 
            date, ticker, open, high, low, close, volume,
            AVG(close) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS ma_7,
            AVG(close) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN 9 PRECEDING AND CURRENT ROW) AS ma_10,
            AVG(close) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) AS ma_20,
            AVG(close) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) AS ma_30,
            AVG(close) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN 99 PRECEDING AND CURRENT ROW) AS ma_100,
            SUM(CASE WHEN close > open THEN close - open ELSE 0 END) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN 23 PRECEDING AND CURRENT ROW) AS gain,
            SUM(CASE WHEN open > close THEN open - close ELSE NULL END) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN 23 PRECEDING AND CURRENT ROW) AS loss,
            MAX(high) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN 23 PRECEDING AND CURRENT ROW) AS highest,
            MIN(low) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN 23 PRECEDING AND CURRENT ROW) AS lowest,
            (AVG(close) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN 11 PRECEDING AND CURRENT ROW) - AVG(close) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN 23 PRECEDING AND CURRENT ROW)) AS macd
          FROM {BQ_DATASET}.tickers_prices
        )
          SELECT 
            date, prices.ticker, open, high, low, close, volume,
            ma_7, ma_10, ma_20, ma_30, ma_100, macd, 
            (100 - (100 / (1 + (gain / loss)))) AS rsi,
            info.sector as sector
          FROM prices
          LEFT JOIN {BQ_DATASET}.tickers_info AS info
                    ON prices.ticker = info.ticker

          )
        ;
    """
    # EXTRACT(YEAR FROM prices.date) as year,
    rows = bq_client.query_and_wait(query)
    print("Create/replace " + table_name, rows)

    # quick statistics to check data
    # table_name = 'tickers_prices'
    query = f"""
        SELECT EXTRACT(YEAR FROM date) as year, AVG(close) as avg_price, count(*) as count
          FROM {BQ_DATASET}.{table_name} as prices 
          WHERE EXTRACT(YEAR FROM date)>={year}
          GROUP BY year
          ORDER BY year
    """
    rows = bq_client.query_and_wait(query)

    print(f"\nThe query data {table_name}:")
    for row in rows:
        # Row values can be accessed by field name or index.
        print(
            row["year"],
            row["avg_price"],
            row["count"],
        )


    print(f"Transforming finished in {(time() - t_start):.3f} second(s)")

    return 0


if __name__ == "__main__":
    if not (GCP_CREDENTIALS and GCP_PROJECT_NAME and BQ_DATASET):
        print(f"!! Check GCP credentails and BigQuery settings. Connection failed.\n")
        exit(1)

    bq_client, dataset = bigquery_connect()
    # table_ref = bigquery_get_table(bq_client, dataset, table_name='tickers_data')
    # print(bq_client, table_ref)
    df = biqquery_get_ticker_records(bq_client, table_name="tickers_prices", ticker="AAPL", start_date="2025-03-21")

    exit()
    bigquery_transform_data(bq_client, dataset, table_name="tickers_data", year=START_YEAR, description="Enriching data")

    path = DATA_DIR
    # mask = 'tickers_data*.csv' # .parquet
    table_name = "tickers_prices"  # 'tickers_info' # 'tickers_prices'
    # mask = 'tickers_info*.csv'
    mask = f"{table_name}*.csv"
    file_type = "csv"
    try:
        # file_list = [ sorted(glob(f'{path}/{mask}')) [0] ] # only 1st for testing
        file_list = sorted(glob(f"{path}/{mask}"))  # all found
    except:
        print(f"No {path}/{mask} files found.")
        exit(1)
    description = f"Testing export {mask}"
    # Load files to BigQuery
    result = bigquery_load_data(table_name, file_list, description, file_type=file_type)
    exit(result)

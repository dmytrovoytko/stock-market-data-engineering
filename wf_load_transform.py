import pandas as pd

from datetime import date, datetime, timedelta
from time import sleep, strftime, time

from settings import DATA_DIR, START_DATE, DEBUG
from settings import MODE, SAMPLE, PARQUET, DUCKDB, BIGQUERY, CHUNKSIZE, SAMPLE_SIZE
from settings import SELECTED_TICKERS, ticker_sets

from load_duckdb import duckdb_load_data, duckdb_transform_data
from load_bigquery import bigquery_load_data, bigquery_transform_data

# Pandas settings: Display all df columns
pd.set_option("display.width", 200)
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.max_colwidth", 40)


def split_dataframe(df, chunk_size=CHUNKSIZE):
    chunks = list()
    num_chunks = len(df) // chunk_size + 1
    for i in range(num_chunks):
        chunks.append(df[i * chunk_size : (i + 1) * chunk_size])
    return chunks


def load_data(df_tickers_info, df_tickers, mode=SAMPLE, selected_tickers=SELECTED_TICKERS):
    print(f"\nLoad data: Mode {mode}")

    table_name = "tickers_prices"
    export_filename = DATA_DIR + table_name
    t_start = time()
    print(f'\n[{strftime("%H:%M:%S")}] Loading data: mode {mode}')

    res = 1

    if len(selected_tickers) == 0:
        # on empty list use all S&P500 tickers
        selected_tickers = df_tickers_info["ticker"].to_list()

    i = 0
    export_list = []
    chunks = split_dataframe(df_tickers)
    for chunk in chunks:
        i += 1
        df = chunk

        if i == 1 and mode == SAMPLE:
            # export sample 1: after final transformation
            df.head(SAMPLE_SIZE).to_csv(export_filename + "_1.csv", encoding="utf-8", index=False)
            # no full export - exiting
            print(f"Finished exporting {export_filename} -> samples. Total time {(time() - t_start):.3f} second(s)\n+++\n")
            # return 0
            break

        if mode == DUCKDB:
            duckdb_load_data(df, table_name, export_filename)
            print(f"... {export_filename}-{i:02d} -> DuckDB, {df.shape[0]} record(s), took {(time() - t_start):.3f} second(s)")
            t_start = time()
            continue
        elif mode in [BIGQUERY]:  # , BIGQUERY PARQUET
            # load_data_to_parquet(df, f'{export_filename}-{i:02d}.parquet', export_list)
            current_filename = f"{export_filename}-{i:02d}.csv"
            df.to_csv(current_filename, encoding="utf-8", index=False)
            print(f"... {current_filename}, {df.shape[0]} record(s), took {(time() - t_start):.3f} second(s)")
            export_list.append(current_filename)
            t_start = time()
            continue
        elif mode in [PARQUET]:
            # load_data_to_parquet(df, f'{export_filename}-{i:02d}.parquet', export_list)
            print(f"... {export_filename}-{i:02d}.csv, {df.shape[0]} record(s), took {(time() - t_start):.3f} second(s)")
            t_start = time()
            continue

    if mode == DUCKDB:
        table_name = "tickers_info"
        export_filename = DATA_DIR + table_name
        res = duckdb_load_data(df_tickers_info, table_name, export_filename)
        print(f"... {export_filename}-{i:02d} -> DuckDB, {df.shape[0]} record(s), took {(time() - t_start):.3f} second(s)")
        t_start = time()
    elif mode == BIGQUERY:
        table_name = "tickers_info"
        export_filename = DATA_DIR + f"{table_name}.csv"
        df_tickers_info.to_csv(export_filename, encoding="utf-8", index=False)
        bigquery_load_data(table_name, [export_filename], table_name, file_type="csv")
        print(f"... {export_filename}-{i:02d} -> BigQuery, {df.shape[0]} record(s), took {(time() - t_start):.3f} second(s)")

        table_name = "tickers_prices"
        # print(table_name, export_list)
        res = bigquery_load_data(table_name, export_list, table_name, file_type="csv")

    return res


def transform_data(mode=SAMPLE):
    print(f"\nTransform data: Mode {mode}")
    if mode == DUCKDB:
        # 
        duckdb_transform_data(table_name="tickers_data", description="Enriching data")
    elif mode == BIGQUERY:
        bigquery_transform_data(table_name="tickers_data", description="Enriching data")


if __name__ == "__main__":
    selected_tickers = ticker_sets["set1"]

    from wf_extract import extract_data

    mode = MODE

    # df_tickers_info, df_tickers = extract_data(mode, selected_tickers=selected_tickers, scrape=True)
    df_tickers_info, df_tickers = extract_data(mode=SAMPLE, selected_tickers=selected_tickers, scrape=False)  # True

    res = load_data(df_tickers_info, df_tickers, mode, selected_tickers=SELECTED_TICKERS)

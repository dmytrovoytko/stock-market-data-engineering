import warnings

# warnings.simplefilter("ignore", category=UserWarning)
warnings.filterwarnings("ignore")

import os
import argparse
from time import time

from prefect import flow, task # TEMP uncomment

from settings import DATA_DIR, START_DATE, SELECTED_TICKERS, DEBUG
from settings import MODE, SAMPLE, PARQUET, DUCKDB, BIGQUERY, CHUNKSIZE, SAMPLE_SIZE

from settings import DEBUG  # isort:skip

DEBUG = True  # True # False # override global settings


from wf_extract import extract_data
from wf_load_transform import load_data, transform_data

###########################


@task(retries=3)
def extract(mode=MODE, selected_tickers=SELECTED_TICKERS):
    print(f"\nExtracting data: {mode}")
    df_tickers_info, df_tickers = extract_data(mode, selected_tickers)
    return df_tickers_info, df_tickers


@task(retries=3)
def load(df_tickers_info, df_tickers, mode=MODE):
    print(f"\nLoading data: {mode}")
    res = load_data(df_tickers_info, df_tickers, mode, selected_tickers=SELECTED_TICKERS)
    return res


@task(retries=3)
def transform(mode=MODE):
    print(f"\nTransforming data: {mode}")
    res = transform_data(mode)
    return res


###########################


@flow(log_prints=True)
def de_workflow(params):
    # data engineering workflow

    mode = params.mode

    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    # Stage: EXTRACT
    # input:
    #  - selected_tickers,
    #  - (?date=current)
    #    if DW already exist we can get last loaded date and backfill only since then
    #  - mode
    df_tickers_info, df_tickers = extract(mode, selected_tickers=SELECTED_TICKERS)
    if mode == SAMPLE:
        # done - no load/transform
        return 0

    # Stage: LOAD
    # input:
    #  - mode
    #  TODO - backfill or full load
    columns = ["date","ticker","open","high","low","close","volume"]
    res = load(df_tickers_info, df_tickers[columns], mode)

    # Stage: TRANSFORM
    # input:
    #  - mode
    if res == 0:
        transform(mode)
        return 0
    else:
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process (ELT) data into BigQuery/DuckDb or export sample CSV")

    parser.add_argument("--mode", required=False, type=str, default=MODE, help=f"{SAMPLE}/{PARQUET} or {DUCKDB}, {BIGQUERY} as default")
    # parser.add_argument('--reset', required=False, type=str, default='False', help='True to reset table before loading, False as default')

    args = parser.parse_args()

    # execute Data Engineering Workflow
    res = de_workflow(args)

    exit(res)

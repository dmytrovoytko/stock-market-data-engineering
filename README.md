# Data Engineering project Stock/Crypto Analitics

Data Engineering project for ZoomCamp`25: Stock prices -> BigQuery/DuckDB + TradingView charts in Streamlit

ELT for 💹 [Yahoo Finance](https://finance.yahoo.com/markets/)

![Data Engineering Stock/Crypto Analitics](/screenshots/stock-analytics-data-engineering.png)
Project can be tested and deployed in **GitHub CodeSpaces** (the easiest option, and free), cloud virtual machine (AWS, Azure, GCP), or just locally.
For the GitHub CodeSpace option you don't need to use anything extra at all - just your favorite web browser + GitHub account is totally enough.

## Problem statement

If you decide to start investing in stocks/crypto, how do you choose companies/currencies?
Which of them are good/bad to invest just right now, and which are good to buy and hold for the long term?

Legendary King of Stocks Buffett continues to prioritize finding and buying quality stocks at a fair price — and holding them for the long term. He patiently builds those positions over time.

Even beginners know about The Magnificent 7 stocks - seven of the world's biggest and most influential tech companies: Apple, Microsoft, Amazon, Alphabet (Google)... Should you invest in particular companies (like Magnificent 7) or investing in S&P 500 index funds would be a better/safer choice for you?

Are recent storms in economy signal to stay away from investing, or it was in history many times, or even open new opportunities?

I think the better understanding we can only get by "playing" with data the way we want, not as investors channels present us. So let's Data Engineering help us with that!

I decided to collect historical data of S&P 500 companies, enrich it, put it into warehouse like BigQuery and experiment with data analytics via Google Looker Studio (then I found something great specifically for trading data). 
Let's see how well we can deal with that!

## 🎯 Goals

This is my Data Engineering project in [DE ZoomCamp](https://github.com/DataTalksClub/data-engineering-zoomcamp)'2025.

**The main goal** is straight-forward: build an end-to-end **Extract - Load - Transform** data pipeline, then **visualize** some insights.  
- choose an interesting dataset
- process (extract, load, transform) data
- deploy orchestration tool to manage pipeline
- build a dashboard to visualize the data


## :toolbox: Tech stack

- Python 3.11/3.12
- Docker and docker-compose for containerization
- Teraaform for infrastructure
- Prefect for workflow orchestration
- BigQuery or/and DuckDB (MotherDuck) for data warehouse
- [optional] Google Cloud Storage
- Pandas and Matplotlib for basic exploratory data analysis
- Plotly and streamlit lightweight charts for data visualization
- Streamlit for dashboard

## 🚀 Instructions to reproduce

- [Setup environment](#hammer_and_wrench-setup-environment)
- [Run workflow](#arrow_forward-run-workflow)
- [Dashboard](#mag_right-dashboard)

### :hammer_and_wrench: Setup environment

1. **Fork this repo on GitHub**. Or use `git clone https://github.com/dmytrovoytko/stock-market-data-engineering.git` command to clone it locally, then `cd stock-market-data-engineering`.
2. Create GitHub CodeSpace from the repo.
3. **Start CodeSpace**
4. The app works in docker container, **you don't need to install packages locally to test it**.
5. Only if you want to develop the project locally, you can run `pip install -r requirements.txt` (project tested on python 3.11/3.12).
6. You need to copy `example.env` to `.env` and edit setting according to your environment. Run `cp example.env .env` then edit `.env` file.
7. If you want and can use BigQuery you need to save GCP credentials to the file `gcp-credentials.json` (recommended) and then set GOOGLE_APPLICATION_CREDENTIALS in `.env` file. Then edit GCP_PROJECT_NAME, BQ_DATASET, GCS_BUCKET (optional). You also need to set proper access for the service account to access BigQuery.
8. If you want to use Terraform, set `USE_TERRAFORM=true` in `.env` file.
9. If you don't want to use BigQuery the default settings will activate alternative - DuckDb database (you can also create/use free! MotherDuck account to use cloud data warehouse).

### :arrow_forward: Run workflow

1. **Run `bash deploy.sh` to start app container**. As packages include some quite heavy packages like Prefect, building container takes some time (~3min). When new log messages will stop appearing, you can press enter to return to a command line (service will keep running in background).

![docker-compose up](/screenshots/docker-compose-00.png)

When you see these messages the app is ready!

![docker-compose up](/screenshots/docker-compose-01.png)

You can scroll up to see previous messages with the steps of the workflow.

2. Terraform setup and deployment starts automatically if you set to use it.

![Terraform](/screenshots/terraform-01.png)

3. Prefect Workflow starts automatically

![Prefect](/screenshots/workflow-01.png)

Including extracting prices

![Extraction](/screenshots/workflow-02.png)

... then loading and transformation

![Extraction](/screenshots/workflow-03.png)


### Dashboard

If you run container locally you can click the link `Local URL: http://localhost:8501` to open the app dashboard.

If you run container in CodeSpace it will pop-up the notification that `Your application running on port 8501 is available.` - click `Open in Browser`. 

💡 In case you accidentally close that pop-up or dashboard page and you need it again, you can always open that page from `Ports` tab:

![Streamlit app ports](/screenshots/streamlit-app-ports.png)
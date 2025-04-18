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
7. If you want and can use BigQuery you need to save GCP credentials to the file `gcp-credentials.json` (recommended) and then set GOOGLE_APPLICATION_CREDENTIALS in `.env` file. Then edit GCP_PROJECT_NAME, BQ_DATASET, GCS_BUCKET (optional). You also need to set proper access for the service account to access BigQuery (see the next part of description). 
8. If you want to use Terraform, set `USE_TERRAFORM=true` in `.env` file.
9. If you don't want to use BigQuery the default settings will activate alternative - DuckDb database (you can also create/use free! MotherDuck account to use cloud data warehouse).


### Generate BigQuery credentials

In order to let the workflow and dashboard connect to your BigQuery warehouse, you'll need to generate a keyfile. This is analogous to using a database username and password with most other data warehouses.

1. Start the [GCP credentials wizard](https://console.cloud.google.com/apis/credentials/wizard). Make sure your new project is selected in the header. If you do not see your account or project, click your profile picture to the right and verify you are using the correct email account. For **Credential Type**:
- From the **Select an API** dropdown, choose **BigQuery API**
- Select **Application data** for the type of data you will be accessing
- Click **Next** to create a new service account.
    
2. Create a service account for your new project from the [Service accounts page](https://console.cloud.google.com/projectselector2/iam-admin/serviceaccounts?supportedpurview=project). For more information, refer to [Create a service account](https://developers.google.com/workspace/guides/create-credentials#create_a_service_account) in the Google Cloud docs. As an example for this guide, you can:
- Type `bq-user` as the Service account name
- From the **Select a role** dropdown, choose `BigQuery Job User` and `BigQuery Data Editor` roles and click **Continue**
- Leave the **Grant users access to this service account** fields blank
- Click **Done**

3. Create a service account key for your new project from the [Service accounts page](https://console.cloud.google.com/iam-admin/serviceaccounts?walkthrough_id=iam--create-service-account-keys&start_index=1#step_index=1). For more information, refer to [Create a service account key](https://cloud.google.com/iam/docs/creating-managing-service-account-keys#creating) in the Google Cloud docs. When downloading the JSON file, make sure to use a filename you can easily remember. For example, gcp-credentials.json. For security reasons, it is recommended that you protect this JSON file like you would your identity credentials; for example, don't add the JSON file into your version control software or share screenshots.

4. I recommend to save it to `gcp` folder inside this project, so you follow `example.env` structure.


### :arrow_forward: Run workflow

1. **Run `bash deploy.sh` to start app container**. As packages include some quite heavy packages like Prefect, building container takes some time (~3min). When new log messages will stop appearing, you can press enter to return to a command line (service will keep running in background).

![docker-compose up](/screenshots/docker-compose-00.png)

When you see these messages the app is ready!

![docker-compose up](/screenshots/docker-compose-01.png)

You can scroll up to see previous messages with the steps of the workflow.

2. Terraform setup and deployment starts automatically if you set to use it:

![Terraform](/screenshots/terraform-01.png)

3. Prefect Workflow starts automatically:

![Prefect](/screenshots/workflow-01.png)

It includes extracting prices...

![Extraction](/screenshots/workflow-02.png)

... then loading and transformation:

![Extraction](/screenshots/workflow-03.png)

4. Workflow commands are located in `start_app.sh` 
- it starts `terraform-setup.sh` script
- then `python wf_orchestrate.py` with Prefect orchestrator
- finally executes `streamlit run dashboard-app.py` to start dashboard app

5. `wf_orchestrate.py` has 3 key tasks (extract, load, transform) that call code from `wf_extract.py` and `wf_load_transform.py`

6. Dashboard app is based on Streamlit and located in `dashboard-app.py`


### 📊📈 Dashboard

If you run docker container locally you can click the link `Local URL: http://localhost:8501` to open the app dashboard.

If you run container in CodeSpace it will pop-up the notification that `Your application running on port 8501 is available.` - click `Open in Browser`. 

![Streamlit app popup](/screenshots/app-open-popup.png)

💡 In case you accidentally close that pop-up or dashboard page and you need it again, you can always open that page from `Ports` tab (click that little 'globe' icon over a link):

![Streamlit app ports](/screenshots/streamlit-app-ports.png)

When you open the app it shows the dialog, where you can choose a parameter (open/low/high/close price, volume, different moving averages, MACD, RSI) and a pair of tickers to compare:

![Streamlit app ports](/screenshots/dashboard-01.png)

Simple comparison looks like this (done with Plotly, you can left click and slide to look at a segment closer):

![Streamlit app ports](/screenshots/dashboard-02.png)

And also you can see charts more specific for stock market (scroll mouse wheel over it to zoom in/out):

![Streamlit app ports](/screenshots/dashboard-03.png)


### 🏬 BigQuery tables

Currently ELT creates 3 tables:
- tickers_info with information about S&P500 companies (scraped from Wikipedia) including ticker symbols and company sectors
- tickers_prices with open, low, high, close, volume for tickers by days, collected via yfinance package from Yahoo Finance
- tickers_data with enriched stocks data like calculated tecnical indicators (MA, MACD, RSI) and Sectors

In BigQuery tables can be partitioned and clastered to significantly improve performance and reduce costs (which depends on transferred data volume).

In this case tickers_prices and tickers_data tables can be partitioned by date, and clustered by ticker (tickers_prices)... 

![BigQuery tables](/screenshots/tickers_prices-partitioned.png)

... or ticker and sector (tickers_data)

![BigQuery tables](/screenshots/tickers_data.png)

Information about Sector opens interesting analytics like this:

![visuals](/visuals/avg_price_distribution_by_sector-5.png)


### :stop_sign: Stop all containers

Run `docker compose down` in command line to stop the running conteiner.

Don't forget to remove downloaded images if you experimented with project locally! Use `docker images` to list all images and then `docker image rm ...` to remove those you don't need anymore.

And of course don't forget to destroy resources in Google Cloud/BigQuery!


## 🔜 Next steps

Stock/Crypto Analitics is a very interesting topic, especially now when market volatility is so high!

I plan to analyze more tecnical indicators and use BigQuery ML capabilities to play with predictions, I think it would be interesting!

Stay tuned!


## Support

🙏 Thank you for your attention and time!

- If you experience any issue while following this instruction (or something left unclear), please add it to [Issues](/issues), I'll be glad to help/fix. And your feedback, questions & suggestions are welcome as well!
- Feel free to fork and submit pull requests.

If you find this project helpful, please ⭐️star⭐️ my repo 
https://github.com/dmytrovoytko/stock-market-data-engineering to help other people discover it 🙏

Made with ❤️ in Ukraine 🇺🇦 Dmytro Voytko
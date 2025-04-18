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

I decided to collect historical data of S&P 500 companies, enrich it, put it into warehouse like BigQuery and experiment with data analytics via Google Looker Studio. 
Let's see how well we can deal with that!

## 🎯 Goals

This is my Data Engineering project in [DE ZoomCamp](https://github.com/DataTalksClub/data-engineering-zoomcamp)'2025.

**The main goal** is straight-forward: build an end-to-end **Extract - Load - Transform** data pipeline, then **visualize** some insights.  
- choose an interesting dataset
- process (extract, load, transform) data
- deploy orchestration tool to manage pipeline
- build a dashboard to visualize the data


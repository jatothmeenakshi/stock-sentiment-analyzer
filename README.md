# 📈 Stock News Sentiment Analyzer

## About
A real-time NLP web application that fetches live news
headlines for any company and predicts market sentiment
as Bullish, Bearish or Neutral.

## Features
- Live news fetching using NewsAPI (50+ articles per query)
- NLP sentiment analysis using TextBlob
- Interactive Streamlit dashboard with Plotly charts
- Analyzes any company in real time
- Sentiment trend over time visualization

## Results
- Tested on Tesla, Apple, Infosys, Reliance
- Apple showed most positive market sentiment

## Tech Stack
Python, TextBlob, NewsAPI, Streamlit, Plotly, Pandas

## How to Run
pip install streamlit newsapi-python textblob plotly pandas
streamlit run app.py

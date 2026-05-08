import streamlit as st
import pandas as pd
from textblob import TextBlob
from newsapi import NewsApiClient
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Stock Sentiment Analyzer",
    page_icon="📈",
    layout="wide"
)

# Your API key
API_KEY = "71810680fc7945ffaaf7cd914d42525e"
newsapi = NewsApiClient(api_key=API_KEY)

# Functions
def fetch_news(company):
    news = newsapi.get_everything(
        q=company,
        language="en",
        sort_by="publishedAt",
        page_size=50
    )
    articles = news["articles"]
    headlines = []
    for article in articles:
        if article["title"] and article["title"] != "[Removed]":
            headlines.append({
                "title": article["title"],
                "published": article["publishedAt"],
                "source": article["source"]["name"]
            })
    return pd.DataFrame(headlines)

def analyze_sentiment(text):
    if text is None:
        return 0, "Neutral"
    analysis = TextBlob(str(text))
    score = analysis.sentiment.polarity
    if score > 0.1:
        sentiment = "Positive"
    elif score < -0.1:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"
    return score, sentiment

# ── UI ───────────────────────────────────────────────────
st.title("📈 Stock News Sentiment Analyzer")
st.markdown("Enter any company name to analyze live market sentiment from recent news!")
st.divider()

# Input
col1, col2 = st.columns([3, 1])
with col1:
    company = st.text_input("Enter Company Name",
                             placeholder="e.g. Tesla, Apple, Infosys, Reliance...")
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    analyze_btn = st.button("🔍 Analyze", use_container_width=True)

# Analysis
if analyze_btn and company:
    with st.spinner(f"Fetching live news for {company}..."):
        df = fetch_news(company)

    if df.empty:
        st.error("No news found! Try another company name.")
    else:
        # Analyze sentiment
        df["score"], df["sentiment"] = zip(
            *df["title"].apply(analyze_sentiment)
        )
        df["published"] = pd.to_datetime(df["published"])
        df = df.sort_values("published", ascending=False)

        avg_score = df["score"].mean()

        # ── Market mood banner ───────────────────────────
        st.divider()
        if avg_score > 0.1:
            st.success(f"## 🟢 Market Mood: BULLISH 📈")
            mood_color = "green"
        elif avg_score < -0.1:
            st.error(f"## 🔴 Market Mood: BEARISH 📉")
            mood_color = "red"
        else:
            st.warning(f"## 🟡 Market Mood: NEUTRAL ➡️")
            mood_color = "orange"

        # ── Metrics row ──────────────────────────────────
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Articles", len(df))
        m2.metric("Avg Sentiment Score", f"{avg_score:.3f}")
        m3.metric("Positive Articles",
                  len(df[df["sentiment"]=="Positive"]))
        m4.metric("Negative Articles",
                  len(df[df["sentiment"]=="Negative"]))

        st.divider()

        # ── Charts ───────────────────────────────────────
        c1, c2 = st.columns(2)

        with c1:
            # Pie chart
            fig1 = px.pie(
                df,
                names="sentiment",
                title=f"{company} Sentiment Distribution",
                color="sentiment",
                color_discrete_map={
                    "Positive": "#51cf66",
                    "Negative": "#ff6b6b",
                    "Neutral":  "#ffd43b"
                }
            )
            st.plotly_chart(fig1, use_container_width=True)

        with c2:
            # Sentiment over time
            fig2 = px.line(
                df,
                x="published",
                y="score",
                title=f"{company} Sentiment Over Time",
                color_discrete_sequence=["#339af0"]
            )
            fig2.add_hline(y=0, line_dash="dash",
                          line_color="gray")
            st.plotly_chart(fig2, use_container_width=True)

        st.divider()

        # ── Top headlines ────────────────────────────────
        col_pos, col_neg = st.columns(2)

        with col_pos:
            st.subheader("🟢 Top Positive Headlines")
            top_pos = df[df["sentiment"]=="Positive"].head(3)
            if top_pos.empty:
                st.info("No positive headlines found")
            for _, row in top_pos.iterrows():
                st.success(f"**{row['title'][:100]}...**\n\n"
                          f"Score: {row['score']:.3f} | "
                          f"Source: {row['source']}")

        with col_neg:
            st.subheader("🔴 Top Negative Headlines")
            top_neg = df[df["sentiment"]=="Negative"].head(3)
            if top_neg.empty:
                st.info("No negative headlines found")
            for _, row in top_neg.iterrows():
                st.error(f"**{row['title'][:100]}...**\n\n"
                        f"Score: {row['score']:.3f} | "
                        f"Source: {row['source']}")

        st.divider()

        # ── Full news table ──────────────────────────────
        st.subheader("📰 All Articles")
        st.dataframe(
            df[["title", "source", "sentiment",
                "score", "published"]],
            use_container_width=True
        )
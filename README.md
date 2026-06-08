<!-- <h4 align="center">
    <br> <img src="imgs/download.png">
</h4> -->

<h4 align="center">
    Market Signal Pipeline
</h4>

<p align="center">
    <a href="#description">Description</a> •
    <a href="#technology-stack">Tech Stack</a> •
    <a href="#architecture">Architecture</a> •
    <a href="#feature">Features</a> •
    <a href="#architecture-overview">Architecture</a> •
    <a href="#project-structure"> Structure </a>
</p>

## Description

This project is event-driven fintech project that collects recent financial news and market data, calculates deterministic quantitative indicators, generates bullish, bearish, or neutral signals, stores result in Firestore and sends a daily email report. 

This project demonstrates practical software engineering, quantitative analysis, cloud deployment, and event-driven architecture on Google Cloud Platform (GCP).

The MVP monitors a stock watchlist, such as:
- `AAPL`
- `NVDA`
- `TSLA`

For each scheduled run, the system:

1. Publishes a market-analysis event through Cloud Scheduler and Pub/Sub.
2. Fetches recent financial news and market data.
3. Deduplicates and filters relevant articles.
4. Calculates technical indicators and create quantitative analysis in Python
5. Produces a bullish, bearish, or neutral signal with a confidence score. 
6. Generates an evidence-grounded explanation using LLM API.
7. Stores the result in Firestore.
8. Sends one combined daily email report. 

## Technology Stack

### Application

- Python
- FastAPI
- pandas
- NumPy
- pandas-ta
- yfinance

### Google Cloud Platform

- Cloud Scheduler
- Pub/Sub
- Cloud Run
- Firestore
- Secret Manager
- Artifact Registry
- Cloud Logging

### External Integration

- undecided

## Architecture

![architecture](img/stock-market-signal-pipeline.jpg)

## Feature


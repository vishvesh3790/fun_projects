import yfinance as yf
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.model_selection import train_test_split, GridSearchCV
from textblob import TextBlob
import sys

st.set_page_config(page_title="Stock Analysis", layout="wide")

def prepare_data_for_rf(df, lookback=30):
    df = df.copy()
    # Create features
    df['SMA_5'] = df['Close'].rolling(window=5).mean()
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['RSI'] = calculate_rsi(df)
    df['Daily_Return'] = df['Close'].pct_change()
    df['Volatility'] = df['Daily_Return'].rolling(window=20).std()
    
    # Create target (next day's closing price)
    df['Target'] = df['Close'].shift(-1)
    
    # Drop NaN values
    df = df.dropna()
    
    # Features for prediction
    features = ['Close', 'SMA_5', 'SMA_20', 'RSI', 'Volatility', 'Volume']
    X = df[features]
    y = df['Target']
    
    return X, y

def prepare_data_for_lstm(data, lookback=60):
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(data['Close'].values.reshape(-1, 1))
    
    X, y = [], []
    for i in range(lookback, len(scaled_data)):
        X.append(scaled_data[i-lookback:i, 0])
        y.append(scaled_data[i, 0])
    
    X, y = np.array(X), np.array(y)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))  # Reshape for LSTM
    
    return X, y, scaler

def create_lstm_model(lookback):
    model = Sequential([
        LSTM(units=50, return_sequences=True, input_shape=(lookback, 1)),
        Dropout(0.2),
        LSTM(units=50, return_sequences=False),
        Dropout(0.2),
        Dense(units=1)
    ])
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

def calculate_rsi(data, periods=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def get_news(ticker):
    news_data = []
    try:
        # Fetch from Finviz
        url = f"https://finviz.com/quote.ashx?t={ticker}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        news_table = soup.find(id='news-table')
        
        if news_table:
            for row in news_table.findAll('tr')[:5]:
                title = row.a.text
                link = row.a['href']
                news_data.append({'title': title, 'link': link})
        
        # Fetch from Yahoo Finance
        yahoo_url = f"https://finance.yahoo.com/quote/{ticker}/news?p={ticker}"
        response = requests.get(yahoo_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        yahoo_news = soup.find_all('li', class_='js-stream-content')
        
        for item in yahoo_news[:5]:
            title = item.find('h3').text
            link = item.find('a')['href']
            if not link.startswith('http'):
                link = 'https://finance.yahoo.com' + link
            news_data.append({'title': title, 'link': link})

        return news_data
    except Exception as e:
        return ["Error fetching news: " + str(e)]

def analyze_stock_health(info):
    health_score = 0
    analysis = []
    
    # Debt Analysis
    total_debt = info.get('totalDebt', 0) or 0
    cash = info.get('totalCash', 0) or 0
    if cash > total_debt:
        analysis.append("Company has more cash than debt")
        health_score += 2
    elif total_debt > 0:
        debt_to_cash = total_debt / cash if cash > 0 else float('inf')
        if debt_to_cash < 2:
            analysis.append("Manageable debt levels")
            health_score += 1
        else:
            analysis.append("High debt levels")
    
    # Profitability
    profit_margin = info.get('profitMargin', 0) or 0
    if profit_margin > 0.2:
        analysis.append("Strong profit margins")
        health_score += 2
    elif profit_margin > 0.1:
        analysis.append("Decent profit margins")
        health_score += 1
    else:
        analysis.append("Low profit margins")
    
    # Growth
    revenue_growth = info.get('revenueGrowth', 0) or 0
    if revenue_growth > 0.1:
        analysis.append("Good revenue growth")
        health_score += 2
    elif revenue_growth > 0:
        analysis.append("Moderate revenue growth")
        health_score += 1
    else:
        analysis.append("Declining revenue")
    
    return analysis, health_score

def get_buy_sell_recommendation(rsi, health_score, info, rf_pred, lstm_pred, current_price):
    recommendation = []
    
    # RSI Analysis
    if rsi < 30:
        recommendation.append("RSI indicates stock is oversold - potential buying opportunity")
    elif rsi > 70:
        recommendation.append("RSI indicates stock is overbought - consider waiting")
    else:
        recommendation.append("RSI is neutral")
    
    # Model Predictions Analysis
    rf_change = (rf_pred - current_price) / current_price * 100
    lstm_change = (lstm_pred - current_price) / current_price * 100
    
    recommendation.append(f"Random Forest predicts a {rf_change:.2f}% {'increase' if rf_change > 0 else 'decrease'}")
    recommendation.append(f"LSTM predicts a {lstm_change:.2f}% {'increase' if lstm_change > 0 else 'decrease'}")
    
    # Analyst Recommendations
    target_price = info.get('targetMeanPrice', 0) or 0
    current_price = info.get('currentPrice', 0) or 0
    if target_price > current_price * 1.2:
        recommendation.append("Analysts suggest significant upside potential")
    elif target_price < current_price:
        recommendation.append("Analysts suggest potential downside")
    
    # Overall Health Score
    if health_score >= 4:
        recommendation.append("Company shows strong financial health")
    elif health_score >= 2:
        recommendation.append("Company shows moderate financial health")
    else:
        recommendation.append("Company shows weak financial health")
    
    return recommendation

def fine_tune_random_forest(X_train, y_train):
    param_grid = {
        'n_estimators': [50, 100, 150],
        'max_depth': [None, 10, 20, 30],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4]
    }
    rf_model = RandomForestRegressor(random_state=42)
    grid_search = GridSearchCV(estimator=rf_model, param_grid=param_grid, cv=3, n_jobs=-1, verbose=2)
    grid_search.fit(X_train, y_train)
    return grid_search.best_estimator_

def main():
    try:
        st.title("Advanced Stock Analysis Dashboard")
        
        # Debug information
        st.sidebar.write("Debug Information:")
        st.sidebar.write(f"Python Version: {sys.version}")
        st.sidebar.write(f"Streamlit Version: {st.__version__}")
        
        # Input for multiple stock tickers
        ticker_symbols = st.text_area("Enter Stock Ticker Symbols (comma-separated, e.g., AAPL, MSFT, GOOGL):", "AAPL").upper()
        ticker_list = [ticker.strip() for ticker in ticker_symbols.split(',') if ticker.strip()]
        
        if not ticker_list:
            st.warning("Please enter at least one valid stock ticker symbol.")
            return
            
        for ticker in ticker_list:
            try:
                st.info(f"Fetching data for {ticker}...")
                # Fetch stock data
                df = yf.download(ticker, start='2020-01-01', end=datetime.now())
                
                if df.empty:
                    st.error(f"No data found for ticker: {ticker}")
                    continue
                    
                df.reset_index(inplace=True)

                # Display stock data
                st.subheader(f"Stock Data for {ticker}")
                st.write(df.tail())  # Display the last few rows of the data

                # Plotting the stock price
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], mode='lines', name='Close Price'))
                fig.update_layout(
                    title=f'Stock Price of {ticker}',
                    xaxis_title='Date',
                    yaxis_title='Price (USD)',
                    template='plotly_white'
                )
                st.plotly_chart(fig)

                # Calculate RSI
                df['RSI'] = calculate_rsi(df)
                
                # Display RSI
                st.subheader("RSI Analysis")
                current_rsi = df['RSI'].iloc[-1]
                st.metric("Current RSI", f"{current_rsi:.2f}")
                
                if current_rsi < 30:
                    st.warning("Stock may be oversold")
                elif current_rsi > 70:
                    st.warning("Stock may be overbought")
                else:
                    st.info("RSI is in neutral territory")

            except Exception as e:
                st.error(f"Error processing {ticker}: {str(e)}")
                st.error("Stack trace:", exc_info=True)
                continue

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.error("Please check your input and try again.")

if __name__ == "__main__":
    main()
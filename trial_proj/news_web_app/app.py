from flask import Flask, render_template, jsonify
from flask_apscheduler import APScheduler
import requests
from datetime import datetime
import json
import os

app = Flask(__name__)
scheduler = APScheduler()

# News cache
news_cache = {
    'top': None,
    'politics': None,
    'world': None,
    'business': None,
    'technology': None,
    'last_updated': None
}

def fetch_news(category=None):
    """Fetch news from the API"""
    base_url = "https://saurav.tech/NewsAPI/"
    
    if category == "top":
        url = f"{base_url}/top-headlines/category/general/in.json"
    elif category == "politics":
        url = f"{base_url}/top-headlines/category/politics/in.json"
    elif category == "world":
        url = f"{base_url}/top-headlines/category/general/us.json"
    elif category == "business":
        url = f"{base_url}/top-headlines/category/business/in.json"
    elif category == "technology":
        url = f"{base_url}/top-headlines/category/technology/in.json"
    else:
        url = f"{base_url}/top-headlines/category/general/in.json"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching news for {category}: {str(e)}")
        return None

def update_news_cache():
    """Update the news cache with fresh data"""
    categories = ['top', 'politics', 'world', 'business', 'technology']
    for category in categories:
        news_data = fetch_news(category)
        if news_data and 'articles' in news_data:
            # Keep only top 10 articles
            news_cache[category] = news_data['articles'][:10]
    
    news_cache['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"News cache updated at {news_cache['last_updated']}")

@app.route('/')
def home():
    """Render the home page"""
    return render_template('index.html', 
                         last_updated=news_cache['last_updated'],
                         top_news=news_cache['top'])

@app.route('/category/<category>')
def category_news(category):
    """Render category-specific news page"""
    if category not in news_cache:
        return "Category not found", 404
    
    return render_template('category.html',
                         category=category.capitalize(),
                         news=news_cache[category],
                         last_updated=news_cache['last_updated'])

@app.route('/api/news/<category>')
def get_news_api(category):
    """API endpoint to get news data"""
    if category not in news_cache:
        return jsonify({'error': 'Category not found'}), 404
    
    return jsonify({
        'category': category,
        'articles': news_cache[category],
        'last_updated': news_cache['last_updated']
    })

def init_scheduler():
    """Initialize the scheduler for periodic news updates"""
    scheduler.add_job(id='update_news',
                     func=update_news_cache,
                     trigger='interval',
                     minutes=30)  # Update every 30 minutes
    scheduler.start()

if __name__ == '__main__':
    # Initial news fetch
    update_news_cache()
    
    # Start scheduler
    init_scheduler()
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5001)

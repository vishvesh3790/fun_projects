import streamlit as st
import requests
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="Global News Hub",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .stButton button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #4287f5;
        color: white;
    }
    .news-card {
        padding: 1rem;
        border-radius: 10px;
        background-color: #1a1f2c;
        border: 1px solid #2d3544;
        margin: 1rem 0;
    }
    .news-title {
        color: #ffffff;
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .news-meta {
        color: #8b949e;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }
    .news-description {
        color: #c9d1d9;
        font-size: 1rem;
        margin-bottom: 0.5rem;
    }
    .news-link {
        color: #4287f5;
        text-decoration: none;
    }
    .news-link:hover {
        text-decoration: underline;
    }
</style>
""", unsafe_allow_html=True)

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
    else:
        url = f"{base_url}/top-headlines/category/general/in.json"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except Exception as e:
        st.error(f"Error fetching news: {str(e)}")
        return None

def display_news(articles):
    """Display news articles in a card format"""
    if not articles:
        st.warning("No news articles found.")
        return
    
    # Display only top 10 articles
    for article in articles[:10]:
        with st.container():
            st.markdown(f"""
            <div class="news-card">
                <div class="news-title">{article['title']}</div>
                <div class="news-meta">
                    {article['source']['name']} • {article['publishedAt'][:10]}
                </div>
                <div class="news-description">{article.get('description', 'No description available.')}</div>
                <a href="{article['url']}" target="_blank" class="news-link">Read more →</a>
            </div>
            """, unsafe_allow_html=True)

# Sidebar
st.sidebar.title("📰 News Categories")
selected_category = st.sidebar.radio(
    "Select News Category",
    ["Top Headlines", "Politics", "International", "Business", "Technology"]
)

# Main content
st.title("🌍 Global News Hub")
st.markdown("Stay informed with the latest news from around the world.")

# Display news based on selection
if selected_category == "Top Headlines":
    st.header("📈 Top Headlines")
    news = fetch_news("top")
    if news:
        display_news(news['articles'])
        
elif selected_category == "Politics":
    st.header("🏛️ Political News")
    news = fetch_news("politics")
    if news:
        display_news(news['articles'])
        
elif selected_category == "International":
    st.header("🌏 International News")
    news = fetch_news("world")
    if news:
        display_news(news['articles'])
        
elif selected_category == "Business":
    st.header("💼 Business News")
    news = fetch_news("business")
    if news:
        display_news(news['articles'])
        
elif selected_category == "Technology":
    st.header("💻 Technology News")
    news = fetch_news("technology")
    if news:
        display_news(news['articles'])

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #8b949e;'>
    Data refreshed every hour • All times in local timezone
</div>
""", unsafe_allow_html=True)

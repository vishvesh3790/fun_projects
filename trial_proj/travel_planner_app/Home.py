import streamlit as st

st.set_page_config(
    page_title="Travel Planner - Home",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for mobile optimization with dark theme
st.markdown("""
<style>
    /* Mobile-first styles */
    .stButton button {
        width: 100%;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: #4287f5;
        color: white;
        border: none;
        border-radius: 5px;
    }
    
    /* Make text more readable on mobile */
    .main p, .main li {
        font-size: 1.1rem;
        line-height: 1.6;
        color: #fafafa;
    }
    
    /* Better spacing for mobile */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Responsive columns */
    @media (max-width: 640px) {
        .row-widget.stHorizontal > div {
            flex: 1 1 100%;
            width: 100%;
        }
    }
    
    /* Custom card-like containers */
    div[data-testid="stMarkdownContainer"] > div {
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        background-color: #1a1f2c;
        border: 1px solid #2d3544;
        color: #fafafa;
    }
    
    div[data-testid="stMarkdownContainer"] h3 {
        color: #4287f5;
        margin-bottom: 1rem;
    }
    
    /* Hide source code tags */
    div[data-testid="stMarkdownContainer"] > div.css-card::before,
    div[data-testid="stMarkdownContainer"] > div.css-card::after {
        display: none;
    }
    
    /* Adjust link colors */
    a {
        color: #4287f5 !important;
        text-decoration: none;
    }
    
    a:hover {
        color: #6ba1f7 !important;
        text-decoration: underline;
    }
    
    /* Footer styling */
    .footer {
        position: fixed;
        bottom: 0;
        width: 100%;
        text-align: center;
        padding: 1rem;
        background: rgba(26, 31, 44, 0.9);
        backdrop-filter: blur(10px);
        border-top: 1px solid #2d3544;
    }
    
    /* Hide specific elements */
    .element-container iframe {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# Main content
st.title("Welcome to Travel Planner 🌍")

# Features section
st.header("Features")

# Create columns for features
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    #### 📍 Route Planning
    - Compare multiple transport modes
    - Real-time distance calculation
    - Estimated travel times
    - Cost predictions for each route
    
    #### 🗺️ Interactive Maps
    - Live map visualization
    - Multiple waypoint support
    - Direct Google Maps integration
    - Satellite and terrain views
    """)

with col2:
    st.markdown("""
    #### 📱 Mobile Friendly
    - Responsive design for all devices
    - Touch-optimized interface
    - Quick location detection
    - Offline route saving
    
    #### 📅 Trip Organization
    - Detailed day-by-day planning
    - Cost tracking and budgeting
    - Activity scheduling
    - Export to calendar
    """)

# Quick Actions section
st.header("Quick Start 🚀")

col1, col2 = st.columns(2)
with col1:
    if st.button("🗺️ Plan New Route", use_container_width=True):
        st.switch_page("pages/1_Route_Planner.py")
with col2:
    if st.button("📅 Create Itinerary", use_container_width=True):
        st.switch_page("pages/2_Itinerary_Planner.py")

# Getting Started
st.markdown("""
<div>
    <h3>Getting Started 🎯</h3>
    <ol>
        <li>Click <strong>Plan New Route</strong> to start planning your journey</li>
        <li>Enter your start and destination points</li>
        <li>Compare different transport options</li>
        <li>Create a detailed itinerary for your trip</li>
    </ol>
</div>
""", unsafe_allow_html=True)

# Tips section
with st.expander("💡 Pro Tips"):
    st.markdown("""
    * Save frequently used locations in Settings
    * Use current location for quicker planning
    * Export your itinerary for offline access
    * Open routes directly in Google Maps
    """)

# Footer
st.markdown("""
<div class='footer'>
    Made with ❤️ for travelers
</div>
""", unsafe_allow_html=True)

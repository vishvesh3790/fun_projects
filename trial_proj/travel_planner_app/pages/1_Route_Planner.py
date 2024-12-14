import streamlit as st
import folium
from streamlit_folium import folium_static
from datetime import datetime, timedelta
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from branca.element import Figure
import branca.colormap as cm
import requests
import json

# Import functions from the main file
from travel_planner import (
    get_user_location,
    load_favorite_locations,
    save_favorite_location,
    get_coordinates,
    get_route_options,
    create_route_map,
    create_google_maps_url
)

st.set_page_config(
    page_title="Route Planner",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Add mobile-friendly CSS
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
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Responsive columns */
    @media (max-width: 640px) {
        .row-widget.stHorizontal > div {
            flex: 1 1 100%;
            width: 100%;
        }
        
        /* Stack columns on mobile */
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            margin-bottom: 1rem;
        }
        
        /* Adjust map size for mobile */
        [data-testid="stIframe"] {
            height: 400px !important;
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
    
    /* Hide source code tags */
    div[data-testid="stMarkdownContainer"] > div::before,
    div[data-testid="stMarkdownContainer"] > div::after {
        display: none;
    }
    
    /* Make Google Maps button more prominent */
    .google-maps-button {
        background-color: #4287f5;
        color: white;
        padding: 0.8rem 1rem;
        border-radius: 5px;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        margin: 1rem 0;
        width: 100%;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

st.title("Route Planner ")

# Initialize favorite locations
load_favorite_locations()

# Get user's current location
if 'user_location' not in st.session_state:
    location, coords = get_user_location()
    if location:
        st.session_state.user_location = location
        st.session_state.user_coords = coords

# Get start and end points
col1, col2 = st.columns(2)

with col1:
    st.header("Starting Point")
    
    # Add favorite locations selector for start point
    start_favorites = ['Current Location'] + list(st.session_state.favorite_locations.keys())
    selected_start = st.selectbox(
        "Choose from saved locations:",
        start_favorites,
        key="start_favorite"
    )
    
    if selected_start == 'Current Location' and 'user_location' in st.session_state:
        start_point = st.text_input(
            "Enter your starting location:",
            value=st.session_state.user_location
        )
    else:
        saved_location = st.session_state.favorite_locations.get(selected_start, '')
        start_point = st.text_input(
            "Enter your starting location:",
            value=saved_location
        )
    
    # Save as favorite option
    if start_point:
        save_as_favorite = st.checkbox("Save as favorite location", key="save_start")
        if save_as_favorite:
            favorite_name = st.text_input(
                "Save as:",
                key="start_favorite_name"
            )
            if st.button("Save Location", key="save_start_btn"):
                save_favorite_location(favorite_name, start_point)
                st.success(f"Saved {start_point} as {favorite_name}")
        
        start_coords, start_address = get_coordinates(start_point)
        if start_coords:
            st.success(f"Starting point found: {start_address}")
        else:
            st.error("Could not find coordinates for the starting point")

with col2:
    st.header("Destination")
    
    # Add favorite locations selector for end point
    end_favorites = [''] + list(st.session_state.favorite_locations.keys())
    selected_end = st.selectbox(
        "Choose from saved locations:",
        end_favorites,
        key="end_favorite"
    )
    
    saved_location = st.session_state.favorite_locations.get(selected_end, '')
    end_point = st.text_input(
        "Enter your destination:",
        value=saved_location
    )
    
    # Save as favorite option
    if end_point:
        save_as_favorite = st.checkbox("Save as favorite location", key="save_end")
        if save_as_favorite:
            favorite_name = st.text_input(
                "Save as:",
                key="end_favorite_name"
            )
            if st.button("Save Location", key="save_end_btn"):
                save_favorite_location(favorite_name, end_point)
                st.success(f"Saved {end_point} as {favorite_name}")
        
        end_coords, end_address = get_coordinates(end_point)
        if end_coords:
            st.success(f"Destination found: {end_address}")
        else:
            st.error("Could not find coordinates for the destination")

# Only proceed if both points are valid
if (start_point and end_point and 'start_coords' in locals() and 'end_coords' in locals() 
    and start_coords and end_coords and start_address and end_address):
    
    # Add Open in Google Maps button
    google_maps_url = create_google_maps_url(start_coords, end_coords)
    st.markdown(f"""
    <a href='{google_maps_url}' target='_blank' class='google-maps-button'>
        <img src='https://www.google.com/images/branding/product/1x/maps_32dp.png' style='height: 20px;'/>
        Open in Google Maps
    </a>
    """, unsafe_allow_html=True)
    
    st.header("Route Options")
    
    # Get route options
    with st.spinner("Calculating routes..."):
        routes = get_route_options(start_coords, end_coords)
    
    if not routes:
        st.error("No routes found between these locations.")
    else:
        # Display route options in tabs
        transport_tabs = st.tabs(list(routes.keys()))
        
        for i, (mode, details) in enumerate(routes.items()):
            with transport_tabs[i]:
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.subheader(f"{mode} Route Details")
                    st.write(f"**Duration:** {details['duration']}")
                    st.write(f"**Distance:** {details['distance']}")
                    st.write(f"**Estimated Cost:** {details['estimated_cost']}")
                    st.write("**Route Description:**")
                    for desc in details['route_description']:
                        st.write(f"- {desc}")
                
                with col2:
                    if st.button(f"Select {mode} Route", key=f"select_{mode}"):
                        st.session_state['selected_route'] = {
                            'mode': mode,
                            'details': details
                        }
                        st.success(f"{mode} route selected! Proceed to itinerary planning.")
        
        # Show route map
        st.header("Route Map")
        selected_mode = st.session_state.get('selected_route', {}).get('mode', 'Driving')
        selected_details = st.session_state.get('selected_route', {}).get('details', None)
        
        route_map = create_route_map(
            start_coords, 
            end_coords, 
            start_address, 
            end_address, 
            selected_mode,
            selected_details
        )
        
        if route_map:
            folium_static(route_map, width=1200, height=600)
        
        # If route is selected, show proceed button
        if 'selected_route' in st.session_state:
            if st.button("Proceed to Itinerary Planning"):
                st.switch_page("pages/2_Itinerary_Planner.py")
        
        # Show travel dates input after route selection
        if 'selected_route' in st.session_state:
            st.header("Travel Dates")
            col1, col2 = st.columns(2)
            
            with col1:
                start_date = st.date_input(
                    "Start Date",
                    min_value=datetime.now().date()
                )
            
            with col2:
                mode = st.session_state['selected_route']['mode']
                duration_str = st.session_state['selected_route']['details']['duration']
                try:
                    hours = float(duration_str.split()[0])
                    suggested_days = max(1, int(hours / 8) + 1)  # Assume 8 hours of travel per day
                except:
                    suggested_days = 1
                
                duration = st.number_input(
                    "Duration (days)",
                    min_value=1,
                    value=suggested_days
                )
            
            end_date = start_date + timedelta(days=duration-1)
            st.write(f"Return Date: {end_date}")

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

# Initialize Nominatim geocoder
geolocator = Nominatim(user_agent="travel_planner")

# Custom map styles
MAP_STYLES = {
    "Driving": {
        "color": "#FF5733",
        "weight": 3,
        "opacity": 0.8,
        "dash_array": None
    },
    "Train": {
        "color": "#3498DB",
        "weight": 3,
        "opacity": 0.8,
        "dash_array": "10, 10"
    },
    "Flying": {
        "color": "#2ECC71",
        "weight": 3,
        "opacity": 0.8,
        "dash_array": "15, 10, 5, 10"
    }
}

def get_user_location():
    """Get user's location based on IP address"""
    try:
        response = requests.get('https://ipapi.co/json/')
        if response.status_code == 200:
            data = response.json()
            location = f"{data['city']}, {data['region']}, {data['country_name']}"
            coords = (float(data['latitude']), float(data['longitude']))
            return location, coords
        return None, None
    except Exception as e:
        st.warning("Could not detect your location automatically.")
        return None, None

def load_favorite_locations():
    """Load favorite locations from session state"""
    if 'favorite_locations' not in st.session_state:
        st.session_state.favorite_locations = {
            'Home': '',
            'Work': '',
            'Favorite 1': '',
            'Favorite 2': ''
        }

def save_favorite_location(name, location):
    """Save a location to favorites"""
    st.session_state.favorite_locations[name] = location

def get_coordinates(location_name):
    """Get coordinates using Nominatim"""
    try:
        location = geolocator.geocode(location_name)
        if location:
            return (location.latitude, location.longitude), location.address
        return None, None
    except Exception as e:
        st.error(f"Error getting coordinates: {str(e)}")
        return None, None

def get_route_options(start_coords, end_coords):
    """Get different route options between two points"""
    routes = {}
    
    try:
        # Calculate direct distance
        direct_distance = geodesic(start_coords, end_coords).kilometers
        
        # Simulate different route options
        if direct_distance <= 500:  # Short distance
            routes["Driving"] = {
                "duration": f"{round(direct_distance/60, 1)} hours",
                "distance": f"{round(direct_distance)} km",
                "route_description": ["Take major highways", "Regular rest stops available"],
                "estimated_cost": f"${round(direct_distance * 0.1)}",  # Rough estimate for gas
                "waypoints": [start_coords, end_coords]
            }
            routes["Train"] = {
                "duration": f"{round(direct_distance/100, 1)} hours",
                "distance": f"{round(direct_distance * 1.2)} km",
                "route_description": ["High-speed rail available", "City center stations"],
                "estimated_cost": f"${round(direct_distance * 0.15)}",
                "waypoints": [start_coords, end_coords]
            }
        else:  # Long distance
            routes["Flying"] = {
                "duration": f"{round(direct_distance/800, 1)} hours",
                "distance": f"{round(direct_distance)} km",
                "route_description": ["Direct flight available", "Airport transfers required"],
                "estimated_cost": f"${round(100 + direct_distance * 0.1)}",
                "waypoints": [start_coords, end_coords]
            }
            routes["Train"] = {
                "duration": f"{round(direct_distance/70, 1)} hours",
                "distance": f"{round(direct_distance * 1.2)} km",
                "route_description": ["Multiple train changes", "Sleeper cars available"],
                "estimated_cost": f"${round(direct_distance * 0.08)}",
                "waypoints": [start_coords, end_coords]
            }
            routes["Driving"] = {
                "duration": f"{round(direct_distance/60, 1)} hours",
                "distance": f"{round(direct_distance * 1.1)} km",
                "route_description": ["Multiple day journey", "Hotel stops recommended"],
                "estimated_cost": f"${round(direct_distance * 0.12)}",  # Including estimated hotel costs
                "waypoints": [start_coords, end_coords]
            }
        
        return routes
    except Exception as e:
        st.error(f"Error calculating routes: {str(e)}")
        return {}

def create_route_map(start_coords, end_coords, start_address, end_address, mode="Driving", route_details=None):
    """Create an enhanced map showing the route between start and end points"""
    try:
        # Create a figure with a specific size
        fig = Figure(width="100%", height="100%")
        
        # Create the map with a modern tile layer
        m = folium.Map(
            location=start_coords,
            zoom_start=6,
            tiles='cartodbpositron',
            width="100%",
            height="100%"
        )
        
        # Add markers for start and end points with custom icons and popups
        start_html = f"""
            <div style='font-family: Arial, sans-serif; font-size: 12px;'>
                <b>Starting Point:</b><br>
                {start_address}<br>
                <i>Coordinates: {start_coords[0]:.4f}, {start_coords[1]:.4f}</i>
            </div>
        """
        
        end_html = f"""
            <div style='font-family: Arial, sans-serif; font-size: 12px;'>
                <b>Destination:</b><br>
                {end_address}<br>
                <i>Coordinates: {end_coords[0]:.4f}, {end_coords[1]:.4f}</i>
            </div>
        """
        
        # Add custom markers
        folium.Marker(
            start_coords,
            popup=folium.Popup(start_html, max_width=300),
            icon=folium.Icon(color='green', icon='info-sign'),
            tooltip="Starting Point"
        ).add_to(m)
        
        folium.Marker(
            end_coords,
            popup=folium.Popup(end_html, max_width=300),
            icon=folium.Icon(color='red', icon='info-sign'),
            tooltip="Destination"
        ).add_to(m)
        
        # Get style for the mode
        style = MAP_STYLES.get(mode, MAP_STYLES["Driving"])
        
        # Draw route line
        if route_details and route_details.get('waypoints'):
            points = route_details['waypoints']
        else:
            points = [start_coords, end_coords]
        
        # Create the route line
        folium.PolyLine(
            points,
            weight=style["weight"],
            color=style["color"],
            opacity=style["opacity"],
            dash_array=style["dash_array"],
            tooltip=f"{mode} Route"
        ).add_to(m)
        
        # Add interactive features
        folium.plugins.MousePosition().add_to(m)
        folium.plugins.MeasureControl().add_to(m)
        minimap = folium.plugins.MiniMap(toggle_display=True)
        m.add_child(minimap)
        
        # Fit the map to show all points
        m.fit_bounds([start_coords, end_coords])
        
        # Add the map to the figure
        fig.add_child(m)
        return fig
    
    except Exception as e:
        st.error(f"Error creating map: {str(e)}")
        return None

def create_google_maps_url(start_coords, end_coords, mode="driving"):
    """Create a Google Maps URL with the given coordinates"""
    # Convert transport mode to Google Maps format
    mode_map = {
        "Driving": "driving",
        "Train": "transit",
        "Flying": "flying"
    }
    transport_mode = mode_map.get(mode, "driving")
    
    # Create the URL
    base_url = "https://www.google.com/maps/dir/?api=1"
    params = {
        "origin": f"{start_coords[0]},{start_coords[1]}",
        "destination": f"{end_coords[0]},{end_coords[1]}",
        "travelmode": transport_mode
    }
    
    # Build the URL with parameters
    url_params = "&".join([f"{k}={v}" for k, v in params.items()])
    return f"{base_url}&{url_params}"

def main():
    st.title("Travel Route Planner ")
    
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
                favorite_name = st.selectbox(
                    "Save as:",
                    list(st.session_state.favorite_locations.keys()),
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
                favorite_name = st.selectbox(
                    "Save as:",
                    list(st.session_state.favorite_locations.keys()),
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
        <div style='text-align: center; margin-bottom: 1rem;'>
            <a href='{google_maps_url}' target='_blank'>
                <button style='
                    background-color: #4285f4;
                    color: white;
                    padding: 10px 20px;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 16px;
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                '>
                    <img src='https://www.google.com/images/branding/product/1x/maps_32dp.png' style='height: 20px;'/>
                    Open in Google Maps
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)
        
        st.header("Route Options")
        
        # Get route options
        with st.spinner("Calculating routes..."):
            routes = get_route_options(start_coords, end_coords)
        
        if not routes:
            st.error("No routes found between these locations.")
            return
        
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
        
        # Update Google Maps link when route mode is selected
        if selected_mode:
            google_maps_url = create_google_maps_url(start_coords, end_coords, selected_mode)
            st.markdown(f"""
            <div style='text-align: center; margin-bottom: 1rem;'>
                <a href='{google_maps_url}' target='_blank'>
                    <button style='
                        background-color: #4285f4;
                        color: white;
                        padding: 10px 20px;
                        border: none;
                        border-radius: 5px;
                        cursor: pointer;
                        font-size: 16px;
                        display: inline-flex;
                        align-items: center;
                        gap: 8px;
                    '>
                        <img src='https://www.google.com/images/branding/product/1x/maps_32dp.png' style='height: 20px;'/>
                        Open {selected_mode} Route in Google Maps
                    </button>
                </a>
            </div>
            """, unsafe_allow_html=True)
        
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
            if st.button("Proceed to Itinerary Planning", key="proceed_button"):
                st.session_state['planning_stage'] = 'itinerary'
        
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

if __name__ == "__main__":
    main()

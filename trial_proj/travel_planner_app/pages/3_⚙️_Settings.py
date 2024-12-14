import streamlit as st

st.set_page_config(
    page_title="Settings",
    page_icon="⚙️",
    layout="wide"
)

st.title("Settings ⚙️")

# Favorite Locations Management
st.header("Manage Favorite Locations")

if 'favorite_locations' not in st.session_state:
    st.session_state.favorite_locations = {
        'Home': '',
        'Work': '',
        'Favorite 1': '',
        'Favorite 2': ''
    }

# Edit favorite locations
for name in st.session_state.favorite_locations.keys():
    current_value = st.session_state.favorite_locations[name]
    new_value = st.text_input(
        f"{name}:",
        value=current_value,
        key=f"setting_{name}"
    )
    if new_value != current_value:
        st.session_state.favorite_locations[name] = new_value
        st.success(f"Updated {name} location!")

# Display preferences
st.header("Display Preferences")

# Map settings
st.subheader("Map Settings")
col1, col2 = st.columns(2)

with col1:
    default_map_style = st.selectbox(
        "Default Map Style",
        ["Standard", "Satellite", "Terrain"],
        key="map_style"
    )

with col2:
    default_transport = st.selectbox(
        "Default Transport Mode",
        ["Driving", "Train", "Flying"],
        key="transport_mode"
    )

# Cost settings
st.subheader("Cost Settings")
col1, col2 = st.columns(2)

with col1:
    currency = st.selectbox(
        "Currency",
        ["USD ($)", "EUR (€)", "GBP (£)", "JPY (¥)", "INR (₹)"],
        key="currency"
    )

with col2:
    cost_per_km = st.number_input(
        "Cost per km (for driving)",
        min_value=0.0,
        value=0.1,
        step=0.01,
        key="cost_per_km"
    )

# Save settings
if st.button("Save Settings"):
    # Here you would typically save these settings to a configuration file
    # For now, we'll just store them in session state
    st.session_state.update({
        'default_map_style': default_map_style,
        'default_transport': default_transport,
        'currency': currency,
        'cost_per_km': cost_per_km
    })
    st.success("Settings saved successfully!")

# Clear all data
st.header("Data Management")
if st.button("Clear All Data", type="secondary"):
    # Add a confirmation dialog
    if st.checkbox("Are you sure? This will clear all your saved locations and preferences."):
        # Clear session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("All data cleared successfully!")
        st.experimental_rerun()

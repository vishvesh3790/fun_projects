import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

st.set_page_config(
    page_title="Itinerary Planner",
    page_icon="📅",
    layout="wide"
)

st.title("Itinerary Planner 📅")

if 'selected_route' not in st.session_state:
    st.warning("Please select a route first in the Route Planner!")
    st.stop()

# Display selected route information
route = st.session_state['selected_route']
st.header("Selected Route")
st.write(f"**Mode:** {route['mode']}")
st.write(f"**Duration:** {route['details']['duration']}")
st.write(f"**Distance:** {route['details']['distance']}")

# Get or create itinerary
if 'itinerary' not in st.session_state:
    st.session_state.itinerary = []

# Add activity form
st.header("Add Activity")
col1, col2, col3 = st.columns(3)

with col1:
    activity_date = st.date_input(
        "Date",
        min_value=datetime.now().date()
    )

with col2:
    activity_time = st.time_input(
        "Time",
        datetime.now().time()
    )

with col3:
    activity_type = st.selectbox(
        "Type",
        ["🍽️ Food", "🏰 Sightseeing", "🏨 Accommodation", "🚗 Transport", "🎯 Activity"]
    )

activity_name = st.text_input("Activity Name")
activity_notes = st.text_area("Notes")
activity_cost = st.number_input("Estimated Cost", min_value=0.0, step=10.0)

if st.button("Add to Itinerary"):
    st.session_state.itinerary.append({
        "date": activity_date,
        "time": activity_time,
        "type": activity_type,
        "name": activity_name,
        "notes": activity_notes,
        "cost": activity_cost
    })
    st.success("Activity added to itinerary!")

# Display itinerary
if st.session_state.itinerary:
    st.header("Your Itinerary")
    
    # Convert to DataFrame for better display
    df = pd.DataFrame(st.session_state.itinerary)
    df['datetime'] = pd.to_datetime(df['date'].astype(str) + ' ' + df['time'].astype(str))
    df = df.sort_values('datetime')
    
    # Group by date
    for date in df['date'].unique():
        st.subheader(date.strftime('%A, %B %d, %Y'))
        day_activities = df[df['date'] == date].copy()
        
        for _, activity in day_activities.iterrows():
            with st.expander(f"{activity['time'].strftime('%H:%M')} - {activity['type']} {activity['name']}"):
                st.write(f"**Notes:** {activity['notes']}")
                st.write(f"**Cost:** ${activity['cost']:.2f}")
    
    # Show total cost
    total_cost = df['cost'].sum()
    st.metric("Total Estimated Cost", f"${total_cost:.2f}")
    
    # Export options
    if st.button("Export Itinerary"):
        # Create a more detailed DataFrame for export
        export_df = df[['datetime', 'type', 'name', 'notes', 'cost']]
        export_df.columns = ['Date & Time', 'Type', 'Activity', 'Notes', 'Cost']
        
        # Convert to CSV
        csv = export_df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="travel_itinerary.csv",
            mime="text/csv"
        )

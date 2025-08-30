import streamlit as st
from main import app  

st.set_page_config(page_title="LangGraph Travel Planner", page_icon="🗺️", layout="centered")

st.title("🗺️ LangGraph Travel Planner")


location = st.text_input("Enter location", placeholder="e.g., Bangalore")
days = st.number_input("Number of days", min_value=1, max_value=15, step=1)

if st.button("Generate Itinerary"):
    if location.strip():
        with st.spinner("Generating your travel plan..."):
            user_request = f"I want to go for a trip to {location} for {days} days"
            result = app.invoke({'message': user_request})
        
        st.subheader(f"📌 Itinerary for {location}")
        if 'plan' in result:
            st.write(result['plan'])
        else:
            st.warning("No plan generated. Check your LangGraph nodes and API responses.")
    else:
        st.warning("⚠️ Please enter a location.")
import streamlit as st
import json
import os
import pandas as pd

st.set_page_config(page_title="VOC Explorer", page_icon="📜", layout="wide")

def load_data():
    if os.path.exists('data.json'):
        with open('data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

data = load_data()

st.title("📜 VOC Historical Person Explorer")

if data:
    tab_search, tab_stats = st.tabs(["🔍 Search", "📊 Statistics"])

    with tab_search:
        query = st.text_input("Search by name...", placeholder="e.g. Jan")
        
        with st.expander("🛠️ Advanced Search"):
            adv_loc = st.text_input("Location")
            adv_role = st.text_input("Role")

        # Filtering logic
        results = {k: v for k, v in data.items() if 
                   (query.lower() in str(v.get('appellations')).lower()) and
                   (adv_loc.lower() in str(v.get('locationRelations')).lower()) and
                   (adv_role.lower() in str(v.get('activeAs')).lower())}

        if results:
            selection = st.selectbox("Select a person:", options=list(results.keys()),
                                    format_func=lambda x: f"{x} - {results[x]['appellations'][0]['appellation']}")
            
            if st.button("View Full Profile 👤"):
                st.session_state['selected_person_id'] = selection
                st.session_state['selected_person_data'] = results[selection]
                st.switch_page("pages/👤_Person_Details.py")
        else:
            st.info("No matches found.")

    with tab_stats:
        st.header("Global Overview")
        col1, col2 = st.columns(2)
        col1.metric("Total Records", len(data))
        col2.metric("Total Events", sum(len(v.get('events', [])) for v in data.values()))
        
else:
    st.error("data.json not found!")
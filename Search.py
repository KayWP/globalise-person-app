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

def get_primary_name(person_data):
    """Get the primary appellation for a person"""
    appellations = person_data.get('appellations', [])
    if appellations:
        return appellations[0].get('appellation', 'Unknown')
    return 'Unknown'

def search_in_field(field_list, search_term):
    """Search for a term within a list of dictionaries"""
    if not search_term:
        return True
    search_lower = search_term.lower()
    for item in field_list:
        if search_lower in str(item).lower():
            return True
    return False

data = load_data()

st.title("📜 VOC Historical Person Explorer")

if data:
    tab_search, tab_stats = st.tabs(["🔍 Search", "📊 Statistics"])

    with tab_search:
        query = st.text_input("Search by name...", placeholder="e.g. Johannes")
        
        with st.expander("🛠️ Advanced Search"):
            adv_loc = st.text_input("Location (e.g. Amsterdam, Cochin)")
            adv_role = st.text_input("Role (e.g. merchant, bookkeeper)")

        # Filtering logic
        results = {}
        for k, v in data.items():
            name_match = not query or query.lower() in str(v.get('appellations', '')).lower()
            loc_match = not adv_loc or search_in_field(v.get('locationRelations', []), adv_loc)
            role_match = not adv_role or search_in_field(v.get('activeAs', []), adv_role)
            
            if name_match and loc_match and role_match:
                results[k] = v

        if results:
            st.write(f"Found {len(results)} result(s)")
            
            # Create display options
            display_options = {k: f"{k} - {get_primary_name(v)}" for k, v in results.items()}
            
            selection = st.selectbox(
                "Select a person:", 
                options=list(results.keys()),
                format_func=lambda x: display_options[x]
            )
            
            # Show preview
            if selection:
                person = results[selection]
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Activities", len(person.get('activeAs', [])))
                with col2:
                    st.metric("Locations", len(person.get('locationRelations', [])))
                with col3:
                    st.metric("Events", len(person.get('events', [])))
            
            if st.button("View Full Profile 👤", type="primary"):
                st.session_state['selected_person_id'] = selection
                st.session_state['selected_person_data'] = results[selection]
                st.switch_page("pages/Person_Details.py")
        else:
            st.info("No matches found. Try different search terms.")

    with tab_stats:
        st.header("📊 Global Overview")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Clusters", len(data))
        
        total_events = sum(len(v.get('events', [])) for v in data.values())
        col2.metric("Total Events", total_events)
        
        total_activities = sum(len(v.get('activeAs', [])) for v in data.values())
        col3.metric("Total Activities", total_activities)
        
        # Activity distribution
        st.subheader("Most Common Roles")
        roles = {}
        for person in data.values():
            for activity in person.get('activeAs', []):
                role = activity.get('original_label', 'Unknown')
                roles[role] = roles.get(role, 0) + 1
        
        if roles:
            roles_df = pd.DataFrame(list(roles.items()), columns=['Role', 'Count'])
            roles_df = roles_df.sort_values('Count', ascending=False).head(10)
            st.bar_chart(roles_df.set_index('Role'))
        
else:
    st.error("data.json not found! Please ensure data.json is in the same directory as this script.")
    st.info("Your data.json should contain VOC person clusters with appellations, activeAs, locationRelations, events, etc.")

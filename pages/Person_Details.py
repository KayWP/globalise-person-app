import streamlit as st
import pandas as pd

st.set_page_config(page_title="Person Details", layout="wide")

# Check if a person was actually selected
if 'selected_person_data' not in st.session_state:
    st.warning("No person selected. Please go back to the Search page.")
    if st.button("⬅️ Back to Search"):
        st.switch_page("Search.py")
    st.stop()

person = st.session_state['selected_person_data']
pid = st.session_state['selected_person_id']

# Get primary name
primary_name = "Unknown"
if person.get('appellations'):
    primary_name = person['appellations'][0].get('appellation', 'Unknown')

st.title(f"👤 {primary_name}")
st.caption(f"Cluster ID: {pid}")

if st.button("⬅️ Back to Search"):
    st.switch_page("Search.py")

# --- Tabbed Details View ---
t1, t2, t3, t4, t5, t6 = st.tabs([
    "💼 Activities", 
    "🌍 Locations", 
    "📅 Events", 
    "👤 Appellations",
    "🆔 Identities",
    "🔗 References"
])

with t1:
    st.subheader("Professional Activities")
    activities = person.get('activeAs', [])
    
    if activities:
        # Create a clean dataframe
        activity_data = []
        for act in activities:
            activity_data.append({
                'Role': act.get('original_label', 'N/A'),
                'Employer': act.get('employer', 'N/A'),
                'Start Date': act.get('startDate', 'N/A'),
                'End Date': act.get('endDate', 'N/A'),
                'Annotation Date': act.get('annotationDate', 'N/A'),
                'Source': act.get('observation_source', 'N/A')
            })
        
        df = pd.DataFrame(activity_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Show detailed view in expander
        with st.expander("📋 View Raw Activity Data"):
            for i, act in enumerate(activities, 1):
                st.write(f"**Activity {i}:**")
                st.json(act)
    else:
        st.info("No activity data recorded.")

with t2:
    st.subheader("Location Relations")
    locations = person.get('locationRelations', [])
    
    if locations:
        for loc in locations:
            col1, col2 = st.columns([1, 3])
            with col1:
                st.write(f"**Type:** {loc.get('original_label', 'N/A')}")
            with col2:
                location_desc = loc.get('original_location_description', 'Unknown location')
                st.write(f"📍 **{location_desc.title()}**")
                if loc.get('annotationDate'):
                    st.caption(f"Annotated: {loc.get('annotationDate')}")
            st.divider()
    else:
        st.info("No location data recorded.")

with t3:
    st.subheader("Life Events")
    events = person.get('events', [])
    
    if events:
        for event in events:
            event_label = event.get('original_label', 'Unknown Event')
            event_date = event.get('startDate', 'Unknown date')
            location = event.get('original_location_description', 'Unknown location')
            
            st.write(f"### {event_label}")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Date:** {event_date}")
            with col2:
                st.write(f"**Location:** {location}")
            
            if event.get('observation_source'):
                st.caption(f"📚 Source: {event.get('observation_source')}")
            st.divider()
    else:
        st.info("No events recorded.")

with t4:
    st.subheader("Name Variations")
    appellations = person.get('appellations', [])
    
    if appellations:
        # Show all name variations
        names = {}
        for app in appellations:
            name = app.get('appellation', 'Unknown')
            date = app.get('annotationDate', 'Unknown date')
            if name not in names:
                names[name] = []
            names[name].append(date)
        
        for name, dates in names.items():
            st.write(f"**{name}**")
            st.caption(f"Recorded in: {', '.join(dates)}")
            st.divider()
        
        with st.expander("📋 View Raw Appellation Data"):
            st.json(appellations)
    else:
        st.info("No appellations recorded.")

with t5:
    st.subheader("Identity Information")
    identities = person.get('identities', [])
    
    if identities:
        for identity in identities:
            st.write(f"**{identity.get('original_label', 'N/A')}**")
            if identity.get('annotationDate'):
                st.caption(f"Annotated: {identity.get('annotationDate')}")
            st.divider()
        
        with st.expander("📋 View Raw Identity Data"):
            st.json(identities)
    else:
        st.info("No identity information recorded.")

with t6:
    st.subheader("External References")
    refs = person.get('externalReferences', [])
    
    if refs:
        for ref in refs:
            st.write(f"**Database:** {ref.get('external_db_name', 'N/A')}")
            st.write(f"**ID:** {ref.get('external_id', 'N/A')}")
            st.divider()
    else:
        st.info("No external references recorded.")
    
    # Also show persons in cluster
    persons = person.get('persons', [])
    if persons:
        st.subheader("Person IDs in Cluster")
        person_df = pd.DataFrame(persons)
        st.dataframe(person_df, use_container_width=True, hide_index=True)

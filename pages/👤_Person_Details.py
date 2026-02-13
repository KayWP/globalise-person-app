import streamlit as st
import pandas as pd

st.set_page_config(page_title="Person Details", layout="wide")

# Check if a person was actually selected
if 'selected_person_data' not in st.session_state:
    st.warning("No person selected. Please go back to the Search page.")
    if st.button("⬅️ Back to Search"):
        st.switch_page("main.py")
    st.stop()

person = st.session_state['selected_person_data']
pid = st.session_state['selected_person_id']

st.title(f"👤 {person['appellations'][0]['appellation']}")
st.caption(f"Cluster ID: {pid}")

if st.button("⬅️ Back to Search"):
    st.switch_page("main.py")

# --- Tabbed Details View ---
t1, t2, t3, t4 = st.tabs(["💼 Activities", "🌍 Locations", "📅 Events", "👥 Relations"])

with t1:
    if person.get('activeAs'):
        st.table(pd.DataFrame(person['activeAs'])[['original_label', 'startDate', 'endDate']])
    else:
        st.write("No activity data.")

with t2:
    for loc in person.get('locationRelations', []):
        st.write(f"📍 **{loc.get('original_label')}**: {loc.get('original_location_description')}")

with t3:
    for event in person.get('events', []):
        st.write(f"📅 **{event.get('original_label')}**: {event.get('startDate', 'N/A')}")

with t4:
    if person.get('relations'):
        st.json(person['relations'])
    else:
        st.write("No personal relations recorded.")
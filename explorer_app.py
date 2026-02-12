import streamlit as st
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(
    page_title="VOC Person Explorer",
    page_icon="📜",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

def load_json_data(uploaded_file):
    """Load JSON data from uploaded file"""
    try:
        data = json.load(uploaded_file)
        return data
    except Exception as e:
        st.error(f"Error loading JSON: {e}")
        return None

def display_person_details(data):
    """Display detailed view for individual persons"""
    # If data is a dict with cluster keys, let user select
    if isinstance(data, dict):
        cluster_keys = list(data.keys())
        
        if len(cluster_keys) == 1:
            selected_cluster = cluster_keys[0]
            cluster_data = data[selected_cluster]
        else:
            selected_cluster = st.selectbox(
                "Select person cluster to explore:",
                cluster_keys
            )
            cluster_data = data[selected_cluster]
        
        st.header(f"Cluster: {selected_cluster}")
        
        # Parse the data
        person_info = parse_person_data(cluster_data)
        
        # Overview metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Names", len(person_info['appellations']))
        with col2:
            st.metric("Activities", len(person_info['activeAs']))
        with col3:
            st.metric("Events", len(person_info['events']))
        with col4:
            st.metric("Relations", len(person_info['relations']))
        
        st.markdown("---")
        
        # Tabbed interface
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "👤 Names", 
            "💼 Activities", 
            "🌍 Locations", 
            "📅 Events",
            "👥 Relations",
            "🔍 Raw Data"
        ])
        
        with tab1:
            display_appellations(person_info['appellations'])
            display_identities(person_info['identities'])
        
        with tab2:
            display_activities(person_info['activeAs'])
        
        with tab3:
            display_locations(person_info['locationRelations'])
        
        with tab4:
            display_events(person_info['events'])
        
        with tab5:
            display_relations(person_info['relations'])
        
        with tab6:
            st.subheader("Raw JSON Data")
            st.json(cluster_data)

def parse_person_data(cluster_data: Dict) -> Dict:
    """Parse and organize person cluster data"""
    return {
        'persons': cluster_data.get('persons', []),
        'appellations': cluster_data.get('appellations', []),
        'activeAs': cluster_data.get('activeAs', []),
        'identities': cluster_data.get('identities', []),
        'locationRelations': cluster_data.get('locationRelations', []),
        'relations': cluster_data.get('relations', []),
        'events': cluster_data.get('events', []),
        'externalReferences': cluster_data.get('externalReferences', [])
    }

def display_appellations(appellations: List[Dict]):
    """Display person names/appellations"""
    st.subheader("📝 Names & Appellations")
    
    if not appellations:
        st.info("No appellations recorded")
        return
    
    df = pd.DataFrame(appellations)
    
    # Show unique names
    unique_names = df['appellation'].unique()
    st.write(f"**Known as:** {', '.join(unique_names)}")
    
    # Detailed table
    if st.checkbox("Show detailed appellations"):
        display_cols = ['appellation', 'annotationDate', 'observation_source']
        available_cols = [col for col in display_cols if col in df.columns]
        st.dataframe(df[available_cols], use_container_width=True)

def display_activities(activities: List[Dict]):
    """Display person's professional activities"""
    st.subheader("💼 Professional Activities")
    
    if not activities:
        st.info("No activities recorded")
        return
    
    df = pd.DataFrame(activities)
    
    # Timeline view
    for idx, activity in enumerate(activities):
        with st.expander(f"{activity.get('original_label', 'Activity')} ({activity.get('annotationDate', 'Unknown date')})"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Position:** {activity.get('original_label', 'N/A')}")
                st.write(f"**Employer:** {activity.get('employer', 'N/A')}")
                st.write(f"**Location:** {activity.get('location', 'N/A')}")
            
            with col2:
                st.write(f"**Start Date:** {activity.get('startDate', 'N/A')}")
                st.write(f"**End Date:** {activity.get('endDate', 'N/A')}")
                st.write(f"**Source:** {activity.get('observation_source', 'N/A')}")

def display_locations(location_relations: List[Dict]):
    """Display location relationships"""
    st.subheader("🌍 Location Relations")
    
    if not location_relations:
        st.info("No location relations recorded")
        return
    
    for loc in location_relations:
        label = loc.get('original_label', 'Unknown relation')
        location = loc.get('original_location_description', 'Unknown location')
        date = loc.get('annotationDate', 'Unknown date')
        
        st.write(f"**{label}:** {location} ({date})")

def display_events(events: List[Dict]):
    """Display life events"""
    st.subheader("📅 Life Events")
    
    if not events:
        st.info("No events recorded")
        return
    
    for event in events:
        event_type = event.get('original_label', 'Event')
        date = event.get('startDate') or event.get('annotationDate', 'Unknown date')
        location = event.get('original_location_description', 'Unknown location')
        
        st.write(f"**{event_type}:** {date} at {location}")

def display_relations(relations: List[Dict]):
    """Display personal relations"""
    st.subheader("👥 Personal Relations")
    
    if not relations:
        st.info("No relations recorded")
        return
    
    for rel in relations:
        relation_type = rel.get('relation', 'Unknown relation')
        other_person = rel.get('otherPerson', 'Unknown person')
        date = rel.get('annotationDate', 'Unknown date')
        
        st.write(f"**Relation:** {relation_type}")
        st.write(f"**Person:** {other_person}")
        st.write(f"**Date:** {date}")

def display_identities(identities: List[Dict]):
    """Display identity information"""
    st.subheader("🆔 Identity Information")
    
    if not identities:
        st.info("No identity information recorded")
        return
    
    for identity in identities:
        label = identity.get('original_label', 'Unknown')
        date = identity.get('annotationDate', 'Unknown date')
        st.write(f"**{label}** (recorded in {date})")

def main():
    st.title("📜 VOC Historical Person Explorer")
    st.markdown("Explore biographical data from VOC (Dutch East India Company) historical records")
    
    # Sidebar for file upload and navigation
    with st.sidebar:
        st.header("Data Input")
        uploaded_file = st.file_uploader("Upload JSON file", type=['json'])
        
        st.markdown("---")
        st.header("Navigation")
        page = st.radio(
            "Choose a page:",
            ["🔍 Search Persons", "👤 Person Details"],
            help="Search to find persons, then view individual details"
        )
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This app helps explore historical person records including:
        - Names and appellations
        - Professional activities
        - Location relations
        - Life events
        - Personal relations
        """)
    
    if uploaded_file is not None:
        data = load_json_data(uploaded_file)
        
        if data:
            # Import search functionality
            try:
                from search_page import search_page
                has_search = True
            except ImportError:
                has_search = False
                st.warning("Search page module not found. Only detail view available.")
            
            # Route to appropriate page
            if page == "🔍 Search Persons" and has_search:
                search_page(data)
            else:
                # Original person details view
                display_person_details(data)
    
    else:
        # Welcome screen
        st.info("👆 Please upload a JSON file to begin exploring")
        
        st.markdown("""
        ### Expected JSON Format
        
        The JSON should contain person cluster data with the following structure:
        - `persons`: List of person IDs
        - `appellations`: Names and titles
        - `activeAs`: Professional activities and positions
        - `identities`: Identity information (gender, etc.)
        - `locationRelations`: Geographic connections
        - `relations`: Personal relationships
        - `events`: Life events (birth, death, etc.)
        - `externalReferences`: Links to external databases
        """)

if __name__ == "__main__":
    main()

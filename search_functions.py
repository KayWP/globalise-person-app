import streamlit as st
import json
import pandas as pd
from typing import Dict, List, Any, Tuple
import re

def load_multiple_persons(data: Dict) -> List[Tuple[str, Dict]]:
    """Extract all person clusters from the data"""
    persons = []
    
    # Handle both single cluster and multiple clusters
    if isinstance(data, dict):
        # Check if this is a single cluster or a collection
        if 'persons' in data and 'appellations' in data:
            # Single cluster
            persons.append(('single_cluster', data))
        else:
            # Multiple clusters
            for cluster_id, cluster_data in data.items():
                if isinstance(cluster_data, dict) and 'persons' in cluster_data:
                    persons.append((cluster_id, cluster_data))
    
    return persons

def extract_searchable_data(cluster_id: str, cluster_data: Dict) -> Dict:
    """Extract searchable information from a person cluster"""
    # Get all names
    names = []
    for app in cluster_data.get('appellations', []):
        if app.get('appellation'):
            names.append(app['appellation'].lower())
    
    # Get all activities/positions
    activities = []
    for act in cluster_data.get('activeAs', []):
        if act.get('original_label'):
            activities.append(act['original_label'].lower())
    
    # Get all locations
    locations = []
    for loc in cluster_data.get('locationRelations', []):
        if loc.get('original_location_description'):
            locations.append(loc['original_location_description'].lower())
    
    # Get employers
    employers = []
    for act in cluster_data.get('activeAs', []):
        if act.get('employer'):
            employers.append(act['employer'].lower())
    
    # Get dates
    dates = []
    for app in cluster_data.get('appellations', []):
        if app.get('annotationDate'):
            dates.append(app['annotationDate'])
    for act in cluster_data.get('activeAs', []):
        if act.get('annotationDate'):
            dates.append(act['annotationDate'])
        if act.get('startDate'):
            dates.append(act['startDate'])
    
    # Get events
    events = []
    for event in cluster_data.get('events', []):
        if event.get('original_label'):
            events.append(event['original_label'].lower())
    
    # Get gender
    gender = None
    for identity in cluster_data.get('identities', []):
        if identity.get('original_label'):
            gender = identity['original_label']
            break
    
    return {
        'cluster_id': cluster_id,
        'names': list(set(names)),
        'activities': list(set(activities)),
        'locations': list(set(locations)),
        'employers': list(set(employers)),
        'dates': list(set(dates)),
        'events': list(set(events)),
        'gender': gender,
        'raw_data': cluster_data
    }

def search_persons(persons_data: List[Dict], 
                   name_query: str = None,
                   location_query: str = None,
                   activity_query: str = None,
                   employer_query: str = None,
                   date_from: str = None,
                   date_to: str = None,
                   gender_filter: str = None) -> List[Dict]:
    """Search through person records based on various criteria"""
    results = []
    
    for person in persons_data:
        match = True
        
        # Name search
        if name_query:
            name_match = any(name_query.lower() in name for name in person['names'])
            if not name_match:
                match = False
        
        # Location search
        if location_query and match:
            location_match = any(location_query.lower() in loc for loc in person['locations'])
            if not location_match:
                match = False
        
        # Activity search
        if activity_query and match:
            activity_match = any(activity_query.lower() in act for act in person['activities'])
            if not activity_match:
                match = False
        
        # Employer search
        if employer_query and match:
            employer_match = any(employer_query.lower() in emp for emp in person['employers'])
            if not employer_match:
                match = False
        
        # Date range filter
        if (date_from or date_to) and match:
            person_dates = []
            for date_str in person['dates']:
                if date_str:
                    # Extract year from date string
                    year_match = re.search(r'\d{4}', str(date_str))
                    if year_match:
                        person_dates.append(int(year_match.group()))
            
            if person_dates:
                min_date = min(person_dates)
                max_date = max(person_dates)
                
                if date_from and max_date < int(date_from):
                    match = False
                if date_to and min_date > int(date_to):
                    match = False
            elif date_from or date_to:
                # If we're filtering by date but person has no dates, exclude them
                match = False
        
        # Gender filter
        if gender_filter and gender_filter != "All" and match:
            if person['gender'] != gender_filter.lower():
                match = False
        
        if match:
            results.append(person)
    
    return results

def display_search_results(results: List[Dict]):
    """Display search results in a formatted way"""
    if not results:
        st.info("No persons found matching your criteria. Try adjusting your search filters.")
        return
    
    st.success(f"Found {len(results)} person(s)")
    
    for idx, person in enumerate(results):
        with st.expander(f"👤 {person['names'][0] if person['names'] else 'Unknown'} ({person['cluster_id']})", expanded=(idx < 3)):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Names:**")
                for name in person['names'][:5]:  # Show first 5 names
                    st.write(f"- {name.title()}")
                if len(person['names']) > 5:
                    st.write(f"... and {len(person['names']) - 5} more")
                
                st.markdown("**Locations:**")
                for loc in person['locations'][:3]:
                    st.write(f"- {loc.title()}")
                if len(person['locations']) > 3:
                    st.write(f"... and {len(person['locations']) - 3} more")
            
            with col2:
                st.markdown("**Activities/Positions:**")
                for act in person['activities'][:3]:
                    st.write(f"- {act.title()}")
                if len(person['activities']) > 3:
                    st.write(f"... and {len(person['activities']) - 3} more")
                
                if person['gender']:
                    st.markdown(f"**Gender:** {person['gender'].title()}")
                
                if person['dates']:
                    years = [int(re.search(r'\d{4}', str(d)).group()) 
                            for d in person['dates'] 
                            if d and re.search(r'\d{4}', str(d))]
                    if years:
                        st.markdown(f"**Date Range:** {min(years)} - {max(years)}")
            
            # Add button to view full details
            if st.button(f"View Full Details", key=f"view_{person['cluster_id']}"):
                st.session_state['selected_person'] = person['cluster_id']
                st.session_state['selected_data'] = person['raw_data']

def create_summary_statistics(persons_data: List[Dict]):
    """Create summary statistics for the dataset"""
    st.subheader("📊 Dataset Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Persons", len(persons_data))
    
    with col2:
        total_activities = sum(len(p['activities']) for p in persons_data)
        st.metric("Total Activities", total_activities)
    
    with col3:
        unique_locations = set()
        for p in persons_data:
            unique_locations.update(p['locations'])
        st.metric("Unique Locations", len(unique_locations))
    
    with col4:
        # Count persons with dates
        persons_with_dates = sum(1 for p in persons_data if p['dates'])
        st.metric("Records with Dates", persons_with_dates)
    
    # Most common activities
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Most Common Activities:**")
        all_activities = []
        for p in persons_data:
            all_activities.extend(p['activities'])
        
        if all_activities:
            activity_counts = pd.Series(all_activities).value_counts().head(10)
            for activity, count in activity_counts.items():
                st.write(f"- {activity.title()}: {count}")
    
    with col2:
        st.markdown("**Most Common Locations:**")
        all_locations = []
        for p in persons_data:
            all_locations.extend(p['locations'])
        
        if all_locations:
            location_counts = pd.Series(all_locations).value_counts().head(10)
            for location, count in location_counts.items():
                st.write(f"- {location.title()}: {count}")

def search_page(data: Dict):
    """Main search page"""
    st.title("🔍 Person Search & Discovery")
    st.markdown("Search through VOC historical person records using various filters")
    
    # Load all persons
    persons_list = load_multiple_persons(data)
    
    if not persons_list:
        st.error("No person data found in the uploaded file.")
        return
    
    # Extract searchable data
    persons_data = [extract_searchable_data(cluster_id, cluster_data) 
                    for cluster_id, cluster_data in persons_list]
    
    st.info(f"Loaded {len(persons_data)} person record(s)")
    
    # Create tabs
    tab1, tab2 = st.tabs(["🔎 Search", "📊 Statistics"])
    
    with tab1:
        st.subheader("Search Filters")
        
        # Search form
        col1, col2 = st.columns(2)
        
        with col1:
            name_query = st.text_input(
                "Name (partial match)",
                placeholder="e.g., abraham, goosen...",
                help="Search by any part of the person's name"
            )
            
            location_query = st.text_input(
                "Location (partial match)",
                placeholder="e.g., cochin, gouda...",
                help="Search by place of origin, residence, or work location"
            )
            
            activity_query = st.text_input(
                "Activity/Position (partial match)",
                placeholder="e.g., boekhouder, corporal...",
                help="Search by job title or activity"
            )
        
        with col2:
            employer_query = st.text_input(
                "Employer (partial match)",
                placeholder="e.g., voc, mallabaar...",
                help="Search by employer name"
            )
            
            col2a, col2b = st.columns(2)
            with col2a:
                date_from = st.text_input(
                    "Date From (year)",
                    placeholder="e.g., 1700",
                    help="Filter persons active from this year onwards"
                )
            
            with col2b:
                date_to = st.text_input(
                    "Date To (year)",
                    placeholder="e.g., 1800",
                    help="Filter persons active up to this year"
                )
            
            gender_filter = st.selectbox(
                "Gender",
                ["All", "Male", "Female"],
                help="Filter by recorded gender"
            )
        
        # Search button
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            search_button = st.button("🔍 Search", type="primary", use_container_width=True)
        with col2:
            clear_button = st.button("Clear Filters", use_container_width=True)
        
        if clear_button:
            st.rerun()
        
        # Perform search
        if search_button or any([name_query, location_query, activity_query, employer_query, date_from, date_to, gender_filter != "All"]):
            st.markdown("---")
            st.subheader("Search Results")
            
            results = search_persons(
                persons_data,
                name_query=name_query if name_query else None,
                location_query=location_query if location_query else None,
                activity_query=activity_query if activity_query else None,
                employer_query=employer_query if employer_query else None,
                date_from=date_from if date_from else None,
                date_to=date_to if date_to else None,
                gender_filter=gender_filter if gender_filter != "All" else None
            )
            
            display_search_results(results)
        else:
            st.info("👆 Enter search criteria above and click 'Search' to find persons")
            
            # Show a few example persons
            st.markdown("---")
            st.subheader("Recent Records (showing first 5)")
            display_search_results(persons_data[:5])
    
    with tab2:
        create_summary_statistics(persons_data)

# This allows the search page to be imported and used in the main app
if __name__ == "__main__":
    st.set_page_config(page_title="Person Search", page_icon="🔍", layout="wide")
    
    uploaded_file = st.file_uploader("Upload JSON file", type=['json'])
    
    if uploaded_file:
        data = json.load(uploaded_file)
        search_page(data)
    else:
        st.info("Please upload a JSON file to begin searching")

import streamlit as st
import pandas as pd
from typing import Dict, List, Any
from collections import defaultdict
import re

def extract_year_from_date(date_str):
    """Extract year from various date formats"""
    if not date_str or date_str == "":
        return None
    
    # Try to extract 4-digit year
    year_match = re.search(r'\b(\d{4})\b', str(date_str))
    if year_match:
        return int(year_match.group(1))
    return None

def group_by_observation(cluster_data: Dict) -> Dict[str, Dict]:
    """Group all data by observation_id to create timeline entries"""
    observations = defaultdict(lambda: {
        'observation_id': '',
        'date': None,
        'year': None,
        'source': '',
        'location_in_source': '',
        'appellations': [],
        'activities': [],
        'identities': [],
        'locations': [],
        'relations': [],
        'events': []
    })
    
    # Process appellations
    for app in cluster_data.get('appellations', []):
        obs_id = app.get('observation_id', 'unknown')
        obs = observations[obs_id]
        obs['observation_id'] = obs_id
        obs['date'] = app.get('annotationDate')
        obs['year'] = extract_year_from_date(app.get('annotationDate'))
        obs['source'] = app.get('observation_source', '')
        obs['location_in_source'] = app.get('location_in_observation_source', '')
        obs['appellations'].append(app)
    
    # Process activities
    for act in cluster_data.get('activeAs', []):
        obs_id = act.get('observation_id', 'unknown')
        obs = observations[obs_id]
        obs['observation_id'] = obs_id
        if not obs['date']:
            obs['date'] = act.get('annotationDate')
            obs['year'] = extract_year_from_date(act.get('annotationDate'))
        obs['source'] = act.get('observation_source', '')
        obs['location_in_source'] = act.get('location_in_observation_source', '')
        obs['activities'].append(act)
    
    # Process identities
    for ident in cluster_data.get('identities', []):
        obs_id = ident.get('observation_id', 'unknown')
        obs = observations[obs_id]
        obs['observation_id'] = obs_id
        if not obs['date']:
            obs['date'] = ident.get('annotationDate')
            obs['year'] = extract_year_from_date(ident.get('annotationDate'))
        obs['source'] = ident.get('observation_source', '')
        obs['location_in_source'] = ident.get('location_in_observation_source', '')
        obs['identities'].append(ident)
    
    # Process location relations
    for loc in cluster_data.get('locationRelations', []):
        obs_id = loc.get('observation_id', 'unknown')
        obs = observations[obs_id]
        obs['observation_id'] = obs_id
        if not obs['date']:
            obs['date'] = loc.get('annotationDate')
            obs['year'] = extract_year_from_date(loc.get('annotationDate'))
        obs['source'] = loc.get('observation_source', '')
        obs['location_in_source'] = loc.get('location_in_observation_source', '')
        obs['locations'].append(loc)
    
    # Process relations
    for rel in cluster_data.get('relations', []):
        obs_id = rel.get('observation_id', 'unknown')
        obs = observations[obs_id]
        obs['observation_id'] = obs_id
        if not obs['date']:
            obs['date'] = rel.get('annotationDate')
            obs['year'] = extract_year_from_date(rel.get('annotationDate'))
        obs['source'] = rel.get('observation_source', '')
        obs['location_in_source'] = rel.get('location_in_observation_source', '')
        obs['relations'].append(rel)
    
    # Process events
    for event in cluster_data.get('events', []):
        obs_id = event.get('observation_id', 'unknown')
        obs = observations[obs_id]
        obs['observation_id'] = obs_id
        if not obs['date']:
            obs['date'] = event.get('annotationDate')
            obs['year'] = extract_year_from_date(event.get('annotationDate'))
        obs['source'] = event.get('observation_source', '')
        obs['location_in_source'] = event.get('location_in_observation_source', '')
        obs['events'].append(event)
    
    return dict(observations)

def sort_observations(observations: Dict) -> List[tuple]:
    """Sort observations by year/date"""
    obs_list = list(observations.items())
    
    # Sort by year (None values go to end)
    def sort_key(item):
        obs_id, obs_data = item
        year = obs_data.get('year')
        if year is None:
            return (9999, obs_id)  # Put undated at end
        return (year, obs_id)
    
    return sorted(obs_list, key=sort_key)

def display_timeline_entry(obs_id: str, obs_data: Dict, index: int):
    """Display a single timeline entry"""
    
    # Determine if this should be expanded by default (first 3 entries)
    expanded = index < 3
    
    # Create title with date and observation ID
    year = obs_data.get('year')
    date_display = str(year) if year else "Date Unknown"
    title = f"📅 {date_display} - {obs_id}"
    
    with st.expander(title, expanded=expanded):
        # Show source information
        st.markdown("### 📚 Source Information")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Observation ID:** {obs_id}")
            st.write(f"**Date:** {obs_data.get('date', 'N/A')}")
        
        with col2:
            source = obs_data.get('source', 'N/A')
            # Truncate very long sources
            if len(source) > 100:
                source = source[:100] + "..."
            st.write(f"**Source:** {source}")
            st.write(f"**Page/Location:** {obs_data.get('location_in_source', 'N/A')}")
        
        st.markdown("---")
        
        # Create columns for different data types
        has_data = False
        
        # Names/Appellations
        if obs_data['appellations']:
            has_data = True
            st.markdown("#### 📝 Names Recorded")
            for app in obs_data['appellations']:
                name = app.get('appellation', 'Unknown')
                app_type = app.get('appellationType', '').split('/')[-1]
                st.write(f"- **{name}** ({app_type})")
        
        # Activities
        if obs_data['activities']:
            has_data = True
            st.markdown("#### 💼 Activities/Positions")
            for act in obs_data['activities']:
                position = act.get('original_label', 'Unknown position')
                employer = act.get('employer', 'N/A')
                location = act.get('location', act.get('original_location_description', 'N/A'))
                start = act.get('startDate', 'N/A')
                end = act.get('endDate', 'Ongoing' if act.get('endDate') == '' else 'N/A')
                
                st.write(f"**{position}**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"Employer: {employer}")
                with col2:
                    st.write(f"Location: {location}")
                with col3:
                    st.write(f"Period: {start} - {end}")
                st.write("")
        
        # Identity
        if obs_data['identities']:
            has_data = True
            st.markdown("#### 🆔 Identity Information")
            for ident in obs_data['identities']:
                label = ident.get('original_label', 'Unknown')
                st.write(f"- {label}")
        
        # Locations
        if obs_data['locations']:
            has_data = True
            st.markdown("#### 🌍 Location Relations")
            for loc in obs_data['locations']:
                rel_type = loc.get('original_label', 'Unknown relation')
                location = loc.get('original_location_description', 'Unknown location')
                st.write(f"- **{rel_type}:** {location}")
        
        # Relations
        if obs_data['relations']:
            has_data = True
            st.markdown("#### 👥 Personal Relations")
            for rel in obs_data['relations']:
                rel_type = rel.get('relation', 'Unknown relation').split('#')[-1]
                other = rel.get('otherPerson', 'Unknown person')
                st.write(f"- **{rel_type}:** {other}")
        
        # Events
        if obs_data['events']:
            has_data = True
            st.markdown("#### 📅 Life Events")
            for event in obs_data['events']:
                event_label = event.get('original_label', 'Event')
                event_date = event.get('startDate', event.get('annotationDate', 'N/A'))
                event_location = event.get('original_location_description', 'N/A')
                st.write(f"- **{event_label}** on {event_date} at {event_location}")
        
        if not has_data:
            st.info("No detailed information recorded in this observation")

def display_timeline(cluster_data: Dict):
    """Main function to display the timeline view"""
    st.subheader("📅 Timeline View")
    st.markdown("All information about this person grouped by observation/source")
    
    # Group data by observation
    observations = group_by_observation(cluster_data)
    
    if not observations:
        st.info("No observations found for this person")
        return
    
    # Sort observations chronologically
    sorted_obs = sort_observations(observations)
    
    # Display summary
    total_obs = len(observations)
    dated_obs = sum(1 for _, obs in sorted_obs if obs.get('year') is not None)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Observations", total_obs)
    with col2:
        st.metric("Dated Observations", dated_obs)
    with col3:
        if dated_obs > 0:
            years = [obs.get('year') for _, obs in sorted_obs if obs.get('year') is not None]
            year_range = f"{min(years)} - {max(years)}"
            st.metric("Year Range", year_range)
        else:
            st.metric("Year Range", "N/A")
    
    st.markdown("---")
    
    # Display timeline entries
    for index, (obs_id, obs_data) in enumerate(sorted_obs):
        display_timeline_entry(obs_id, obs_data, index)

# This can be imported by the main app
if __name__ == "__main__":
    st.set_page_config(page_title="Timeline View", page_icon="📅", layout="wide")
    st.title("Timeline View Test")
    st.info("This module is meant to be imported by explorer_app.py")

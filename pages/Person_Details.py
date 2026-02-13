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
enrichment_data = st.session_state.get('enrichment_data', {'locations': {}, 'poolparty': {}})

def get_enriched_label(uri, fallback=''):
    """Get enriched label for a URI"""
    # Check if it's a location URI
    location_data = enrichment_data['locations'].get(uri.lower())
    if location_data:
        return location_data.get('label', fallback)
    
    # Check if it's a poolparty URI
    poolparty_data = enrichment_data['poolparty'].get(uri)
    if poolparty_data:
        label = poolparty_data.get('label')
        return label if label else fallback
    
    return fallback

def get_definition(uri):
    """Get definition for a poolparty URI"""
    poolparty_data = enrichment_data['poolparty'].get(uri)
    if poolparty_data:
        return poolparty_data.get('definition')
    return None

def get_location_coords(uri):
    """Get coordinates for a location URI"""
    location_data = enrichment_data['locations'].get(uri.lower())
    if location_data:
        lat = location_data.get('latitude')
        lng = location_data.get('longitude')
        if lat and lng:
            return (lat, lng)
    return None

# Get primary name
primary_name = "Unknown"
if person.get('appellations'):
    primary_name = person['appellations'][0].get('appellation', 'Unknown')

st.title(f"👤 {primary_name}")
st.caption(f"Cluster ID: {pid}")

if st.button("⬅️ Back to Search"):
    st.switch_page("Search.py")

# --- Tabbed Details View ---
t0, t1, t2, t3, t4, t5, t6 = st.tabs([
    "📅 Timeline",
    "💼 Activities", 
    "🌍 Locations", 
    "📅 Events", 
    "👤 Appellations",
    "🆔 Identities",
    "🔗 References"
])

with t0:
    st.subheader("📅 Chronological Timeline")
    st.caption("All observations grouped by source and date")
    
    # Collect all observations
    observations = {}
    
    # Process activities
    for activity in person.get('activeAs', []):
        obs_id = activity.get('observation_id')
        if obs_id:
            if obs_id not in observations:
                observations[obs_id] = {
                    'observation_id': obs_id,
                    'dates': set(),
                    'source': activity.get('observation_source', 'N/A'),
                    'reconstruction_source': activity.get('reconstruction_source', 'N/A'),
                    'activities': [],
                    'appellations': [],
                    'identities': [],
                    'locations': [],
                    'events': []
                }
            observations[obs_id]['activities'].append(activity)
            if activity.get('annotationDate'):
                observations[obs_id]['dates'].add(activity.get('annotationDate'))
            if activity.get('startDate'):
                observations[obs_id]['dates'].add(activity.get('startDate'))
    
    # Process appellations
    for appellation in person.get('appellations', []):
        obs_id = appellation.get('observation_id')
        if obs_id:
            if obs_id not in observations:
                observations[obs_id] = {
                    'observation_id': obs_id,
                    'dates': set(),
                    'source': appellation.get('observation_source', 'N/A'),
                    'reconstruction_source': appellation.get('reconstruction_source', 'N/A'),
                    'activities': [],
                    'appellations': [],
                    'identities': [],
                    'locations': [],
                    'events': []
                }
            observations[obs_id]['appellations'].append(appellation)
            if appellation.get('annotationDate'):
                observations[obs_id]['dates'].add(appellation.get('annotationDate'))
    
    # Process identities
    for identity in person.get('identities', []):
        obs_id = identity.get('observation_id')
        if obs_id:
            if obs_id not in observations:
                observations[obs_id] = {
                    'observation_id': obs_id,
                    'dates': set(),
                    'source': identity.get('observation_source', 'N/A'),
                    'reconstruction_source': identity.get('reconstruction_source', 'N/A'),
                    'activities': [],
                    'appellations': [],
                    'identities': [],
                    'locations': [],
                    'events': []
                }
            observations[obs_id]['identities'].append(identity)
            if identity.get('annotationDate'):
                observations[obs_id]['dates'].add(identity.get('annotationDate'))
    
    # Process location relations
    for location in person.get('locationRelations', []):
        obs_id = location.get('observation_id')
        if obs_id:
            if obs_id not in observations:
                observations[obs_id] = {
                    'observation_id': obs_id,
                    'dates': set(),
                    'source': location.get('observation_source', 'N/A'),
                    'reconstruction_source': location.get('reconstruction_source', 'N/A'),
                    'activities': [],
                    'appellations': [],
                    'identities': [],
                    'locations': [],
                    'events': []
                }
            observations[obs_id]['locations'].append(location)
            if location.get('annotationDate'):
                observations[obs_id]['dates'].add(location.get('annotationDate'))
    
    # Process events
    for event in person.get('events', []):
        obs_id = event.get('observation_id')
        if obs_id:
            if obs_id not in observations:
                observations[obs_id] = {
                    'observation_id': obs_id,
                    'dates': set(),
                    'source': event.get('observation_source', 'N/A'),
                    'reconstruction_source': event.get('reconstruction_source', 'N/A'),
                    'activities': [],
                    'appellations': [],
                    'identities': [],
                    'locations': [],
                    'events': []
                }
            observations[obs_id]['events'].append(event)
            if event.get('annotationDate'):
                observations[obs_id]['dates'].add(event.get('annotationDate'))
            if event.get('startDate'):
                observations[obs_id]['dates'].add(event.get('startDate'))
    
    if not observations:
        st.info("No observations with observation IDs found.")
    else:
        # Convert dates to sortable format and sort observations
        obs_list = []
        for obs_id, obs_data in observations.items():
            # Get the earliest date for sorting
            dates = obs_data['dates']
            if dates:
                # Convert dates to sortable strings (handle various formats)
                date_strings = sorted([str(d) for d in dates if d])
                earliest_date = date_strings[0] if date_strings else 'Unknown'
                obs_data['sort_date'] = earliest_date
                obs_data['display_dates'] = ', '.join(date_strings)
            else:
                obs_data['sort_date'] = 'Unknown'
                obs_data['display_dates'] = 'No date'
            obs_list.append(obs_data)
        
        # Sort by date (chronologically)
        obs_list.sort(key=lambda x: x['sort_date'])
        
        # Display timeline
        for i, obs in enumerate(obs_list):
            # Create a container for each observation
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"### 📍 {obs['observation_id']}")
                    st.markdown(f"**Date(s):** {obs['display_dates']}")
                
                with col2:
                    st.metric("Items", 
                             len(obs['activities']) + len(obs['appellations']) + 
                             len(obs['identities']) + len(obs['locations']) + len(obs['events']))
                
                # Display source information
                with st.expander("ℹ️ Source Information", expanded=False):
                    st.write(f"**Observation Source:** {obs['source']}")
                    st.write(f"**Reconstruction Source:** {obs['reconstruction_source']}")
                
                # Display content by category
                if obs['appellations']:
                    st.markdown("**👤 Names in this observation:**")
                    for app in obs['appellations']:
                        name = app.get('appellation', 'Unknown')
                        type_uri = app.get('appellationType', '')
                        enriched_type = get_enriched_label(type_uri, 'name')
                        st.write(f"• {name} ({enriched_type})")
                
                if obs['activities']:
                    st.markdown("**💼 Activities/Roles:**")
                    for act in obs['activities']:
                        original_label = act.get('original_label', 'N/A')
                        enriched_label = get_enriched_label(act.get('activity', ''), original_label)
                        employer = act.get('employer', '')
                        
                        display_text = f"• {enriched_label}"
                        if employer:
                            display_text += f" (employer: {employer})"
                        if act.get('startDate') or act.get('endDate'):
                            dates = []
                            if act.get('startDate'):
                                dates.append(f"from {act['startDate']}")
                            if act.get('endDate'):
                                dates.append(f"to {act['endDate']}")
                            display_text += f" [{' '.join(dates)}]"
                        
                        st.write(display_text)
                
                if obs['identities']:
                    st.markdown("**🆔 Identities:**")
                    for identity in obs['identities']:
                        original_label = identity.get('original_label', 'N/A')
                        enriched_label = get_enriched_label(identity.get('identity', ''), original_label)
                        st.write(f"• {enriched_label}")
                
                if obs['locations']:
                    st.markdown("**🌍 Locations:**")
                    for loc in obs['locations']:
                        relation_uri = loc.get('locationRelation', '')
                        enriched_relation = get_enriched_label(relation_uri, loc.get('original_label', 'N/A'))
                        
                        location_uri = loc.get('location', '')
                        original_desc = loc.get('original_location_description', 'Unknown')
                        enriched_location = get_enriched_label(location_uri, '')
                        if not enriched_location and original_desc:
                            enriched_location = get_enriched_label(original_desc.upper(), enrichment_data, original_desc)
                        
                        st.write(f"• {enriched_relation}: {enriched_location}")
                
                if obs['events']:
                    st.markdown("**📅 Events:**")
                    for event in obs['events']:
                        original_label = event.get('original_label', 'Unknown Event')
                        enriched_label = get_enriched_label(event.get('event', ''), original_label)
                        
                        location_uri = event.get('location', '')
                        original_location = event.get('original_location_description', '')
                        enriched_location = get_enriched_label(location_uri, '')
                        if not enriched_location and original_location:
                            enriched_location = get_enriched_label(original_location.upper(), enrichment_data, original_location)
                        
                        display_text = f"• {enriched_label}"
                        if enriched_location:
                            display_text += f" at {enriched_location}"
                        if event.get('startDate'):
                            display_text += f" [{event['startDate']}]"
                        
                        st.write(display_text)
                
                # Add a divider between observations
                if i < len(obs_list) - 1:
                    st.divider()


with t1:
    st.subheader("Professional Activities")
    activities = person.get('activeAs', [])
    
    if activities:
        # Create a clean dataframe with enriched data
        activity_data = []
        for act in activities:
            original_label = act.get('original_label', 'N/A')
            activity_uri = act.get('activity', '')
            activity_type_uri = act.get('activityType', '')
            
            # Get enriched labels
            enriched_activity = get_enriched_label(activity_uri, original_label)
            enriched_type = get_enriched_label(activity_type_uri, '')
            
            activity_data.append({
                'Original Role': original_label,
                'Standardized Role': enriched_activity if enriched_activity != original_label else '—',
                'Activity Type': enriched_type if enriched_type else 'N/A',
                'Employer': act.get('employer', 'N/A'),
                'Start Date': act.get('startDate', 'N/A'),
                'End Date': act.get('endDate', 'N/A'),
                'Annotation Date': act.get('annotationDate', 'N/A'),
                'Source': act.get('observation_source', 'N/A')
            })
        
        df = pd.DataFrame(activity_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Show detailed view with definitions
        with st.expander("📖 View Activity Definitions"):
            for i, act in enumerate(activities, 1):
                st.write(f"### Activity {i}")
                
                original_label = act.get('original_label', 'N/A')
                activity_uri = act.get('activity', '')
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Original Label:**")
                    st.write(original_label)
                    
                    enriched_label = get_enriched_label(activity_uri, '')
                    if enriched_label and enriched_label != original_label:
                        st.write("**Standardized Label:**")
                        st.write(f"_{enriched_label}_")
                
                with col2:
                    st.write("**Activity URI:**")
                    st.caption(activity_uri if activity_uri else "N/A")
                
                # Show definition if available
                definition = get_definition(activity_uri)
                if definition:
                    st.write("**Definition:**")
                    st.info(definition)
                
                st.divider()
        
        # Show raw data
        with st.expander("🔍 View Raw Activity Data"):
            for i, act in enumerate(activities, 1):
                st.write(f"**Activity {i}:**")
                st.json(act)
    else:
        st.info("No activity data recorded.")

with t2:
    st.subheader("Location Relations")
    locations = person.get('locationRelations', [])
    
    if locations:
        # Create location data with enrichment
        location_data = []
        map_data = []
        
        for loc in locations:
            original_desc = loc.get('original_location_description', 'Unknown')
            location_uri = loc.get('location', '')
            relation_uri = loc.get('locationRelation', '')
            
            # Get enriched labels
            enriched_location = get_enriched_label(location_uri, '')
            if not enriched_location and original_desc:
                enriched_location = get_enriched_label(original_desc.upper(), enrichment_data, '')
            
            enriched_relation = get_enriched_label(relation_uri, loc.get('original_label', 'N/A'))
            
            location_data.append({
                'Relation Type': enriched_relation,
                'Original Location': original_desc,
                'Standardized Location': enriched_location if enriched_location else '—',
                'Annotation Date': loc.get('annotationDate', 'N/A')
            })
            
            # Get coordinates for map
            coords = get_location_coords(location_uri)
            if not coords and original_desc:
                coords = get_location_coords(original_desc.upper())
            
            if coords:
                map_data.append({
                    'lat': coords[0],
                    'lon': coords[1],
                    'location': enriched_location if enriched_location else original_desc
                })
        
        # Display table
        df = pd.DataFrame(location_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Display map if we have coordinates
        if map_data:
            st.subheader("📍 Location Map")
            map_df = pd.DataFrame(map_data)
            st.map(map_df, latitude='lat', longitude='lon')
        
        # Show detailed view
        with st.expander("🔍 View Raw Location Data"):
            for i, loc in enumerate(locations, 1):
                st.write(f"**Location {i}:**")
                st.json(loc)
    else:
        st.info("No location data recorded.")

with t3:
    st.subheader("Life Events")
    events = person.get('events', [])
    
    if events:
        event_data = []
        
        for event in events:
            original_label = event.get('original_label', 'Unknown Event')
            event_uri = event.get('event', '')
            location_uri = event.get('location', '')
            original_location = event.get('original_location_description', 'Unknown')
            
            # Get enriched labels
            enriched_event = get_enriched_label(event_uri, original_label)
            enriched_location = get_enriched_label(location_uri, '')
            if not enriched_location and original_location:
                enriched_location = get_enriched_label(original_location.upper(), enrichment_data, original_location)
            
            event_data.append({
                'Event': enriched_event if enriched_event != original_label else original_label,
                'Original Location': original_location,
                'Standardized Location': enriched_location if enriched_location and enriched_location != original_location else '—',
                'Date': event.get('startDate', 'Unknown date'),
                'Source': event.get('observation_source', 'N/A')
            })
        
        df = pd.DataFrame(event_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Show detailed view
        with st.expander("🔍 View Raw Event Data"):
            for i, event in enumerate(events, 1):
                st.write(f"**Event {i}:**")
                st.json(event)
    else:
        st.info("No events recorded.")

with t4:
    st.subheader("Name Variations")
    appellations = person.get('appellations', [])
    
    if appellations:
        # Show all name variations
        appellation_data = []
        
        for app in appellations:
            name = app.get('appellation', 'Unknown')
            date = app.get('annotationDate', 'Unknown date')
            type_uri = app.get('appellationType', '')
            
            enriched_type = get_enriched_label(type_uri, 'N/A')
            
            appellation_data.append({
                'Name': name,
                'Type': enriched_type,
                'Annotation Date': date,
                'Source': app.get('observation_source', 'N/A')
            })
        
        df = pd.DataFrame(appellation_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        with st.expander("🔍 View Raw Appellation Data"):
            st.json(appellations)
    else:
        st.info("No appellations recorded.")

with t5:
    st.subheader("Identity Information")
    identities = person.get('identities', [])
    
    if identities:
        identity_data = []
        
        for identity in identities:
            original_label = identity.get('original_label', 'N/A')
            identity_uri = identity.get('identity', '')
            identity_type_uri = identity.get('identityType', '')
            
            # Get enriched labels
            enriched_identity = get_enriched_label(identity_uri, original_label)
            enriched_type = get_enriched_label(identity_type_uri, 'N/A')
            
            identity_data.append({
                'Original Label': original_label,
                'Standardized Label': enriched_identity if enriched_identity != original_label else '—',
                'Identity Type': enriched_type,
                'Annotation Date': identity.get('annotationDate', 'N/A')
            })
        
        df = pd.DataFrame(identity_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Show definitions
        with st.expander("📖 View Identity Definitions"):
            for i, identity in enumerate(identities, 1):
                st.write(f"### Identity {i}")
                
                original_label = identity.get('original_label', 'N/A')
                identity_uri = identity.get('identity', '')
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Original Label:**")
                    st.write(original_label)
                    
                    enriched_label = get_enriched_label(identity_uri, '')
                    if enriched_label and enriched_label != original_label:
                        st.write("**Standardized Label:**")
                        st.write(f"_{enriched_label}_")
                
                with col2:
                    st.write("**Identity URI:**")
                    st.caption(identity_uri if identity_uri else "N/A")
                
                # Show definition if available
                definition = get_definition(identity_uri)
                if definition:
                    st.write("**Definition:**")
                    st.info(definition)
                
                st.divider()
        
        with st.expander("🔍 View Raw Identity Data"):
            st.json(identities)
    else:
        st.info("No identity information recorded.")

with t6:
    st.subheader("External References")
    refs = person.get('externalReferences', [])
    
    if refs:
        ref_data = []
        for ref in refs:
            ref_data.append({
                'Database': ref.get('external_db_name', 'N/A'),
                'ID': ref.get('external_id', 'N/A'),
                'ID Type': ref.get('external_id_type', 'N/A')
            })
        
        df = pd.DataFrame(ref_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No external references recorded.")
    
    # Also show persons in cluster
    persons = person.get('persons', [])
    if persons:
        st.subheader("Person IDs in Cluster")
        person_df = pd.DataFrame(persons)
        st.dataframe(person_df, use_container_width=True, hide_index=True)

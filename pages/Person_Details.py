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
all_data = st.session_state.get('all_data', {})

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

def get_primary_name(person_data):
    """Get the primary name/appellation for a person"""
    appellations = person_data.get('appellations', [])
    if appellations:
        return appellations[0].get('appellation', 'Unknown')
    return 'Unknown'

def get_event_label(event_uri, original_label):
    """Get enriched label for an event URI"""
    # Check for special event mappings first
    if event_uri in enrichment_data.get('event_labels', {}):
        return enrichment_data['event_labels'][event_uri]
    
    # Otherwise use the enriched label system
    return get_enriched_label(event_uri, original_label)

def get_better_source(source_string):
    """Get a better citation for Zotero sources"""
    if not source_string:
        return source_string
    
    # Check if this is a Zotero URI
    zotero_data = enrichment_data.get('zotero', {})
    
    # Try exact match first
    if source_string in zotero_data:
        return zotero_data[source_string]
    
    # Try lowercase match
    if source_string.lower() in zotero_data:
        return zotero_data[source_string.lower()]
    
    # Check if source contains a Zotero URI
    if 'zotero.org' in source_string.lower():
        for zot_uri, citation in zotero_data.items():
            if zot_uri.lower() in source_string.lower():
                return citation
    
    return source_string

# Get primary name
primary_name = "Unknown"
if person.get('appellations'):
    primary_name = person['appellations'][0].get('appellation', 'Unknown')

st.title(f"👤 {primary_name}")
st.caption(f"Cluster ID: {pid}")

if st.button("⬅️ Back to Search"):
    st.switch_page("Search.py")

# --- Tabbed Details View ---
t0, t1, t2, t3, t4, t5, t6, t7 = st.tabs([
    "📅 Timeline",
    "💼 Activities", 
    "🌍 Locations", 
    "📅 Events", 
    "👤 Appellations",
    "🆔 Identities",
    "👥 Relations",
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
        
        # CSS for timeline styling
        st.markdown("""
        <style>
        .timeline-item {
            margin-left: 20px;
            border-left: 3px solid #e0e0e0;
            padding-left: 30px;
            padding-bottom: 20px;
            position: relative;
        }
        .timeline-marker {
            position: absolute;
            left: -9px;
            top: 5px;
            width: 15px;
            height: 15px;
            border-radius: 50%;
            background: #4CAF50;
            border: 3px solid white;
            box-shadow: 0 0 0 2px #4CAF50;
        }
        .timeline-date {
            font-weight: bold;
            color: #4CAF50;
            font-size: 1.1em;
            margin-bottom: 5px;
        }
        .timeline-summary {
            color: #666;
            font-size: 0.9em;
            margin-top: 5px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Display timeline
        for i, obs in enumerate(obs_list):
            # Timeline marker and date
            st.markdown(f"""
            <div class="timeline-item">
                <div class="timeline-marker"></div>
                <div class="timeline-date">📅 {obs['display_dates']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Create summary line
            summary_parts = []
            
            # Get primary name from this observation
            if obs['appellations']:
                name = obs['appellations'][0].get('appellation', 'Unknown')
                summary_parts.append(f"👤 {name}")
            
            # Get primary activity
            if obs['activities']:
                original_label = obs['activities'][0].get('original_label', '')
                enriched = get_enriched_label(obs['activities'][0].get('activity', ''), original_label)
                summary_parts.append(f"💼 {enriched}")
            
            # Get primary location
            if obs['locations']:
                location_uri = obs['locations'][0].get('location', '')
                original_desc = obs['locations'][0].get('original_location_description', '')
                enriched_location = get_enriched_label(location_uri, '')
                if not enriched_location and original_desc:
                    enriched_location = get_enriched_label(original_desc.upper(), enrichment_data, original_desc)
                if enriched_location:
                    summary_parts.append(f"📍 {enriched_location}")
            
            # Get primary event
            if obs['events']:
                event_label = obs['events'][0].get('original_label', '')
                event_uri = obs['events'][0].get('event', '')
                enriched = get_event_label(event_uri, event_label)
                summary_parts.append(f"⚡ {enriched}")
            
            summary = " • ".join(summary_parts) if summary_parts else "No data"
            
            # Display compact summary with expander
            with st.expander(f"**{obs['observation_id']}** — {summary}", expanded=False):
                # Source information in a compact format
                col1, col2 = st.columns(2)
                with col1:
                    st.caption("📚 **Source**")
                    better_source = get_better_source(obs['source'])
                    st.caption(better_source)
                with col2:
                    st.caption("🔗 **Reconstruction**")
                    better_recon = get_better_source(obs['reconstruction_source'])
                    st.caption(better_recon)
                
                st.markdown("---")
                
                # Display content by category in a compact format
                if obs['appellations']:
                    st.markdown("**👤 Names**")
                    name_list = []
                    for app in obs['appellations']:
                        name = app.get('appellation', 'Unknown')
                        type_uri = app.get('appellationType', '')
                        enriched_type = get_enriched_label(type_uri, '')
                        if enriched_type:
                            name_list.append(f"{name} _{({enriched_type})}_")
                        else:
                            name_list.append(name)
                    st.write(" • ".join(name_list))
                    st.write("")
                
                if obs['activities']:
                    st.markdown("**💼 Activities**")
                    for act in obs['activities']:
                        original_label = act.get('original_label', 'N/A')
                        enriched_label = get_enriched_label(act.get('activity', ''), original_label)
                        employer = act.get('employer', '')
                        
                        parts = [f"**{enriched_label}**"]
                        if employer:
                            parts.append(f"at _{employer}_")
                        if act.get('startDate') or act.get('endDate'):
                            date_range = []
                            if act.get('startDate'):
                                date_range.append(act['startDate'])
                            if act.get('endDate'):
                                date_range.append(act['endDate'])
                            parts.append(f"`{' – '.join(date_range)}`")
                        
                        st.write(" ".join(parts))
                    st.write("")
                
                if obs['identities']:
                    st.markdown("**🆔 Identity**")
                    identity_list = []
                    for identity in obs['identities']:
                        original_label = identity.get('original_label', 'N/A')
                        enriched_label = get_enriched_label(identity.get('identity', ''), original_label)
                        identity_list.append(enriched_label)
                    st.write(" • ".join(identity_list))
                    st.write("")
                
                if obs['locations']:
                    st.markdown("**🌍 Locations**")
                    for loc in obs['locations']:
                        relation_uri = loc.get('locationRelation', '')
                        enriched_relation = get_enriched_label(relation_uri, loc.get('original_label', ''))
                        
                        location_uri = loc.get('location', '')
                        original_desc = loc.get('original_location_description', 'Unknown')
                        enriched_location = get_enriched_label(location_uri, '')
                        if not enriched_location and original_desc:
                            enriched_location = get_enriched_label(original_desc.upper(), enrichment_data, original_desc)
                        
                        st.write(f"_{enriched_relation}_: **{enriched_location}**")
                    st.write("")
                
                if obs['events']:
                    st.markdown("**⚡ Events**")
                    for event in obs['events']:
                        original_label = event.get('original_label', 'Unknown Event')
                        event_uri = event.get('event', '')
                        enriched_label = get_event_label(event_uri, original_label)
                        
                        location_uri = event.get('location', '')
                        original_location = event.get('original_location_description', '')
                        enriched_location = get_enriched_label(location_uri, '')
                        if not enriched_location and original_location:
                            enriched_location = get_enriched_label(original_location.upper(), enrichment_data, original_location)
                        
                        parts = [f"**{enriched_label}**"]
                        if enriched_location:
                            parts.append(f"in _{enriched_location}_")
                        if event.get('startDate'):
                            parts.append(f"`{event['startDate']}`")
                        
                        st.write(" ".join(parts))



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
                'Source': get_better_source(act.get('observation_source', 'N/A'))
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
            map_df["lat"] = pd.to_numeric(map_df["lat"], errors="coerce")
            map_df["lon"] = pd.to_numeric(map_df["lon"], errors="coerce")

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
            enriched_event = get_event_label(event_uri, original_label)
            enriched_location = get_enriched_label(location_uri, '')
            if not enriched_location and original_location:
                enriched_location = get_enriched_label(original_location.upper(), enrichment_data, original_location)
            
            # Get better source citation
            source = event.get('observation_source', 'N/A')
            better_source = get_better_source(source)
            
            event_data.append({
                'Event': enriched_event,
                'Original Location': original_location,
                'Standardized Location': enriched_location if enriched_location and enriched_location != original_location else '—',
                'Date': event.get('startDate', 'Unknown date'),
                'Source': better_source
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
                'Source': get_better_source(app.get('observation_source', 'N/A'))
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
    st.subheader("Personal Relations")
    relations = person.get('relations', [])
    
    if relations:
        st.write(f"Found {len(relations)} relationship(s)")
        
        # Create relation data with enrichment
        relation_data = []
        
        for rel in relations:
            relation_type_uri = rel.get('relation', '')
            other_person_uri = rel.get('otherPerson', '')
            
            # Get enriched relation type
            enriched_relation = get_enriched_label(relation_type_uri, rel.get('original_label', 'N/A'))
            
            # Find the other person in the dataset
            # The otherPerson URI is a cluster ID in the dataset
            other_person_name = "Unknown"
            other_person_id = None
            
            if other_person_uri and other_person_uri in all_data:
                # Direct match - the URI is a cluster ID
                other_person_id = other_person_uri
                other_person_data = all_data[other_person_uri]
                other_person_name = get_primary_name(other_person_data)
            
            relation_data.append({
                'Relation Type': enriched_relation,
                'Related Person': other_person_name,
                'Cluster ID': other_person_id if other_person_id else 'Not found',
                'Date': rel.get('annotationDate', 'N/A'),
                'Source': get_better_source(rel.get('observation_source', 'N/A')),
                'other_person_uri': other_person_uri,
                'other_person_id': other_person_id
            })
        
        # Display relations as cards with clickable links
        for i, rel_info in enumerate(relation_data):
            with st.container():
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.markdown(f"**{rel_info['Relation Type']}**")
                    st.caption(f"Date: {rel_info['Date']}")
                
                with col2:
                    st.markdown(f"**👤 {rel_info['Related Person']}**")
                    if rel_info['Cluster ID'] != 'Not found':
                        st.caption(f"Cluster: {rel_info['Cluster ID']}")
                    else:
                        st.caption(f"⚠️ Person not found in dataset")
                
                with col3:
                    # Add button to view the related person
                    if rel_info['other_person_id'] and rel_info['other_person_id'] in all_data:
                        if st.button(f"View →", key=f"view_relation_{i}"):
                            # Update session state to view the related person
                            st.session_state['selected_person_id'] = rel_info['other_person_id']
                            st.session_state['selected_person_data'] = all_data[rel_info['other_person_id']]
                            st.rerun()
                    else:
                        st.caption("Not available")
                
                # Show source in expander
                with st.expander("ℹ️ Details"):
                    st.write(f"**Source:** {rel_info['Source']}")
                    st.write(f"**Other Person URI:** {rel_info['other_person_uri']}")
                    if rel_info['Cluster ID'] == 'Not found':
                        st.warning("This person's cluster ID could not be found in the dataset. The person may have been filtered out or excluded from the current data export.")
                
                if i < len(relation_data) - 1:
                    st.divider()
        
        # Show raw data
        with st.expander("🔍 View Raw Relations Data"):
            st.json(relations)
    else:
        st.info("No relations recorded.")

with t7:
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

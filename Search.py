import streamlit as st
import json
import os
import pandas as pd

st.set_page_config(page_title="VOC Explorer", page_icon="📜", layout="wide")

@st.cache_data
def load_enrichment_data():
    """Load the enrichment CSV files with proper encoding handling"""
    enrichment = {
        'locations': {},
        'poolparty': {},
        'zotero': {},
        'event_labels': {}
    }
    
    # Special event URI mappings
    enrichment['event_labels']['https://github.com/globalise-huygens/nlp-event-detection/wiki#beingdead'] = 'Deceased'
    
    # Load location URIs with encoding fallback
    if os.path.exists('location_uris_enriched.csv'):
        try:
            # Try UTF-8 first
            loc_df = pd.read_csv('location_uris_enriched.csv', encoding='utf-8')
        except UnicodeDecodeError:
            try:
                # Try Windows-1252 (common for Western European languages)
                loc_df = pd.read_csv('location_uris_enriched.csv', encoding='windows-1252')
            except UnicodeDecodeError:
                # Try ISO-8859-1 as last resort
                loc_df = pd.read_csv('location_uris_enriched.csv', encoding='iso-8859-1')
        
        for _, row in loc_df.iterrows():
            if pd.notna(row['location_uri']):
                enrichment['locations'][row['location_uri'].lower()] = {
                    'label': row['label'],
                    'latitude': row['latitude'] if pd.notna(row['latitude']) else None,
                    'longitude': row['longitude'] if pd.notna(row['longitude']) else None
                }
    
    # Load poolparty URIs with encoding fallback
    if os.path.exists('poolparty_uris_enriched.csv'):
        try:
            # Try UTF-8 first
            pp_df = pd.read_csv('poolparty_uris_enriched.csv', encoding='utf-8')
        except UnicodeDecodeError:
            try:
                # Try Windows-1252
                pp_df = pd.read_csv('poolparty_uris_enriched.csv', encoding='windows-1252')
            except UnicodeDecodeError:
                # Try ISO-8859-1
                pp_df = pd.read_csv('poolparty_uris_enriched.csv', encoding='iso-8859-1')
        
        for _, row in pp_df.iterrows():
            if pd.notna(row['uri']):
                enrichment['poolparty'][row['uri']] = {
                    'type': row['type'],
                    'label': row['dutch_prefLabel'] if pd.notna(row['dutch_prefLabel']) else None,
                    'definition': row['definition'] if pd.notna(row['definition']) else None
                }
    
    # Load Zotero citations with encoding fallback
    if os.path.exists('zotero_uris.csv'):
        try:
            # Try UTF-8 first
            zot_df = pd.read_csv('zotero_uris.csv', encoding='utf-8')
        except UnicodeDecodeError:
            try:
                # Try Windows-1252
                zot_df = pd.read_csv('zotero_uris.csv', encoding='windows-1252')
            except UnicodeDecodeError:
                # Try ISO-8859-1
                zot_df = pd.read_csv('zotero_uris.csv', encoding='iso-8859-1')
        
        for _, row in zot_df.iterrows():
            if pd.notna(row['zotero_uri']):
                # Store both lowercase and original case versions for matching
                uri_lower = row['zotero_uri'].lower()
                enrichment['zotero'][uri_lower] = row['source_reference'] if pd.notna(row['source_reference']) else row['zotero_uri']
                enrichment['zotero'][row['zotero_uri']] = row['source_reference'] if pd.notna(row['source_reference']) else row['zotero_uri']
    
    return enrichment

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

import re

def get_lifespan(person_data):
    """Extracts a year range from startDate, endDate, and annotationDate across the cluster"""
    years = []
    
    # These are the lists in your JSON that contain date information
    categories = ['activeAs', 'events', 'locationRelations', 'appellations']
    
    for category in categories:
        items = person_data.get(category, [])
        for item in items:
            # Check all possible date fields in each record
            for date_key in ['startDate', 'endDate', 'annotationDate']:
                val = item.get(date_key)
                if val and isinstance(val, str):
                    # Find 4-digit years (e.g., 1745)
                    found_years = re.findall(r'\b(1[678]\d{2})\b', val)
                    years.extend([int(y) for y in found_years])

    if not years:
        return "Dates unknown"
    
    start_yr = min(years)
    end_yr = max(years)
    
    if start_yr == end_yr:
        return f"Active in {start_yr}"
    return f"{start_yr} – {end_yr}"

def get_enriched_label(uri, enrichment_data, fallback=''):
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

def search_in_field(field_list, search_term, enrichment_data=None):
    """Search for a term within a list of dictionaries"""
    if not search_term:
        return True
    search_lower = search_term.lower()
    
    for item in field_list:
        # Search in original text
        if search_lower in str(item).lower():
            return True
        
        # Search in enriched labels if available
        if enrichment_data:
            for key in ['activity', 'locationRelation', 'location']:
                if key in item:
                    uri = item[key]
                    enriched_label = get_enriched_label(uri, enrichment_data, '')
                    if search_lower in enriched_label.lower():
                        return True
            
            # Search in location description
            if 'original_location_description' in item:
                loc_desc = item['original_location_description']
                if isinstance(loc_desc, str) and loc_desc.upper() in enrichment_data['locations']:
                    enriched_label = enrichment_data['locations'][loc_desc.upper()].get('label', '')
                    if search_lower in enriched_label.lower():
                        return True
    
    return False

# Load data and enrichment
data = load_data()
enrichment_data = load_enrichment_data()

# Display info about loaded enrichment data
if enrichment_data:
    with st.sidebar:
        st.success("✅ Enrichment data loaded")
        st.caption(f"📍 {len(enrichment_data['locations'])} location mappings")
        st.caption(f"🏷️ {len(enrichment_data['poolparty'])} poolparty URIs")
        if enrichment_data['zotero']:
            st.caption(f"📚 {len(enrichment_data['zotero']) // 2} Zotero citations")  # Divided by 2 because we store both cases

st.title("Cochin Persondata Viewer")

st.markdown("""This viewer allows you to search data from the to be published GLOBALISE persons dataset. 
            It contains a small sample of the data, created by asking the question _Who in the dataset had Cochin as their place of residence?_'
            It is meant for use in the 'Getting to know GLOBALISE: personsdata' workshop on march 3th.""")

st.markdown('This viewer is an experiment and not a part of the official GLOBALISE infrastructure. YMMV.')

if data:
    tab_search, tab_stats, tab_enrichment = st.tabs(["🔍 Search", "📊 Statistics", "🗂️ Enrichment Info"])

    with tab_search:
        query = st.text_input("Search by name...", placeholder="e.g. Johannes")
        
        with st.expander("🛠️ Advanced Search"):
            adv_loc = st.text_input("Location (e.g. Amsterdam, Cochin)")
            adv_role = st.text_input("Role (e.g. merchant, bookkeeper)")

        # Filtering logic
        results = {}
        for k, v in data.items():
            name_match = not query or query.lower() in str(v.get('appellations', '')).lower()
            loc_match = not adv_loc or search_in_field(v.get('locationRelations', []), adv_loc, enrichment_data)
            role_match = not adv_role or search_in_field(v.get('activeAs', []), adv_role, enrichment_data)
            
            if name_match and loc_match and role_match:
                results[k] = v

        if results:
            st.markdown("### Top Matches")
            
            # Get first 3 items from results
            top_matches = list(results.items())[:3]
            
            cols = st.columns(3)
            for idx, (p_id, person) in enumerate(top_matches):
                with cols[idx]:
                    with st.container(border=True):
                        st.markdown(f"**{get_primary_name(person)}**")
                        st.caption(f"📅 Observed: {get_lifespan(person)}")
                        
                        # Direct navigation button
                        if st.button(f"View Profile", key=f"btn_{p_id}", use_container_width=True):
                            st.session_state['selected_person_id'] = p_id
                            st.session_state['selected_person_data'] = person
                            st.session_state['enrichment_data'] = enrichment_data
                            st.session_state['all_data'] = data
                            st.switch_page("pages/Person_Details.py")

            st.divider()

            # Secondary Selector (for when the person isn't in the top 3)
            st.write(f"Total results: {len(results)}")
            
            display_options = {k: f"{k} - {get_primary_name(v)}" for k, v in results.items()}
            
            selection = st.selectbox(
                "Or select from all results:", 
                options=list(results.keys()),
                format_func=lambda x: display_options[x]
            )
            
            if selection:
                if st.button("Go to Selected Profile 👤", type="primary", use_container_width=True):
                    st.session_state['selected_person_id'] = selection
                    st.session_state['selected_person_data'] = results[selection]
                    st.session_state['enrichment_data'] = enrichment_data
                    st.session_state['all_data'] = data
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
        
        # Activity distribution with enriched labels
        st.subheader("Most Common Roles")
        roles = {}
        for person in data.values():
            for activity in person.get('activeAs', []):
                # Try to get enriched label
                enriched_label = get_enriched_label(
                    activity.get('activity', ''),
                    enrichment_data,
                    activity.get('original_label', 'Unknown')
                )
                roles[enriched_label] = roles.get(enriched_label, 0) + 1
        
        if roles:
            roles_df = pd.DataFrame(list(roles.items()), columns=['Role', 'Count'])
            roles_df = roles_df.sort_values('Count', ascending=False).head(15)
            st.bar_chart(roles_df.set_index('Role'))
        
        # Location distribution
        st.subheader("Most Common Locations")
        locations = {}
        for person in data.values():
            for loc_rel in person.get('locationRelations', []):
                # Try to get enriched label
                loc_uri = loc_rel.get('location', '')
                original_desc = loc_rel.get('original_location_description', 'Unknown')
                
                # Try enriched label
                enriched_label = get_enriched_label(loc_uri, enrichment_data, '')
                if not enriched_label and original_desc:
                    enriched_label = get_enriched_label(original_desc.upper(), enrichment_data, original_desc)
                
                label = enriched_label if enriched_label else original_desc
                locations[label] = locations.get(label, 0) + 1
        
        if locations:
            loc_df = pd.DataFrame(list(locations.items()), columns=['Location', 'Count'])
            loc_df = loc_df.sort_values('Count', ascending=False).head(15)
            st.bar_chart(loc_df.set_index('Location'))

    with tab_enrichment:
        st.header("🗂️ Enrichment Data Overview")
        
        st.subheader("📍 Location Mappings")
        if enrichment_data['locations']:
            loc_list = []
            for uri, data in enrichment_data['locations'].items():
                loc_list.append({
                    'URI': uri,
                    'Label': data['label'],
                    'Latitude': data['latitude'],
                    'Longitude': data['longitude']
                })
            loc_df = pd.DataFrame(loc_list)
            st.dataframe(loc_df, use_container_width=True, hide_index=True)
        else:
            st.info("No location enrichment data loaded.")
        
        st.subheader("🏷️ Poolparty URI Mappings")
        if enrichment_data['poolparty']:
            # Group by type
            types = {}
            for uri, data in enrichment_data['poolparty'].items():
                type_name = data['type']
                if type_name not in types:
                    types[type_name] = []
                types[type_name].append({
                    'URI': uri,
                    'Label': data['label'],
                    'Has Definition': '✓' if data['definition'] else '✗'
                })
            
            for type_name, items in types.items():
                with st.expander(f"📁 {type_name.title()} ({len(items)} entries)"):
                    df = pd.DataFrame(items)
                    st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No poolparty enrichment data loaded.")
        
        st.subheader("📚 Zotero Citations")
        if enrichment_data['zotero']:
            # Get unique citations (we store both cases, so divide by 2)
            unique_citations = {}
            for uri, citation in enrichment_data['zotero'].items():
                if uri.lower() not in unique_citations:
                    unique_citations[uri.lower()] = {
                        'URI': uri,
                        'Citation': citation
                    }
            
            citation_list = list(unique_citations.values())[:50]  # Show first 50
            df = pd.DataFrame(citation_list)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            if len(unique_citations) > 50:
                st.caption(f"Showing 50 of {len(unique_citations)} citations")
        else:
            st.info("No Zotero citation data loaded. Add zotero_uris.csv to enable better source citations.")
        
else:
    st.error("data.json not found! Please ensure data.json is in the same directory as this script.")
    st.info("Your data.json should contain VOC person clusters with appellations, activeAs, locationRelations, events, etc.")

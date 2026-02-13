#!/usr/bin/env python3
"""
Process a JSON file to extract Zotero URIs and generate a reference CSV.

This script:
1. Loads a data.json file
2. Recursively scans the JSON to find all unique Zotero URIs
3. Fetches citations from Zotero API (batch processing)
4. Outputs 'zotero_uris.csv' with columns: zotero_uri, source_reference
"""

import json
import pandas as pd
from pathlib import Path
import re
from pyzotero import zotero

def is_zotero_uri(value):
    """Check if a value is a Zotero URI."""
    if pd.isna(value) or not isinstance(value, str):
        return False
    # Check for standard zotero links or protocol
    return ('zotero://' in value.lower() or 
            'zotero.org' in value.lower())

def extract_item_key(zotero_uri):
    """Extract the item key from a Zotero URI and convert to uppercase."""
    patterns = [
        r'zotero://select/library/items/([A-Za-z0-9]+)',
        r'zotero://select/groups/\d+/items/([A-Za-z0-9]+)',
        r'zotero\.org/users/\d+/items/([A-Za-z0-9]+)',
        r'zotero\.org/groups/\d+/items/([A-Za-z0-9]+)',
        r'/items/([A-Za-z0-9]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, zotero_uri, re.IGNORECASE)
        if match:
            return match.group(1).upper()
    return None

def extract_library_info(zotero_uri):
    """Extract library type and ID from Zotero URI."""
    group_match = re.search(r'groups/(\d+)', zotero_uri)
    if group_match:
        return 'group', group_match.group(1)
    
    user_match = re.search(r'users/(\d+)', zotero_uri)
    if user_match:
        return 'user', user_match.group(1)
    
    return None, None

def fetch_citations_batch(zotero_uris, default_library_id=None, api_key=None, default_library_type='user'):
    """
    Fetch citations for all unique Zotero URIs in one batch.
    """
    citation_cache = {}
    
    if not api_key:
        print("  No API key - using item keys as placeholders")
        for uri in zotero_uris:
            item_key = extract_item_key(uri)
            citation_cache[uri] = f"[Zotero Item: {item_key}]" if item_key else uri
        return citation_cache
    
    # Group URIs by library
    libraries = {}
    for uri in zotero_uris:
        lib_type, lib_id = extract_library_info(uri)
        
        if lib_type and lib_id:
            key = (lib_type, lib_id)
        elif default_library_id:
            key = (default_library_type, default_library_id)
        else:
            item_key = extract_item_key(uri)
            citation_cache[uri] = f"[Zotero Item: {item_key}]" if item_key else uri
            continue
        
        if key not in libraries:
            libraries[key] = []
        libraries[key].append(uri)
    
    # Fetch citations for each library
    for (lib_type, lib_id), uris in libraries.items():
        print(f"  Fetching {len(uris)} citations from {lib_type} library {lib_id}...")
        
        try:
            zot = zotero.Zotero(lib_id, lib_type, api_key)
            
            # Zotero API allows fetching multiple items by key (up to 50 at a time usually)
            # For simplicity here, we iterate. Optimization: could use zot.items(itemKeys=...)
            for uri in uris:
                item_key = extract_item_key(uri)
                if not item_key:
                    citation_cache[uri] = uri
                    continue
                
                try:
                    item = zot.item(item_key)
                    data = item.get('data', {})
                    
                    # Build citation string
                    authors = []
                    creators = data.get('creators', [])
                    for creator in creators[:3]:
                        if 'lastName' in creator:
                            authors.append(creator['lastName'])
                        elif 'name' in creator: # Sometimes organizations have just 'name'
                            authors.append(creator['name'])
                    
                    author_str = ', '.join(authors) if authors else 'Unknown Author'
                    if len(creators) > 3:
                        author_str += ' et al.'
                    
                    title = data.get('title', 'Untitled')
                    year = data.get('date', '')[:4] if data.get('date') else ''
                    
                    citation = f"{author_str}"
                    if year:
                        citation += f" ({year})"
                    citation += f". {title}"
                    
                    citation_cache[uri] = citation
                    print(f"    ✓ {item_key}: {citation[:60]}...")
                    
                except Exception as e:
                    print(f"    ✗ Failed to fetch {item_key}: {e}")
                    citation_cache[uri] = f"[Zotero Item: {item_key}]"
        
        except Exception as e:
            print(f"    Error connecting to library: {e}")
            for uri in uris:
                if uri not in citation_cache:
                    item_key = extract_item_key(uri)
                    citation_cache[uri] = f"[Zotero Item: {item_key}]" if item_key else uri
    
    return citation_cache

def extract_uris_recursive(data, unique_uris=None):
    """
    Recursively scan a JSON object (dict or list) for Zotero URIs.
    """
    if unique_uris is None:
        unique_uris = set()

    if isinstance(data, dict):
        for key, value in data.items():
            extract_uris_recursive(value, unique_uris)
    elif isinstance(data, list):
        for item in data:
            extract_uris_recursive(item, unique_uris)
    elif isinstance(data, str):
        if is_zotero_uri(data):
            unique_uris.add(data)
    
    return unique_uris

def main():
    """Main function to process the JSON file."""
    
    # Configuration - UPDATE THESE VALUES
    input_json_path = "C:/Users/kayp/GitHub/globalise-person-app/data.json"
    output_csv_name = 'zotero_uris.csv'
    
    library_id = '4678659'   # Your Zotero user ID or group ID
    api_key = 'Rnibs3JA89o3DSWBwOFt3r6N'      # Your Zotero API key
    library_type = 'group'   # 'user' or 'group'
    
    print("=" * 70)
    print("Zotero JSON Reference Extractor")
    print("=" * 70)
    
    if not api_key:
        print("\n⚠ WARNING: No Zotero API key provided")
        print("  Citations will show as placeholders\n")

    input_path = Path(input_json_path)
    if not input_path.exists():
        # Fallback to local directory if full path doesn't exist
        input_path = Path('data.json')
        if not input_path.exists():
            print(f"✗ File not found: {input_json_path}")
            return

    print(f"\n📂 Reading: {input_path}")
    
    # Step 1: Load JSON and Collect URIs
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"✗ Error reading JSON file: {e}")
        return

    print(f"\n{'─' * 70}")
    print("STEP 1: Scanning JSON for Zotero URIs...")
    print(f"{'─' * 70}")
    
    unique_uris = extract_uris_recursive(data)
    
    if not unique_uris:
        print("✗ No Zotero URIs found in the JSON file.")
        return
    
    print(f"✓ Found {len(unique_uris)} unique Zotero URI(s)")
    
    # Step 2: Fetch citations
    print(f"\n{'─' * 70}")
    print("STEP 2: Fetching citations from Zotero API...")
    print(f"{'─' * 70}")
    citation_map = fetch_citations_batch(unique_uris, library_id, api_key, library_type)
    
    # Step 3: Write CSV
    print(f"\n{'─' * 70}")
    print("STEP 3: Generating output CSV...")
    print(f"{'─' * 70}")
    
    csv_rows = []
    for uri in unique_uris:
        citation = citation_map.get(uri, uri)
        csv_rows.append({
            'zotero_uri': uri,
            'source_reference': citation
        })
    
    # Create DataFrame and sort for tidiness
    df = pd.DataFrame(csv_rows)
    # Sort by URI or Citation for better readability
    df = df.sort_values(by='source_reference')
    
    try:
        df.to_csv(output_csv_name, index=False, encoding='utf-8')
        print(f"✓ Successfully wrote {len(df)} references to: {output_csv_name}")
        print(f"  Columns: {', '.join(df.columns)}")
    except Exception as e:
        print(f"✗ Error writing CSV: {e}")

    print(f"\n{'=' * 70}")
    print("✓ Complete!")
    print(f"{'=' * 70}")

if __name__ == '__main__':
    main()
"""
VOC Data URI Extractor
Extracts location URIs and PoolParty URIs from VOC GLOBALISE JSON data
and exports them to separate CSV files.
"""

import json
import csv
from collections import defaultdict
from pathlib import Path


def load_json_data(filepath='data.json'):
    """Load the VOC JSON data file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {filepath} not found!")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {filepath}: {e}")
        return None


def extract_location_uris(data):
    """
    Extract all unique 'location' URIs from the JSON data.
    Searches in: activeAs, locationRelations, events, identities
    """
    location_uris = set()
    
    for cluster_id, cluster_data in data.items():
        # From activeAs
        for activity in cluster_data.get('activeAs', []):
            loc = activity.get('location')
            if loc and loc.strip() and loc != '-1':
                location_uris.add(loc.strip())
        
        # From locationRelations
        for loc_rel in cluster_data.get('locationRelations', []):
            loc = loc_rel.get('location')
            if loc and loc.strip() and loc != '-1':
                location_uris.add(loc.strip())
        
        # From events
        for event in cluster_data.get('events', []):
            loc = event.get('location')
            if loc and loc.strip() and loc != '-1':
                location_uris.add(loc.strip())
        
        # From identities
        for identity in cluster_data.get('identities', []):
            loc = identity.get('location')
            if loc and loc.strip() and loc != '-1':
                location_uris.add(loc.strip())
    
    return sorted(location_uris)


def extract_poolparty_uris(data):
    """
    Extract all unique PoolParty URIs from various fields.
    Searches for: activity, activityType, identity, identityType, 
                  locationRelation, and relation URIs
    """
    poolparty_uris = defaultdict(set)
    
    for cluster_id, cluster_data in data.items():
        # From activeAs - activity and activityType
        for activity in cluster_data.get('activeAs', []):
            act = activity.get('activity')
            if act and act.strip():
                poolparty_uris['activity'].add(act.strip())
            
            act_type = activity.get('activityType')
            if act_type and act_type.strip():
                poolparty_uris['activityType'].add(act_type.strip())
        
        # From identities - identity and identityType
        for identity in cluster_data.get('identities', []):
            ident = identity.get('identity')
            if ident and ident.strip():
                poolparty_uris['identity'].add(ident.strip())
            
            ident_type = identity.get('identityType')
            if ident_type and ident_type.strip():
                poolparty_uris['identityType'].add(ident_type.strip())
        
        # From locationRelations - locationRelation
        for loc_rel in cluster_data.get('locationRelations', []):
            loc_relation = loc_rel.get('locationRelation')
            if loc_relation and loc_relation.strip():
                poolparty_uris['locationRelation'].add(loc_relation.strip())
        
        # From relations - relation (if it exists as a field)
        for relation in cluster_data.get('relations', []):
            if isinstance(relation, dict):
                rel = relation.get('relation')
                if rel and rel.strip():
                    poolparty_uris['relation'].add(rel.strip())
    
    return poolparty_uris


def write_location_uris_csv(location_uris, output_file='location_uris.csv'):
    """Write location URIs to CSV file"""
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['location_uri'])
        for uri in location_uris:
            writer.writerow([uri])
    
    print(f"✓ Created {output_file} with {len(location_uris)} unique location URIs")


def write_poolparty_uris_csv(poolparty_uris, output_file='poolparty_uris.csv'):
    """Write PoolParty URIs to CSV file with type column"""
    # Flatten all URIs with their type
    all_uris = []
    for uri_type, uri_set in poolparty_uris.items():
        for uri in sorted(uri_set):
            all_uris.append((uri_type, uri))
    
    # Sort by type, then by URI
    all_uris.sort()
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['type', 'uri'])
        for uri_type, uri in all_uris:
            writer.writerow([uri_type, uri])
    
    total_count = sum(len(uris) for uris in poolparty_uris.values())
    print(f"✓ Created {output_file} with {total_count} unique PoolParty URIs")
    print(f"  Breakdown:")
    for uri_type, uri_set in sorted(poolparty_uris.items()):
        print(f"    - {uri_type}: {len(uri_set)}")


def main():
    """Main extraction process"""
    print("VOC Data URI Extractor")
    print("=" * 50)
    
    # Load data
    print("\n1. Loading data.json...")
    data = load_json_data('data.json')
    
    if not data:
        print("Cannot proceed without valid JSON data.")
        return
    
    print(f"   Loaded {len(data)} person clusters")
    
    # Extract location URIs
    print("\n2. Extracting location URIs...")
    location_uris = extract_location_uris(data)
    
    # Extract PoolParty URIs
    print("\n3. Extracting PoolParty URIs...")
    poolparty_uris = extract_poolparty_uris(data)
    
    # Write to CSV files
    print("\n4. Writing CSV files...")
    write_location_uris_csv(location_uris)
    write_poolparty_uris_csv(poolparty_uris)
    
    print("\n" + "=" * 50)
    print("Extraction complete!")
    print("\nGenerated files:")
    print("  - location_uris.csv")
    print("  - poolparty_uris.csv")


if __name__ == "__main__":
    main()

"""
URI Extractor - Enriches PoolParty URIs with labels and definitions
Reads poolparty_uris.csv and poolparty.ttl (SKOS thesaurus)
Adds Dutch prefLabel and English/Dutch definition for each URI
"""

import csv
from rdflib import Graph, Namespace, RDF, RDFS, SKOS
from pathlib import Path


def load_skos_graph(ttl_file='poolparty.ttl'):
    """Load the PoolParty SKOS thesaurus from TTL file"""
    print(f"Loading SKOS data from {ttl_file}...")
    
    try:
        g = Graph()
        g.parse(ttl_file, format='turtle')
        print(f"✓ Loaded {len(g)} triples from {ttl_file}")
        return g
    except FileNotFoundError:
        print(f"Error: {ttl_file} not found!")
        print("Please ensure poolparty.ttl is in the same directory.")
        return None
    except Exception as e:
        print(f"Error parsing {ttl_file}: {e}")
        return None


def get_dutch_preflabel(graph, uri):
    """
    Extract Dutch prefLabel for a URI from SKOS graph
    Returns empty string if not found
    """
    if not graph:
        return ""
    
    try:
        from rdflib import URIRef
        uri_ref = URIRef(uri)
        
        # Try to get Dutch prefLabel (language tag: nl)
        for label in graph.objects(uri_ref, SKOS.prefLabel):
            if label.language == 'nl':
                return str(label)
        
        # Fallback: get any prefLabel
        for label in graph.objects(uri_ref, SKOS.prefLabel):
            return str(label)
        
        return ""
    except Exception as e:
        print(f"  Warning: Error getting prefLabel for {uri}: {e}")
        return ""


def get_definition(graph, uri):
    """
    Extract definition for a URI from SKOS graph
    Prefers English (en), falls back to Dutch (nl), then any language
    Returns empty string if not found
    """
    if not graph:
        return ""
    
    try:
        from rdflib import URIRef
        uri_ref = URIRef(uri)
        
        definitions = {'en': [], 'nl': [], 'other': []}
        
        # Collect all definitions by language
        for defn in graph.objects(uri_ref, SKOS.definition):
            lang = defn.language if hasattr(defn, 'language') else None
            if lang == 'en':
                definitions['en'].append(str(defn))
            elif lang == 'nl':
                definitions['nl'].append(str(defn))
            else:
                definitions['other'].append(str(defn))
        
        # Return in order of preference: English > Dutch > Other
        if definitions['en']:
            return definitions['en'][0]
        elif definitions['nl']:
            return definitions['nl'][0]
        elif definitions['other']:
            return definitions['other'][0]
        
        # Try scopeNote as fallback
        for note in graph.objects(uri_ref, SKOS.scopeNote):
            lang = note.language if hasattr(note, 'language') else None
            if lang == 'en':
                return str(note)
        
        for note in graph.objects(uri_ref, SKOS.scopeNote):
            lang = note.language if hasattr(note, 'language') else None
            if lang == 'nl':
                return str(note)
        
        return ""
    except Exception as e:
        print(f"  Warning: Error getting definition for {uri}: {e}")
        return ""


def enrich_poolparty_uris(input_csv='poolparty_uris.csv', 
                          output_csv='poolparty_uris_enriched.csv',
                          ttl_file='poolparty.ttl'):
    """
    Read poolparty_uris.csv and add Dutch prefLabel and definition columns
    """
    # Load SKOS graph
    graph = load_skos_graph(ttl_file)
    
    if not graph:
        print("Cannot proceed without SKOS data.")
        return
    
    # Check if input CSV exists
    if not Path(input_csv).exists():
        print(f"Error: {input_csv} not found!")
        print("Please run data-extract.py first to generate poolparty_uris.csv")
        return
    
    print(f"\nEnriching URIs from {input_csv}...")
    
    # Read input CSV and enrich
    enriched_rows = []
    not_found_count = 0
    
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for i, row in enumerate(reader, 1):
            uri = row['uri']
            uri_type = row['type']
            
            # Get Dutch prefLabel
            dutch_label = get_dutch_preflabel(graph, uri)
            
            # Get definition (preferably English, otherwise Dutch)
            definition = get_definition(graph, uri)
            
            # Track URIs not found
            if not dutch_label and not definition:
                not_found_count += 1
                print(f"  URI not found in thesaurus: {uri}")
            
            enriched_rows.append({
                'type': uri_type,
                'uri': uri,
                'dutch_prefLabel': dutch_label,
                'definition': definition
            })
            
            # Progress indicator
            if i % 10 == 0:
                print(f"  Processed {i} URIs...")
    
    # Write enriched CSV
    print(f"\nWriting enriched data to {output_csv}...")
    
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['type', 'uri', 'dutch_prefLabel', 'definition']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(enriched_rows)
    
    print(f"✓ Created {output_csv}")
    print(f"\nSummary:")
    print(f"  Total URIs processed: {len(enriched_rows)}")
    print(f"  URIs found in thesaurus: {len(enriched_rows) - not_found_count}")
    print(f"  URIs not found: {not_found_count}")


def main():
    """Main enrichment process"""
    print("=" * 60)
    print("URI Extractor - PoolParty URI Enrichment")
    print("=" * 60)
    print()
    
    enrich_poolparty_uris()
    
    print("\n" + "=" * 60)
    print("Enrichment complete!")
    print("\nGenerated file:")
    print("  - poolparty_uris_enriched.csv")
    print("\nColumns:")
    print("  - type: URI type (activity, identity, etc.)")
    print("  - uri: Original URI")
    print("  - dutch_prefLabel: Preferred label in Dutch")
    print("  - definition: Definition (English preferred, Dutch fallback)")


if __name__ == "__main__":
    # Check if rdflib is installed
    try:
        import rdflib
    except ImportError:
        print("Error: rdflib is required but not installed.")
        print("Please install it with: pip install rdflib")
        exit(1)
    
    main()

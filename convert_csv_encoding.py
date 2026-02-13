"""
CSV Encoding Converter
======================
This utility script converts your enrichment CSV files to UTF-8 encoding
to avoid any encoding issues with the Streamlit app.

Usage:
    python convert_csv_encoding.py

This will create UTF-8 encoded versions of your CSV files.
"""

import pandas as pd
import os

def convert_csv_to_utf8(input_file, output_file=None):
    """Convert a CSV file to UTF-8 encoding"""
    if output_file is None:
        output_file = input_file
    
    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}")
        return False
    
    # Try different encodings
    encodings = ['utf-8', 'windows-1252', 'iso-8859-1', 'latin-1']
    df = None
    used_encoding = None
    
    for encoding in encodings:
        try:
            df = pd.read_csv(input_file, encoding=encoding)
            used_encoding = encoding
            print(f"✓ Successfully read {input_file} with {encoding} encoding")
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
    
    if df is None:
        print(f"❌ Could not read {input_file} with any standard encoding")
        return False
    
    # Save as UTF-8
    try:
        df.to_csv(output_file, encoding='utf-8', index=False)
        print(f"✓ Saved {output_file} with UTF-8 encoding")
        return True
    except Exception as e:
        print(f"❌ Error saving {output_file}: {e}")
        return False

def main():
    print("=" * 60)
    print("CSV Encoding Converter for VOC Explorer")
    print("=" * 60)
    print()
    
    files_to_convert = [
        'location_uris_enriched.csv',
        'poolparty_uris_enriched.csv'
    ]
    
    success_count = 0
    
    for filename in files_to_convert:
        print(f"Processing {filename}...")
        if convert_csv_to_utf8(filename):
            success_count += 1
        print()
    
    print("=" * 60)
    print(f"Conversion complete: {success_count}/{len(files_to_convert)} files converted")
    print("=" * 60)
    
    if success_count == len(files_to_convert):
        print("\n✓ All files converted successfully!")
        print("You can now run: streamlit run Search.py")
    else:
        print("\n⚠ Some files could not be converted.")
        print("Please check that the CSV files are in the same directory as this script.")

if __name__ == "__main__":
    main()

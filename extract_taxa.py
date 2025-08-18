#!/usr/bin/env python3
"""
Script to extract taxa information from Kraken2 TSV files and convert to RPM
for the interactive visualization dropdowns.
"""

import pandas as pd
import json
import sys
import os

def convert_to_rpm(df):
    """Convert read counts to reads per million (RPM)"""
    # Sum all reads per sample
    sample_sums = df.iloc[:, 1:].sum()
    # Convert to RPM
    rpm_df = df.copy()
    for col in df.columns[1:]:
        rpm_df[col] = (df[col] / sample_sums[col]) * 1000000
    return rpm_df

def extract_taxa_by_level(level_file, level_num):
    """Extract taxa names from a specific taxonomic level file"""
    if not os.path.exists(level_file):
        return []
    
    # Read the TSV file with headers
    df = pd.read_csv(level_file, sep='\t')
    
    # Define taxonomic level patterns
    level_patterns = {
        2: 'p__',  # Phylum
        3: 'c__',  # Class
        4: 'o__',  # Order
        5: 'f__',  # Family
        6: 'g__',  # Genus
        7: 's__'   # Species
    }
    
    if level_num not in level_patterns:
        return []
    
    pattern = level_patterns[level_num]
    
    # Filter rows that contain the pattern
    taxa_rows = df[df['Taxa'].str.contains(pattern, na=False)]
    
    # Extract taxa names (extract just the part after the pattern)
    taxa_names = []
    for _, row in taxa_rows.iterrows():
        taxon = row['Taxa']
        # Find the pattern and extract the taxon name
        if pattern in taxon:
            # Split by '|' and find the part that starts with our pattern
            parts = taxon.split('|')
            for part in parts:
                if part.startswith(pattern):
                    clean_name = part.replace(pattern, '')
                    taxa_names.append(clean_name)
                    break
    
    return sorted(list(set(taxa_names)))  # Remove duplicates and sort

def get_taxa_data(level_num, selected_taxon):
    """Get the RPM data for a specific taxon at a specific level"""
    level_file = f"all_child-UC_kraken2_250616_level_{level_num}.tsv"
    
    if not os.path.exists(level_file):
        return None
    
    # Read the TSV file with headers
    df = pd.read_csv(level_file, sep='\t')
    
    # Define taxonomic level patterns
    level_patterns = {
        2: 'p__',  # Phylum
        3: 'c__',  # Class
        4: 'o__',  # Order
        5: 'f__',  # Family
        6: 'g__',  # Genus
        7: 's__'   # Species
    }
    
    if level_num not in level_patterns:
        return None
    
    pattern = level_patterns[level_num]
    
    # Find the row with the selected taxon
    taxon_row = df[df['Taxa'].str.contains(f"{pattern}{selected_taxon}", na=False)]
    
    if taxon_row.empty:
        return None
    
    # Get the read counts for the 4 samples
    sample_data = taxon_row.iloc[0, 1:5].values
    
    # Convert to RPM
    sample_sums = df.iloc[:, 1:5].sum()
    rpm_data = (sample_data / sample_sums.values) * 1000000
    
    # Sample names in order: PedUC47, PedUC58, PedCtrl59, PedUC60
    sample_names = ['PedUC47', 'PedUC58', 'PedCtrl59', 'PedUC60']
    
    return {
        'control': float(rpm_data[2]),  # PedCtrl59
        'uc_samples': rpm_data[[0, 1, 3]].tolist(),  # PedUC47, PedUC58, PedUC60
        'uc_mean': float(rpm_data[[0, 1, 3]].mean()),
        'sample_names': sample_names,
        'rpm_values': rpm_data.tolist()
    }

def main():
    """Main function to handle command line arguments"""
    if len(sys.argv) < 2:
        print("Usage: python extract_taxa.py <command> [args...]")
        print("Commands:")
        print("  list_levels - List available taxonomic levels")
        print("  get_taxa <level> - Get taxa for a specific level")
        print("  get_data <level> <taxon> - Get data for a specific taxon")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "list_levels":
        print("Available taxonomic levels:")
        print("2 - Phylum")
        print("3 - Class")
        print("4 - Order")
        print("5 - Family")
        print("6 - Genus")
        print("7 - Species")
    
    elif command == "get_taxa":
        if len(sys.argv) < 3:
            print("Usage: python extract_taxa.py get_taxa <level>")
            sys.exit(1)
        
        level = int(sys.argv[2])
        level_file = f"all_child-UC_kraken2_250616_level_{level}.tsv"
        taxa = extract_taxa_by_level(level_file, level)
        
        # Output as JSON for easy parsing
        print(json.dumps(taxa))
    
    elif command == "get_data":
        if len(sys.argv) < 4:
            print("Usage: python extract_taxa.py get_data <level> <taxon>")
            sys.exit(1)
        
        level = int(sys.argv[2])
        taxon = sys.argv[3]
        data = get_taxa_data(level, taxon)
        
        if data:
            print(json.dumps(data))
        else:
            print("Taxon not found")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Simplified script to extract taxa information from Kraken2 TSV files and convert to RPM
for the interactive visualization dropdowns. Uses only standard library modules.
"""

import csv
import json
import sys
import os

def convert_to_rpm(data_rows):
    """Convert read counts to reads per million (RPM)"""
    # Calculate total reads per sample (columns 1-4)
    sample_totals = [0.0, 0.0, 0.0, 0.0]
    
    for row in data_rows:
        for i in range(4):
            try:
                sample_totals[i] += float(row[i + 1])
            except (ValueError, IndexError):
                pass
    
    # Convert to RPM
    rpm_rows = []
    for row in data_rows:
        rpm_row = [row[0]]  # Keep the taxa name
        for i in range(4):
            try:
                count = float(row[i + 1])
                rpm = (count / sample_totals[i]) * 1000000
                rpm_row.append(rpm)
            except (ValueError, IndexError):
                rpm_row.append(0.0)
        rpm_rows.append(rpm_row)
    
    return rpm_rows

def extract_taxa_by_level(level_file, level_num):
    """Extract taxa names from a specific taxonomic level file"""
    if not os.path.exists(level_file):
        return []
    
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
    
    # Read the TSV file manually
    taxa_names = set()  # Use set to avoid duplicates
    
    try:
        with open(level_file, 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            next(reader)  # Skip header row
            
            for row in reader:
                if len(row) > 0 and pattern in row[0]:
                    # Split by '|' and find the part that starts with our pattern
                    parts = row[0].split('|')
                    for part in parts:
                        if part.startswith(pattern):
                            clean_name = part.replace(pattern, '')
                            taxa_names.add(clean_name)
                            break
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        return []
    
    return sorted(list(taxa_names))

def get_taxa_data(level_num, selected_taxon):
    """Get the RPM data for a specific taxon at a specific level"""
    level_file = f"all_child-UC_kraken2_250616_level_{level_num}.tsv"
    
    if not os.path.exists(level_file):
        return None
    
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
    
    # Read the TSV file and find the taxon
    try:
        with open(level_file, 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            next(reader)  # Skip header row
            
            for row in reader:
                if len(row) > 4 and f"{pattern}{selected_taxon}" in row[0]:
                    # Found the taxon, get the read counts
                    sample_data = [float(row[i + 1]) for i in range(4)]
                    
                    # Convert to RPM
                    sample_totals = [0.0, 0.0, 0.0, 0.0]
                    
                    # Reset file pointer to calculate totals
                    f.seek(0)
                    next(reader)  # Skip header again
                    
                    for total_row in reader:
                        for i in range(4):
                            try:
                                sample_totals[i] += float(total_row[i + 1])
                            except (ValueError, IndexError):
                                pass
                    
                    # Calculate RPM
                    rpm_data = [(sample_data[i] / sample_totals[i]) * 1000000 for i in range(4)]
                    
                    # Sample names in order: PedUC47, PedUC58, PedCtrl59, PedUC60
                    sample_names = ['PedUC47', 'PedUC58', 'PedCtrl59', 'PedUC60']
                    
                    return {
                        'control': float(rpm_data[2]),  # PedCtrl59
                        'uc_samples': [float(rpm_data[0]), float(rpm_data[1]), float(rpm_data[3])],  # PedUC47, PedUC58, PedUC60
                        'uc_mean': float(sum([rpm_data[0], rpm_data[1], rpm_data[3]]) / 3),
                        'sample_names': sample_names,
                        'rpm_values': [float(x) for x in rpm_data]
                    }
                    
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        return None
    
    return None

def main():
    """Main function to handle command line arguments"""
    if len(sys.argv) < 2:
        print("Usage: python3 extract_taxa_simple.py <command> [args...]")
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
            print("Usage: python3 extract_taxa_simple.py get_taxa <level>")
            sys.exit(1)
        
        level = int(sys.argv[2])
        level_file = f"all_child-UC_kraken2_250616_level_{level}.tsv"
        taxa = extract_taxa_by_level(level_file, level)
        
        # Output as JSON for easy parsing
        print(json.dumps(taxa))
    
    elif command == "get_data":
        if len(sys.argv) < 4:
            print("Usage: python3 extract_taxa_simple.py get_data <level> <taxon>")
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

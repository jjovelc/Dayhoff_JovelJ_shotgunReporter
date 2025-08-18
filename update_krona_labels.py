#!/usr/bin/env python3
"""
Update Krona HTML file to replace SRR dataset labels with sample names from metadata.
This script runs automatically when the webpage loads to ensure labels are always correct.
"""

import pandas as pd
import re
import os

def update_krona_labels():
    """
    Update the all_krona_plots.html file to replace SRR dataset labels with sample names.
    """
    
    # Read metadata to get sample name mappings
    metadata_file = "metadata.tsv"
    krona_file = "all_krona_plots.html"
    
    if not os.path.exists(metadata_file):
        print(f"❌ Error: Metadata file '{metadata_file}' not found!")
        return False
        
    if not os.path.exists(krona_file):
        print(f"❌ Error: Krona file '{krona_file}' not found!")
        return False
    
    try:
        # Read metadata
        metadata_df = pd.read_csv(metadata_file, sep='\t')
        
        # Create mapping from SRR to sample name
        srr_to_sample = {}
        for _, row in metadata_df.iterrows():
            sample_name = row['sample']
            srr_accession = row['srr'].strip()
            srr_to_sample[srr_accession] = sample_name
        
        print(f"SRR to Sample mapping: {srr_to_sample}")
        
        # Read the Krona HTML file
        with open(krona_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace each SRR dataset label with the corresponding sample name
        original_content = content
        for srr, sample in srr_to_sample.items():
            # Replace the dataset label
            old_label = f'<dataset>{srr}_krona</dataset>'
            new_label = f'<dataset>{sample}</dataset>'
            content = content.replace(old_label, new_label)
            
            print(f"  Replaced: {old_label} → {new_label}")
        
        # Write the updated content back to the file
        with open(krona_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Successfully updated {krona_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating Krona labels: {e}")
        return False

if __name__ == "__main__":
    update_krona_labels()


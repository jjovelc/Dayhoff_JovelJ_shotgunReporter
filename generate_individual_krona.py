#!/usr/bin/env python3
"""
Generate individual Krona plots for each sample from Kraken2 output.
This script creates separate Krona HTML files for each sample showing their unique microbial composition.
"""

import pandas as pd
import subprocess
import os
import sys

def create_sample_krona_files(input_file, metadata_file, output_dir="krona_plots"):
    """
    Create individual Krona files for each sample.
    
    Args:
        input_file (str): Path to the Kraken2 output file
        metadata_file (str): Path to the metadata file with sample mappings
        output_dir (str): Directory to save the Krona files
    """
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Read the metadata file to get sample name mappings
    print(f"Reading metadata from {metadata_file}...")
    metadata_df = pd.read_csv(metadata_file, sep='\t')
    
    # Create mapping from sample name to SRR accession
    sample_to_srr = {}
    for _, row in metadata_df.iterrows():
        sample_name = row['sample']
        srr_accession = row['srr'].strip()  # Remove any whitespace
        sample_to_srr[sample_name] = srr_accession
    
    print(f"Sample to SRR mapping: {sample_to_srr}")
    
    # Read the Kraken2 output file
    print(f"Reading data from {input_file}...")
    df = pd.read_csv(input_file, sep='\t', index_col=0)
    
    # Get sample names (columns)
    samples = df.columns.tolist()
    print(f"Found samples: {samples}")
    
    # Process each sample
    for sample in samples:
        print(f"\nProcessing sample: {sample}")
        
        # Get the corresponding SRR accession
        if sample not in sample_to_srr:
            print(f"  Warning: No SRR mapping found for sample {sample}")
            continue
            
        srr_accession = sample_to_srr[sample]
        print(f"  Mapping to SRR: {srr_accession}")
        
        # Create sample-specific data
        sample_data = df[[sample]].copy()
        sample_data = sample_data[sample_data[sample] > 0]  # Remove zero counts
        
        if sample_data.empty:
            print(f"  Warning: No data for sample {sample}")
            continue
        
        # Create temporary file for Krona input
        temp_file = f"temp_{sample}_krona.txt"
        
        # Prepare data for Krona (taxonomy\tcount)
        with open(temp_file, 'w') as f:
            for taxon, row in sample_data.iterrows():
                count = row[sample]
                if count > 0:
                    # Convert taxonomy string to Krona format
                    # Replace | with tabs for hierarchical levels
                    taxonomy = taxon.replace('|', '\t')
                    f.write(f"{taxonomy}\t{count}\n")
        
        # Generate Krona HTML file with SRR-based naming
        output_file = os.path.join(output_dir, f"{srr_accession}_krona.html")
        
        try:
            # Use ktImportText to create Krona HTML
            cmd = [
                'ktImportText',
                '-o', output_file,
                temp_file
            ]
            
            print(f"  Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"  ✅ Successfully created: {output_file}")
            else:
                print(f"  ❌ Error creating Krona file: {result.stderr}")
                
        except FileNotFoundError:
            print(f"  ❌ Error: ktImportText not found. Please install Krona tools.")
            print(f"     Install with: conda install -c bioconda krona")
            break
        except Exception as e:
            print(f"  ❌ Unexpected error: {e}")
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    print(f"\n🎉 Krona generation complete! Files saved in '{output_dir}' directory.")
    return output_dir

def main():
    """Main function to run the script."""
    
    # Check if input file exists
    input_file = "all_child-UC_kraken2_250616.tsv"
    metadata_file = "metadata.tsv"
    
    if not os.path.exists(input_file):
        print(f"❌ Error: Input file '{input_file}' not found!")
        print("Please make sure you're in the correct directory.")
        sys.exit(1)
    
    if not os.path.exists(metadata_file):
        print(f"❌ Error: Metadata file '{metadata_file}' not found!")
        print("Please make sure you're in the correct directory.")
        sys.exit(1)
    
    # Generate individual Krona files
    output_dir = create_sample_krona_files(input_file, metadata_file)
    
    # List generated files
    if os.path.exists(output_dir):
        print(f"\n📁 Generated Krona files:")
        for file in sorted(os.listdir(output_dir)):
            if file.endswith('.html'):
                print(f"  - {file}")
    
    print(f"\n🚀 You can now update your webpage to use these individual Krona files!")

if __name__ == "__main__":
    main()

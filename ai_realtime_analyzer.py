#!/usr/bin/env python3
"""
Real-time AI Analyzer for Microbiome Plots
Generates personalized explanations based on actual plot data values
"""

import json
import requests
import pandas as pd
import numpy as np
import os
from typing import Dict, Any, Optional, List, Tuple
import sys

class RealTimeMicrobiomeAnalyzer:
    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "gpt-oss:20b"):
        self.ollama_url = ollama_url
        self.model = model
        self.api_url = f"{ollama_url}/api/generate"
        
        # Data file paths
        self.data_dir = "."
        self.metadata_file = "metadata.tsv"
        self.level_files = {
            2: "all_child-UC_kraken2_250616_level_2.tsv",
            3: "all_child-UC_kraken2_250616_level_3.tsv", 
            4: "all_child-UC_kraken2_250616_level_4.tsv",
            5: "all_child-UC_kraken2_250616_level_5.tsv",
            6: "all_child-UC_kraken2_250616_level_6.tsv",
            7: "all_child-UC_kraken2_250616_level_7.tsv"
        }
    
    def extract_alpha_diversity_data(self, taxonomic_level: str) -> Dict[str, float]:
        """
        Extract actual alpha diversity values from the data files
        """
        try:
            # Map taxonomic level to file level
            level_mapping = {
                "phylum": 2, "class": 3, "order": 4, 
                "family": 5, "genus": 6, "species": 7
            }
            
            level = level_mapping.get(taxonomic_level.lower(), 2)
            level_file = self.level_files.get(level)
            
            if not level_file or not os.path.exists(level_file):
                return {}
            
            # Read the data file
            df = pd.read_csv(level_file, sep='\t', index_col=0)
            
            # Calculate Shannon diversity for each sample
            diversity_data = {}
            for sample in df.columns:
                # Get abundances for this sample
                abundances = df[sample].values
                # Remove zeros and calculate Shannon diversity
                non_zero = abundances[abundances > 0]
                if len(non_zero) > 0:
                    # Normalize to proportions
                    proportions = non_zero / non_zero.sum()
                    # Calculate Shannon diversity: -sum(p * log(p))
                    shannon = -sum(p * (np.log(p) if p > 0 else 0) for p in proportions)
                    diversity_data[sample] = shannon
            
            return diversity_data
            
        except Exception as e:
            print(f"Error extracting alpha diversity data: {e}")
            return {}
    
    def extract_stacked_barplot_data(self, taxonomic_level: str) -> Tuple[List[str], Dict[str, List[float]]]:
        """
        Extract actual abundance data for stacked barplots
        """
        try:
            # Map taxonomic level to file level
            level_mapping = {
                "phylum": 2, "class": 3, "order": 4, 
                "family": 5, "genus": 6, "species": 7
            }
            
            level = level_mapping.get(taxonomic_level.lower(), 2)
            level_file = self.level_files.get(level)
            
            if not level_file or not os.path.exists(level_file):
                return [], {}
            
            # Read the data file
            df = pd.read_csv(level_file, sep='\t', index_col=0)
            
            # Get top 20 taxa by total abundance
            total_abundance = df.sum(axis=1)
            top_taxa = total_abundance.nlargest(20).index.tolist()
            
            # Get abundances for each sample
            abundances = {}
            for sample in df.columns:
                abundances[sample] = df.loc[top_taxa, sample].tolist()
            
            return top_taxa, abundances
            
        except Exception as e:
            print(f"Error extracting stacked barplot data: {e}")
            return [], {}
    
    def extract_pcoa_data(self, taxonomic_level: str) -> Dict[str, List[float]]:
        """
        Extract actual abundance data for PCoA analysis
        """
        try:
            # Map taxonomic level to file level
            level_mapping = {
                "phylum": 2, "class": 3, "order": 4, 
                "family": 5, "genus": 6, "species": 7
            }
            
            level = level_mapping.get(taxonomic_level.lower(), 2)
            level_file = self.level_files.get(level)
            
            if not level_file or not os.path.exists(level_file):
                return {}
            
            # Read the data file
            df = pd.read_csv(level_file, sep='\t', index_col=0)
            
            # Get abundances for each sample
            abundances = {}
            for sample in df.columns:
                abundances[sample] = df[sample].tolist()
            
            return abundances
            
        except Exception as e:
            print(f"Error extracting PCoA data: {e}")
            return {}
    
    def get_sample_metadata(self) -> Dict[str, str]:
        """
        Get sample metadata (Control vs UC)
        """
        try:
            if not os.path.exists(self.metadata_file):
                return {}
            
            df = pd.read_csv(self.metadata_file, sep='\t')
            metadata = {}
            
            for _, row in df.iterrows():
                sample_id = row.get('sample', '')
                condition = row.get('group', '')
                if sample_id and condition:
                    metadata[sample_id] = condition
            
            return metadata
            
        except Exception as e:
            print(f"Error reading metadata: {e}")
            return {}
    
    def calculate_taxa_control_uc_ratios(self, taxonomic_level: str) -> List[Dict[str, any]]:
        """
        Calculate Control/UC ratios for all taxa at a given taxonomic level
        
        Args:
            taxonomic_level: Taxonomic level (can be "phylum", "class", "order", "family", "genus", "species" 
                             or numeric levels "2", "3", "4", "5", "6", "7")
            
        Returns:
            List of dictionaries with taxon name and Control/UC ratio
        """
        try:
            # Map taxonomic level to file level (handle both string and numeric inputs)
            level_mapping = {
                # String inputs
                "phylum": 2, "class": 3, "order": 4, 
                "family": 5, "genus": 6, "species": 7,
                # Numeric inputs
                "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7
            }
            
            level = level_mapping.get(taxonomic_level.lower(), 2)
            level_file = self.level_files.get(level)
            
            if not level_file or not os.path.exists(level_file):
                return []
            
            # Read the data file
            df = pd.read_csv(level_file, sep='\t', index_col=0)
            
            # Get sample metadata
            metadata = self.get_sample_metadata()
            
            # Separate control vs UC samples
            control_samples = []
            uc_samples = []
            for sample in df.columns:
                condition = metadata.get(sample, 'Unknown')
                if 'control' in condition.lower():
                    control_samples.append(sample)
                else:
                    uc_samples.append(sample)
            
            # Calculate ratios for each taxon
            taxa_ratios = []
            
            for taxon in df.index:
                # Extract only the taxon name at the specified level
                # The taxon string format is: k__Kingdom|p__Phylum|c__Class|o__Order|f__Family|g__Genus|s__Species
                taxon_parts = taxon.split('|')
                
                # Find the part that corresponds to our level
                level_prefix = {
                    2: 'p__',  # phylum
                    3: 'c__',  # class
                    4: 'o__',  # order
                    5: 'f__',  # family
                    6: 'g__',  # genus
                    7: 's__'   # species
                }[level]
                
                # Extract the taxon name at this level
                level_taxon = None
                for part in taxon_parts:
                    if part.startswith(level_prefix):
                        level_taxon = part
                        break
                
                # If we can't find the level, try to extract a meaningful name
                if not level_taxon:
                    # Look for the highest available level in the path
                    available_prefixes = ['s__', 'g__', 'f__', 'o__', 'c__', 'p__']
                    for prefix in available_prefixes:
                        for part in taxon_parts:
                            if part.startswith(prefix):
                                level_taxon = part
                                break
                        if level_taxon:
                            break
                    
                    # If still no prefix found, use the last part of the path
                    if not level_taxon and taxon_parts:
                        level_taxon = taxon_parts[-1]
                
                # Clean up the taxon name for better readability
                if level_taxon:
                    # Remove the prefix and replace underscores with spaces for better readability
                    clean_name = level_taxon.split('__', 1)[-1] if '__' in level_taxon else level_taxon
                    clean_name = clean_name.replace('_', ' ')
                    level_taxon = clean_name
                
                # Get abundances for this taxon
                control_values = [df.loc[taxon, sample] for sample in control_samples if sample in df.columns]
                uc_values = [df.loc[taxon, sample] for sample in uc_samples if sample in df.columns]
                
                # Calculate averages
                control_avg = sum(control_values) / len(control_values) if control_values else 0
                uc_avg = sum(uc_values) / len(uc_values) if uc_values else 0
                
                # Calculate ratio (Control/UC)
                if uc_avg > 0:
                    ratio = control_avg / uc_avg
                else:
                    ratio = float('inf') if control_avg > 0 else 0
                
                # Add to results
                taxa_ratios.append({
                    'taxon': level_taxon,  # Use the extracted level-specific taxon name
                    'control_avg': control_avg,
                    'uc_avg': uc_avg,
                    'control_uc_ratio': ratio,
                    'control_samples_count': len(control_values),
                    'uc_samples_count': len(uc_values)
                })
            
            # Sort by ratio (highest to lowest)
            taxa_ratios.sort(key=lambda x: x['control_uc_ratio'], reverse=True)
            
            return taxa_ratios
            
        except Exception as e:
            print(f"Error calculating taxa ratios: {e}")
            return []
    
    def generate_taxa_comparison_tsv(self, taxonomic_level: str) -> str:
        """
        Generate TSV content for taxa comparison table
        
        Args:
            taxonomic_level: Taxonomic level (phylum, class, order, family, genus, species)
            
        Returns:
            TSV string content
        """
        try:
            taxa_ratios = self.calculate_taxa_control_uc_ratios(taxonomic_level)
            
            if not taxa_ratios:
                return ""
            
            # Create TSV header
            tsv_lines = [
                f"Taxon\tControl_Average\tUC_Average\tControl_UC_Ratio\tControl_Samples\tUC_Samples"
            ]
            
            # Add data rows
            for item in taxa_ratios:
                ratio_str = f"{item['control_uc_ratio']:.6f}" if item['control_uc_ratio'] != float('inf') else "Inf"
                tsv_lines.append(
                    f"{item['taxon']}\t{item['control_avg']:.6f}\t{item['uc_avg']:.6f}\t{ratio_str}\t{item['control_samples_count']}\t{item['uc_samples_count']}"
                )
            
            return "\n".join(tsv_lines)
            
        except Exception as e:
            print(f"Error generating TSV: {e}")
            return ""
    
    def generate_taxa_comparison_excel(self, taxonomic_level: str) -> bytes:
        """
        Generate Excel file for taxa comparison table
        
        Args:
            taxonomic_level: Taxonomic level (phylum, class, order, family, genus, species)
            
        Returns:
            Excel file as bytes
        """
        try:
            taxa_ratios = self.calculate_taxa_control_uc_ratios(taxonomic_level)
            
            if not taxa_ratios:
                return b""
            
            # Create DataFrame
            df = pd.DataFrame(taxa_ratios)
            
            # Reorder columns for better presentation
            df = df[['taxon', 'control_avg', 'uc_avg', 'control_uc_ratio', 'control_samples_count', 'uc_samples_count']]
            
            # Rename columns for clarity
            df.columns = ['Taxon', 'Control_Average', 'UC_Average', 'Control_UC_Ratio', 'Control_Samples', 'UC_Samples']
            
            # Create Excel writer
            from io import BytesIO
            output = BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=f'{taxonomic_level.title()}_Comparison', index=False)
                
                # Get the workbook and worksheet
                workbook = writer.book
                worksheet = writer.sheets[f'{taxonomic_level.title()}_Comparison']
                
                # Auto-adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            output.seek(0)
            return output.getvalue()
            
        except Exception as e:
            print(f"Error generating Excel: {e}")
            return b""

    def analyze_taxon_plot(self, taxon_name: str, sample_data: Dict[str, float], 
                          sample_names: list, rpm_values: list) -> str:
        """
        Generate personalized AI analysis for a specific taxon plot
        """
        # Create a detailed prompt with the actual data
        prompt = self._create_taxon_analysis_prompt(taxon_name, sample_data, sample_names, rpm_values)
        
        try:
            response = self._call_ollama(prompt)
            return response
        except Exception as e:
            return self._generate_fallback_analysis(taxon_name, sample_data, sample_names, rpm_values)
    
    def analyze_diversity_plot(self, plot_type: str, diversity_data: Dict[str, float]) -> str:
        """
        Generate personalized AI analysis for diversity plots
        """
        prompt = self._create_diversity_analysis_prompt(plot_type, diversity_data)
        
        try:
            response = self._call_ollama(prompt)
            return response
        except Exception as e:
            return self._generate_fallback_diversity_analysis(plot_type, diversity_data)
    
    def analyze_stacked_plot(self, plot_type: str, top_taxa: list, abundances: Dict[str, list]) -> str:
        """
        Generate personalized AI analysis for stacked bar plots
        """
        prompt = self._create_stacked_analysis_prompt(plot_type, top_taxa, abundances)
        
        try:
            response = self._call_ollama(prompt)
            return response
        except Exception as e:
            return self._generate_fallback_stacked_analysis(plot_type, top_taxa, abundances)
    
    def analyze_pcoa_plot(self, plot_type: str, abundances: Dict[str, list]) -> str:
        """
        Generate personalized AI analysis for PCoA plots
        """
        prompt = self._create_pcoa_analysis_prompt(plot_type, abundances)
        
        try:
            response = self._call_ollama(prompt)
            return response
        except Exception as e:
            return self._generate_fallback_pcoa_analysis(plot_type, abundances)
    
    def _create_taxon_analysis_prompt(self, taxon_name: str, sample_data: Dict[str, float], 
                                    sample_names: list, rpm_values: list) -> str:
        """
        Create a detailed prompt for taxon-specific analysis
        """
        # Find control vs UC samples
        control_samples = [name for name in sample_names if 'ctrl' in name.lower() or 'control' in name.lower()]
        uc_samples = [name for name in sample_names if name not in control_samples]
        
        # Calculate statistics
        control_values = [sample_data.get(name, 0) for name in control_samples if name in sample_data]
        uc_values = [sample_data.get(name, 0) for name in uc_samples if name in sample_data]
        
        control_avg = sum(control_values) / len(control_values) if control_values else 0
        uc_avg = sum(uc_values) / len(uc_values) if uc_values else 0
        
        max_value = max(rpm_values) if rpm_values else 0
        min_value = min(rpm_values) if rpm_values else 0
        
        prompt = f"""
You are a microbiome expert explaining results to patients in simple terms. Analyze this specific data:

TAXON: {taxon_name}
SAMPLE DATA: {json.dumps(sample_data, indent=2)}
SAMPLE NAMES: {sample_names}
RPM VALUES: {rpm_values}

CONTROL SAMPLES: {control_samples} (Average: {control_avg:.3f} RPM)
UC SAMPLES: {uc_samples} (Average: {uc_avg:.3f} RPM)
RANGE: {min_value:.3f} to {max_value:.3f} RPM

Provide a personalized analysis that:
1. Mentions the specific taxon name
2. References actual RPM values and sample names
3. Compares control vs UC samples with specific numbers
4. Explains what the differences might mean in simple terms
5. Gives actionable insights for patients

Keep it under 150 words, simple language, and focus on the specific data provided.
"""
        return prompt
    
    def _create_diversity_analysis_prompt(self, plot_type: str, diversity_data: Dict[str, float]) -> str:
        """
        Create a detailed prompt for diversity plot analysis
        """
        # Calculate statistics
        values = list(diversity_data.values())
        avg_diversity = sum(values) / len(values) if values else 0
        max_diversity = max(values) if values else 0
        min_diversity = min(values) if values else 0
        
        # Get sample metadata
        metadata = self.get_sample_metadata()
        
        # Separate control vs UC samples
        control_samples = []
        uc_samples = []
        for sample, diversity in diversity_data.items():
            condition = metadata.get(sample, 'Unknown')
            if 'control' in condition.lower():
                control_samples.append((sample, diversity))
            else:
                uc_samples.append((sample, diversity))
        
        control_avg = sum(d for _, d in control_samples) / len(control_samples) if control_samples else 0
        uc_avg = sum(d for _, d in uc_samples) / len(uc_samples) if uc_samples else 0
        
        prompt = f"""
You are a microbiome expert explaining diversity results to patients in simple terms. Analyze this specific data:

PLOT TYPE: {plot_type}
DIVERSITY DATA: {json.dumps(diversity_data, indent=2)}
AVERAGE DIVERSITY: {avg_diversity:.3f}
RANGE: {min_diversity:.3f} to {max_diversity:.3f}

CONTROL SAMPLES: {[s[0] for s in control_samples]} (Average: {control_avg:.3f})
UC SAMPLES: {[s[0] for s in uc_samples]} (Average: {uc_avg:.3f})

Provide a personalized analysis that:
1. Explains what {plot_type} diversity means
2. References actual diversity values and sample names
3. Compares control vs UC samples with specific numbers
4. Explains what the differences might mean for gut health
5. Stress the importance of a diverse microbiome

Keep it under 200 words, simple language, and focus on the specific data provided.
"""
        return prompt
    
    def _create_stacked_analysis_prompt(self, plot_type: str, top_taxa: list, abundances: Dict[str, list]) -> str:
        """
        Create a detailed prompt for stacked bar plot analysis
        """
        # Get sample metadata
        metadata = self.get_sample_metadata()
        
        # Calculate total abundances for each taxon
        taxon_totals = {}
        for i, taxon in enumerate(top_taxa):
            total = sum(abundances[sample][i] for sample in abundances if i < len(abundances[sample]))
            taxon_totals[taxon] = total
        
        # Get top 5 most abundant taxa
        top_5_taxa = sorted(taxon_totals.items(), key=lambda x: x[1], reverse=True)[:5]
        
        prompt = f"""
You are a microbiome expert explaining microbiome composition results to patients in simple terms. Analyze this specific data:

PLOT TYPE: {plot_type}
TOP TAXA: {top_taxa}
TOP 5 MOST ABUNDANT: {top_5_taxa}
SAMPLE ABUNDANCES: {json.dumps(abundances, indent=2)}

Provide a personalized analysis that:
1. Explains what this {plot_type} plot shows
2. Mentions specific taxa names from the data
3. References actual abundance values
4. Explains what the patterns might mean for gut health
5. Establish a brief comparisson of taxa abundance between control and UC samples

Keep it under 200 words, simple language, and focus on the specific data provided.
"""
        return prompt
    
    def _create_pcoa_analysis_prompt(self, plot_type: str, abundances: Dict[str, list]) -> str:
        """
        Create a detailed prompt for PCoA plot analysis
        """
        # Get sample metadata
        metadata = self.get_sample_metadata()
        
        # Separate control vs UC samples
        control_samples = []
        uc_samples = []
        for sample in abundances.keys():
            condition = metadata.get(sample, 'Unknown')
            if 'control' in condition.lower():
                control_samples.append(sample)
            else:
                uc_samples.append(sample)
        
        prompt = f"""
You are a microbiome expert explaining PCoA results to patients in simple terms. Analyze this specific data:

PLOT TYPE: {plot_type}
CONTROL SAMPLES: {control_samples}
UC SAMPLES: {uc_samples}
ABUNDANCE DATA: {json.dumps(abundances, indent=2)}

Provide a personalized analysis that:
1. Explains what this PCoA plot shows
2. References the specific samples and their groups
3. Explains what the patterns might mean for gut health
4. Gives actionable insights for patients

Keep it under 150 words, simple language, and focus on the specific data provided.
"""
        return prompt
    
    def _call_ollama(self, prompt: str) -> str:
        """
        Call the Ollama API to generate AI analysis
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 300
            }
        }
        
        response = requests.post(self.api_url, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return result.get('response', '').strip()
    
    def _generate_fallback_analysis(self, taxon_name: str, sample_data: Dict[str, float], 
                                  sample_names: list, rpm_values: list) -> str:
        """
        Generate a fallback analysis when AI is unavailable
        """
        control_samples = [name for name in sample_names if 'ctrl' in name.lower() or 'control' in name.lower()]
        uc_samples = [name for name in sample_names if name not in control_samples]
        
        control_values = [sample_data.get(name, 0) for name in control_samples if name in sample_data]
        uc_values = [sample_data.get(name, 0) for name in uc_samples if name in sample_data]
        
        control_avg = sum(control_values) / len(control_values) if control_values else 0
        uc_avg = sum(uc_values) / len(uc_values) if uc_values else 0
        
        return f"""This plot shows {taxon_name} abundance across your samples. 

Control samples show an average of {control_avg:.3f} RPM, while UC samples show {uc_avg:.3f} RPM. 

The difference suggests {taxon_name} may be {'higher' if uc_avg > control_avg else 'lower'} in your condition compared to healthy controls. This could indicate changes in your gut microbiome that may be related to your health status.

Consult with your healthcare provider about what these specific levels mean for your individual case."""
    
    def _generate_fallback_diversity_analysis(self, plot_type: str, diversity_data: Dict[str, float]) -> str:
        """
        Generate a fallback analysis for diversity plots
        """
        values = list(diversity_data.values())
        avg_diversity = sum(values) / len(values) if values else 0
        
        # Get sample metadata
        metadata = self.get_sample_metadata()
        
        # Separate control vs UC samples
        control_samples = []
        uc_samples = []
        for sample, diversity in diversity_data.items():
            condition = metadata.get(sample, 'Unknown')
            if 'control' in condition.lower():
                control_samples.append((sample, diversity))
            else:
                uc_samples.append((sample, diversity))
        
        control_avg = sum(d for _, d in control_samples) / len(control_samples) if control_samples else 0
        uc_avg = sum(d for _, d in uc_samples) / len(uc_samples) if uc_samples else 0
        
        return f"""This {plot_type} diversity plot shows how diverse your gut microbiome is across samples.

Your average diversity is {avg_diversity:.3f}. {'Higher diversity generally indicates a healthier, more balanced microbiome.' if avg_diversity > 3.0 else 'Lower diversity may suggest your microbiome needs support to become more balanced.'}

Control samples show an average diversity of {control_avg:.3f}, while UC samples show {uc_avg:.3f}. This comparison helps identify how your condition may affect microbiome diversity.

The specific values for each sample help identify which areas of your gut may need attention. Discuss these results with your healthcare provider for personalized recommendations."""
    
    def _generate_fallback_stacked_analysis(self, plot_type: str, top_taxa: list, abundances: Dict[str, list]) -> str:
        """
        Generate a fallback analysis for stacked plots
        """
        # Calculate total abundances for each taxon
        taxon_totals = {}
        for i, taxon in enumerate(top_taxa):
            total = sum(abundances[sample][i] for sample in abundances if i < len(abundances[sample]))
            taxon_totals[taxon] = total
        
        # Get top 5 most abundant taxa
        top_5_taxa = sorted(taxon_totals.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return f"""This {plot_type} plot shows the composition of your gut microbiome, highlighting the most abundant bacteria groups.

The top taxa in your samples include: {', '.join([t[0] for t in top_5_taxa])}.

This visualization helps identify which bacteria are dominant in your gut and how they compare between samples. The patterns can reveal important information about your microbiome balance and health status.

Discuss these specific results with your healthcare provider for personalized insights."""
    
    def _generate_fallback_pcoa_analysis(self, plot_type: str, abundances: Dict[str, list]) -> str:
        """
        Generate a fallback analysis for PCoA plots
        """
        # Get sample metadata
        metadata = self.get_sample_metadata()
        
        # Separate control vs UC samples
        control_samples = []
        uc_samples = []
        for sample in abundances.keys():
            condition = metadata.get(sample, 'Unknown')
            if 'control' in condition.lower():
                control_samples.append(sample)
            else:
                uc_samples.append(sample)
        
        return f"""This PCoA plot shows how similar or different your microbiome is compared to others.

Control samples: {', '.join(control_samples)}
UC samples: {', '.join(uc_samples)}

This visualization helps identify if people with the same health condition have similar gut microbiomes, which could help develop treatments or understand how the disease affects the gut.

The plot shows the relationships between samples based on their microbial composition, helping to identify patterns that may be related to health status."""

def main():
    """
    Test the real-time analyzer
    """
    analyzer = RealTimeMicrobiomeAnalyzer()
    
    # Test data
    test_data = {
        "PedCtrl59": 0.01,
        "SRR15702647": 0.23,
        "SRR15702658": 0.38,
        "SRR15702659": 0.31,
        "SRR15702660": 0.29
    }
    
    sample_names = ["PedCtrl59", "SRR15702647", "SRR15702658", "SRR15702659", "SRR15702660"]
    rpm_values = [0.01, 0.23, 0.38, 0.31, 0.29]
    
    print("Testing Real-Time AI Analyzer...")
    print("=" * 50)
    
    try:
        result = analyzer.analyze_taxon_plot("Acetobacteraceae", test_data, sample_names, rpm_values)
        print("AI Analysis Result:")
        print(result)
    except Exception as e:
        print(f"Error: {e}")
        print("Fallback analysis:")
        fallback = analyzer._generate_fallback_analysis("Acetobacteraceae", test_data, sample_names, rpm_values)
        print(fallback)
    
    # Test diversity data extraction
    print("\n" + "=" * 50)
    print("Testing Diversity Data Extraction...")
    
    diversity_data = analyzer.extract_alpha_diversity_data("phylum")
    if diversity_data:
        print("Alpha diversity data extracted:")
        for sample, diversity in diversity_data.items():
            print(f"  {sample}: {diversity:.3f}")
        
        print("\nGenerating AI analysis for diversity...")
        try:
            result = analyzer.analyze_diversity_plot("alpha_diversity", diversity_data)
            print("AI Diversity Analysis:")
            print(result)
        except Exception as e:
            print(f"Error: {e}")
            fallback = analyzer._generate_fallback_diversity_analysis("alpha_diversity", diversity_data)
            print("Fallback diversity analysis:")
            print(fallback)
    else:
        print("No diversity data found")

if __name__ == "__main__":
    main()

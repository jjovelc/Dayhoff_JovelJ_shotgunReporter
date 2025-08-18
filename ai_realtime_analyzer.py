#!/usr/bin/env python3
"""
Real-time AI Analyzer for Microbiome Plots
Generates personalized explanations based on actual plot data values
"""

import json
import requests
from typing import Dict, Any, Optional
import sys
import os

class RealTimeMicrobiomeAnalyzer:
    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "gpt-oss:20b"):
        self.ollama_url = ollama_url
        self.model = model
        self.api_url = f"{ollama_url}/api/generate"
    
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
        
        prompt = f"""
You are a microbiome expert explaining diversity results to patients in simple terms. Analyze this specific data:

PLOT TYPE: {plot_type}
DIVERSITY DATA: {json.dumps(diversity_data, indent=2)}
AVERAGE DIVERSITY: {avg_diversity:.3f}
RANGE: {min_diversity:.3f} to {max_diversity:.3f}

Provide a personalized analysis that:
1. Explains what {plot_type} diversity means
2. References actual diversity values and sample names
3. Compares samples with specific numbers
4. Explains what the differences might mean for gut health
5. Gives actionable insights for patients

Keep it under 150 words, simple language, and focus on the specific data provided.
"""
        return prompt
    
    def _create_stacked_analysis_prompt(self, plot_type: str, top_taxa: list, abundances: Dict[str, list]) -> str:
        """
        Create a detailed prompt for stacked bar plot analysis
        """
        prompt = f"""
You are a microbiome expert explaining microbiome composition results to patients in simple terms. Analyze this specific data:

PLOT TYPE: {plot_type}
TOP TAXA: {top_taxa}
ABUNDANCES: {json.dumps(abundances, indent=2)}

Provide a personalized analysis that:
1. Explains what this {plot_type} plot shows
2. Mentions specific taxa names from the data
3. References actual abundance values
4. Explains what the patterns might mean for gut health
5. Gives actionable insights for patients

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
        
        return f"""This {plot_type} diversity plot shows how diverse your gut microbiome is across samples.

Your average diversity is {avg_diversity:.3f}. {'Higher diversity generally indicates a healthier, more balanced microbiome.' if avg_diversity > 3.0 else 'Lower diversity may suggest your microbiome needs support to become more balanced.'}

The specific values for each sample help identify which areas of your gut may need attention. Discuss these results with your healthcare provider for personalized recommendations."""
    
    def _generate_fallback_stacked_analysis(self, plot_type: str, top_taxa: list, abundances: Dict[str, list]) -> str:
        """
        Generate a fallback analysis for stacked plots
        """
        return f"""This {plot_type} plot shows the composition of your gut microbiome, highlighting the most abundant bacteria groups.

The top taxa in your samples include: {', '.join(top_taxa[:5])}.

This visualization helps identify which bacteria are dominant in your gut and how they compare between samples. The patterns can reveal important information about your microbiome balance and health status.

Discuss these specific results with your healthcare provider for personalized insights."""

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

if __name__ == "__main__":
    main()

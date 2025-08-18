#!/usr/bin/env python3
"""
CGI endpoint for real-time AI analysis of microbiome plots
"""

import cgi
import cgitb
import json
import sys
import os
import requests
from typing import Dict, Any

# Add parent directory to path to import our analyzer
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from ai_realtime_analyzer import RealTimeMicrobiomeAnalyzer
except ImportError:
    # Fallback if import fails
    class RealTimeMicrobiomeAnalyzer:
        def __init__(self):
            pass
        
        def analyze_taxon_plot(self, taxon_name, sample_data, sample_names, rpm_values):
            return self._generate_fallback_analysis(taxon_name, sample_data, sample_names, rpm_values)
        
        def _generate_fallback_analysis(self, taxon_name, sample_data, sample_names, rpm_values):
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

def main():
    """Main CGI function"""
    # Enable CGI error reporting
    cgitb.enable()
    
    # Set content type
    print("Content-Type: application/json")
    print()
    
    try:
        # Parse form data
        form = cgi.FieldStorage()
        
        # Get parameters
        plot_type = form.getvalue('plot_type', '')
        taxon_name = form.getvalue('taxon_name', '')
        
        # Initialize analyzer
        analyzer = RealTimeMicrobiomeAnalyzer()
        
        if plot_type == 'taxon_plot' and taxon_name:
            # For taxon plots, we need to get the actual data
            # This would typically come from the frontend with the current plot data
            # For now, we'll use a placeholder approach
            
            # Get sample data from form (frontend should send this)
            sample_data_json = form.getvalue('sample_data', '{}')
            sample_names_json = form.getvalue('sample_names', '[]')
            rpm_values_json = form.getvalue('rpm_values', '[]')
            
            try:
                sample_data = json.loads(sample_data_json)
                sample_names = json.loads(sample_names_json)
                rpm_values = json.loads(rpm_values_json)
            except json.JSONDecodeError:
                # Fallback to empty data
                sample_data = {}
                sample_names = []
                rpm_values = []
            
            # Generate analysis
            analysis = analyzer.analyze_taxon_plot(taxon_name, sample_data, sample_names, rpm_values)
            
            response = {
                'success': True,
                'analysis': analysis,
                'plot_type': plot_type,
                'taxon_name': taxon_name
            }
            
        elif plot_type in ['alpha_diversity', 'beta_diversity']:
            # For diversity plots
            diversity_data_json = form.getvalue('diversity_data', '{}')
            
            try:
                diversity_data = json.loads(diversity_data_json)
            except json.JSONDecodeError:
                diversity_data = {}
            
            analysis = analyzer.analyze_diversity_plot(plot_type, diversity_data)
            
            response = {
                'success': True,
                'analysis': analysis,
                'plot_type': plot_type
            }
            
        elif plot_type in ['stacked_barplot']:
            # For stacked bar plots
            top_taxa_json = form.getvalue('top_taxa', '[]')
            abundances_json = form.getvalue('abundances', '{}')
            
            try:
                top_taxa = json.loads(top_taxa_json)
                abundances = json.loads(abundances_json)
            except json.JSONDecodeError:
                top_taxa = []
                abundances = {}
            
            analysis = analyzer.analyze_stacked_plot(plot_type, top_taxa, abundances)
            
            response = {
                'success': True,
                'analysis': analysis,
                'plot_type': plot_type
            }
            
        else:
            response = {
                'success': False,
                'error': 'Invalid plot type or missing parameters'
            }
        
        # Return JSON response
        print(json.dumps(response))
        
    except Exception as e:
        # Error response
        error_response = {
            'success': False,
            'error': str(e),
            'type': 'server_error'
        }
        print(json.dumps(error_response))

if __name__ == "__main__":
    main()

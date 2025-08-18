#!/usr/bin/env python3
"""
AI Plot Explainer for Gut Microbiome Reports
Integrates with gpt-oss:20b to generate simple explanations for customers
"""

import os
import json
import requests
from typing import Dict, List, Optional
import base64
from pathlib import Path

class MicrobiomePlotExplainer:
    """
    AI-powered plot explanation system for gut microbiome reports
    Generates simple, layman-friendly explanations using gpt-oss:20b
    """
    
    def __init__(self, api_base: str = "http://localhost:11434", model: str = "gpt-oss:20b"):
        """
        Initialize the plot explainer
        
        Args:
            api_base: Base URL for the Ollama API
            model: Model name to use for explanations
        """
        self.api_base = api_base
        self.model = model
        self.api_url = f"{api_base}/api/generate"
        
        # Plot type descriptions for context
        self.plot_types = {
            "stacked_barplot": "shows the relative abundance of different bacteria types",
            "alpha_diversity": "shows how diverse your gut bacteria community is",
            "pcoa": "shows how similar or different your microbiome is compared to others",
            "krona": "shows the complete family tree of bacteria found in your gut"
        }
        
        # Taxonomic level explanations
        self.taxonomic_levels = {
            "phylum": "major groups of bacteria (like animal families)",
            "class": "subgroups within major bacterial families",
            "order": "specific types within bacterial classes",
            "family": "closely related bacterial groups",
            "genus": "very similar bacterial types",
            "species": "individual bacterial strains"
        }
    
    def encode_image(self, image_path: str) -> str:
        """Encode image to base64 for API transmission"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"Error encoding image {image_path}: {e}")
            return ""
    
    def generate_plot_explanation(self, plot_path: str, plot_type: str, 
                                taxonomic_level: Optional[str] = None) -> str:
        """
        Generate a simple explanation for a microbiome plot
        
        Args:
            plot_path: Path to the plot image
            plot_type: Type of plot (stacked_barplot, alpha_diversity, pcoa, krona)
            taxonomic_level: Taxonomic level if applicable
            
        Returns:
            Simple explanation text for customers
        """
        
        # Create the prompt for the AI model
        prompt = self._create_explanation_prompt(plot_type, taxonomic_level)
        
        # Prepare the API request
        request_data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 300
            }
        }
        
        try:
            # Make the API call
            response = requests.post(self.api_url, json=request_data, timeout=30)
            response.raise_for_status()
            
            # Extract the response
            result = response.json()
            explanation = result.get('response', '').strip()
            
            # Clean up the explanation
            explanation = self._clean_explanation(explanation)
            
            return explanation
            
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return self._generate_fallback_explanation(plot_type, taxonomic_level)
        except Exception as e:
            print(f"Error generating explanation: {e}")
            return self._generate_fallback_explanation(plot_type, taxonomic_level)
    
    def _create_explanation_prompt(self, plot_type: str, taxonomic_level: Optional[str] = None) -> str:
        """Create a prompt for the AI model"""
        
        base_prompt = f"""
You are a helpful assistant that explains microbiome science to customers in simple, easy-to-understand language.

Your task is to explain a {plot_type} plot that shows gut microbiome data.

Key requirements:
- Use simple, everyday language (high school reading level)
- Avoid scientific jargon
- Use relatable analogies when possible
- Keep explanations under 3 sentences
- Focus on what the customer needs to know
- Be encouraging and positive

Plot type: {plot_type}
"""
        
        if taxonomic_level:
            base_prompt += f"Taxonomic level: {taxonomic_level} ({self.taxonomic_levels.get(taxonomic_level, '')})\n"
        
        base_prompt += f"""
Please explain what this {plot_type} plot shows in simple terms that anyone can understand.

Your explanation should help the customer understand:
1. What they're looking at
2. What it means for their health
3. Why it's important

Keep it friendly and educational!
"""
        
        return base_prompt.strip()
    
    def _clean_explanation(self, explanation: str) -> str:
        """Clean and format the AI-generated explanation"""
        # Remove any markdown formatting
        explanation = explanation.replace('**', '').replace('*', '')
        
        # Remove any quotes
        explanation = explanation.replace('"', '').replace('"', '').replace("'", '')
        
        # Ensure it ends with proper punctuation
        if explanation and not explanation.endswith(('.', '!', '?')):
            explanation += '.'
        
        return explanation
    
    def _generate_fallback_explanation(self, plot_type: str, taxonomic_level: Optional[str] = None) -> str:
        """Generate a fallback explanation if AI fails"""
        
        fallback_explanations = {
            "stacked_barplot": f"This chart shows the different types of bacteria found in your gut. The bigger each bar is, the more of that bacteria type you have. This helps us understand what's living in your digestive system.",
            "alpha_diversity": "This chart shows how diverse your gut bacteria community is. Think of it like having a variety of different plants in a garden - more variety is generally better for your health.",
            "pcoa": "This chart shows how similar or different your microbiome is compared to other people. It helps us see if your gut bacteria pattern is typical or unique.",
            "krona": "This interactive chart shows the complete family tree of bacteria found in your gut. It's like a map of all the tiny organisms living in your digestive system."
        }
        
        base_explanation = fallback_explanations.get(plot_type, "This chart shows important information about your gut microbiome.")
        
        if taxonomic_level:
            level_desc = self.taxonomic_levels.get(taxonomic_level, "")
            if level_desc:
                base_explanation += f" We're looking at the {taxonomic_level} level, which represents {level_desc}."
        
        return base_explanation
    
    def generate_all_plot_explanations(self, plots_directory: str = ".") -> Dict[str, str]:
        """
        Generate explanations for all microbiome plots in the directory
        
        Args:
            plots_directory: Directory containing plot images
            
        Returns:
            Dictionary mapping plot filenames to explanations
        """
        explanations = {}
        
        # Find all plot files
        plot_files = []
        for ext in ['*.png', '*.jpg', '*.jpeg']:
            plot_files.extend(Path(plots_directory).glob(ext))
        
        for plot_file in plot_files:
            filename = plot_file.name
            
            # Determine plot type and taxonomic level
            plot_type, taxonomic_level = self._classify_plot(filename)
            
            print(f"Generating explanation for: {filename}")
            explanation = self.generate_plot_explanation(
                str(plot_file), plot_type, taxonomic_level
            )
            
            explanations[filename] = {
                "plot_type": plot_type,
                "taxonomic_level": taxonomic_level,
                "explanation": explanation
            }
        
        return explanations
    
    def _classify_plot(self, filename: str) -> tuple:
        """Classify a plot based on its filename"""
        filename_lower = filename.lower()
        
        # Determine plot type
        if "stacked_barplot" in filename_lower:
            plot_type = "stacked_barplot"
        elif "alpha_diversity" in filename_lower:
            plot_type = "alpha_diversity"
        elif "pcoa" in filename_lower:
            plot_type = "pcoa"
        elif "krona" in filename_lower:
            plot_type = "krona"
        else:
            plot_type = "unknown"
        
        # Determine taxonomic level
        taxonomic_level = None
        for level in self.taxonomic_levels.keys():
            if level in filename_lower:
                taxonomic_level = level
                break
        
        return plot_type, taxonomic_level
    
    def save_explanations(self, explanations: Dict[str, dict], output_file: str = "plot_explanations.json"):
        """Save explanations to a JSON file"""
        try:
            with open(output_file, 'w') as f:
                json.dump(explanations, f, indent=2)
            print(f"Explanations saved to {output_file}")
        except Exception as e:
            print(f"Error saving explanations: {e}")
    
    def create_html_report(self, explanations: Dict[str, dict], output_file: str = "ai_explained_report.html"):
        """Create an HTML report with AI explanations"""
        
        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your Gut Microbiome Report - AI Explained</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; text-align: center; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
        .plot-section { margin: 30px 0; padding: 20px; border: 1px solid #ddd; border-radius: 8px; background: #fafafa; }
        .plot-title { font-size: 1.2em; font-weight: bold; color: #34495e; margin-bottom: 10px; }
        .plot-explanation { background: #e8f4fd; padding: 15px; border-radius: 5px; border-left: 4px solid #3498db; }
        .plot-type { color: #7f8c8d; font-size: 0.9em; margin-bottom: 5px; }
        .plot-image { text-align: center; margin: 15px 0; }
        .plot-image img { max-width: 100%; height: auto; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }
        .intro { background: #e8f5e8; padding: 20px; border-radius: 8px; margin-bottom: 30px; border-left: 4px solid #27ae60; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧬 Your Gut Microbiome Report</h1>
        
        <div class="intro">
            <h2>Welcome to Your Microbiome Journey!</h2>
            <p>This report uses AI to explain your gut microbiome results in simple, easy-to-understand language. 
            Think of your gut as a tiny ecosystem - we're here to help you understand what's living there and what it means for your health!</p>
        </div>
"""
        
        for filename, data in explanations.items():
            plot_type = data.get("plot_type", "unknown")
            taxonomic_level = data.get("taxonomic_level", "")
            explanation = data.get("explanation", "")
            
            # Create a nice title
            title = filename.replace("_", " ").replace(".png", "").title()
            if taxonomic_level:
                title = f"{taxonomic_level.title()} Level - {title}"
            
            html_content += f"""
        <div class="plot-section">
            <div class="plot-type">📊 {plot_type.replace('_', ' ').title()}</div>
            <div class="plot-title">{title}</div>
            <div class="plot-explanation">
                <strong>🤖 AI Explanation:</strong><br>
                {explanation}
            </div>
            <div class="plot-image">
                <img src="{filename}" alt="{title}" title="{title}">
            </div>
        </div>
"""
        
        html_content += """
    </div>
</body>
</html>
"""
        
        try:
            with open(output_file, 'w') as f:
                f.write(html_content)
            print(f"HTML report created: {output_file}")
        except Exception as e:
            print(f"Error creating HTML report: {e}")


def main():
    """Main function to demonstrate the AI plot explainer"""
    
    # Initialize the explainer
    explainer = MicrobiomePlotExplainer()
    
    print("🧬 AI Microbiome Plot Explainer")
    print("=" * 50)
    
    # Check if Ollama is running
    try:
        response = requests.get(f"{explainer.api_base}/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama API is accessible")
        else:
            print("❌ Ollama API returned an error")
            return
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to Ollama API. Please ensure Ollama is running.")
        print("   You can start it with: ollama serve")
        return
    
    # Generate explanations for all plots
    print("\n🔍 Scanning for microbiome plots...")
    explanations = explainer.generate_all_plot_explanations()
    
    if explanations:
        print(f"\n✅ Generated explanations for {len(explanations)} plots")
        
        # Save explanations to JSON
        explainer.save_explanations(explanations)
        
        # Create HTML report
        explainer.create_html_report(explanations)
        
        print("\n📊 Sample explanations:")
        for filename, data in list(explanations.items())[:3]:
            print(f"\n{filename}:")
            print(f"  {data['explanation']}")
    else:
        print("❌ No plot files found in the current directory")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Demo script for AI Microbiome Plot Explainer
Shows customers how to use the system
"""

import json
import webbrowser
from pathlib import Path

def demo_ai_explainer():
    """Demonstrate the AI explainer system"""
    
    print("🧬 AI Microbiome Plot Explainer - Customer Demo")
    print("=" * 60)
    
    # Check if AI explanations exist
    if not Path("plot_explanations.json").exists():
        print("❌ No AI explanations found!")
        print("Please run 'python ai_plot_explainer.py' first to generate explanations.")
        return
    
    # Load explanations
    try:
        with open("plot_explanations.json", 'r') as f:
            explanations = json.load(f)
        print(f"✅ Loaded {len(explanations)} AI-generated explanations")
    except Exception as e:
        print(f"❌ Error loading explanations: {e}")
        return
    
    # Show sample explanations
    print("\n📊 Sample AI Explanations:")
    print("-" * 40)
    
    # Get first few explanations
    sample_files = list(explanations.keys())[:3]
    
    for filename in sample_files:
        data = explanations[filename]
        plot_type = data.get("plot_type", "unknown")
        taxonomic_level = data.get("taxonomic_level", "")
        explanation = data.get("explanation", "")
        
        print(f"\n📈 {filename}")
        print(f"   Type: {plot_type.replace('_', ' ').title()}")
        if taxonomic_level:
            print(f"   Level: {taxonomic_level.title()}")
        print(f"   Explanation: {explanation[:100]}...")
    
    # Check if HTML report exists
    if Path("ai_explained_report.html").exists():
        print(f"\n🌐 HTML Report Available!")
        print("   File: ai_explained_report.html")
        
        # Ask if user wants to open it
        try:
            response = input("\nWould you like to open the HTML report in your browser? (y/n): ").lower()
            if response in ['y', 'yes']:
                print("Opening report in browser...")
                webbrowser.open("ai_explained_report.html")
            else:
                print("You can open the report manually by double-clicking 'ai_explained_report.html'")
        except KeyboardInterrupt:
            print("\n\nReport can be opened manually by double-clicking 'ai_explained_report.html'")
    else:
        print("\n❌ HTML report not found")
        print("Please run 'python ai_plot_explainer.py' to generate the report")
    
    # Show usage instructions
    print("\n📖 How to Use This System:")
    print("-" * 40)
    print("1. Run the AI explainer: python ai_plot_explainer.py")
    print("2. View explanations in: plot_explanations.json")
    print("3. Open customer report: ai_explained_report.html")
    print("4. Share the HTML report with customers")
    
    print("\n🎯 What This Means for Your Customers:")
    print("-" * 40)
    print("• Complex microbiome plots become easy to understand")
    print("• Professional, customer-friendly explanations")
    print("• No need for customers to understand scientific jargon")
    print("• Beautiful, shareable HTML reports")
    print("• Local AI processing ensures data privacy")

def show_plot_types():
    """Show what types of plots the system can explain"""
    
    print("\n🔍 Supported Plot Types:")
    print("-" * 30)
    
    plot_types = {
        "stacked_barplot": "Shows relative abundance of bacteria types",
        "alpha_diversity": "Shows microbial community diversity",
        "pcoa": "Shows sample similarity/differences",
        "krona": "Shows taxonomic hierarchies"
    }
    
    for plot_type, description in plot_types.items():
        print(f"• {plot_type.replace('_', ' ').title()}: {description}")
    
    print("\n📊 Taxonomic Levels Supported:")
    print("-" * 35)
    
    levels = ["phylum", "class", "order", "family", "genus", "species"]
    for level in levels:
        print(f"• {level.title()}")

if __name__ == "__main__":
    demo_ai_explainer()
    show_plot_types()
    
    print("\n🎉 Demo complete!")
    print("Your AI-powered microbiome reporter is ready to help customers understand their results!")

#!/usr/bin/env python3
"""
CGI script for generating AI-powered summary reports
"""

import cgi
import json
import sys
import os
import base64
from io import BytesIO

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from ai_realtime_analyzer import RealTimeMicrobiomeAnalyzer
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import seaborn as sns
    import numpy as np
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    import pandas as pd
except ImportError as e:
    print(f"Content-Type: application/json")
    print()
    print(json.dumps({"success": False, "error": f"Import error: {e}"}))
    sys.exit(1)

def generate_diversity_plot(analyzer, taxonomic_level):
    """Generate diversity comparison plot"""
    try:
        plot_data = analyzer.generate_diversity_plot(taxonomic_level)
        
        if not plot_data:
            return None
            
        # Create the plot
        plt.figure(figsize=(10, 6))
        
        # Bar plot for diversity comparison
        bars = plt.bar(plot_data['labels'], plot_data['diversity_values'], 
                      color=['#3b82f6', '#ef4444'], alpha=0.8)
        
        # Add value labels on bars
        for bar, value in zip(bars, plot_data['diversity_values']):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{value:.3f}', ha='center', va='bottom', fontweight='bold')
        
        plt.title(f'Shannon Diversity Comparison - {taxonomic_level.title()} Level', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.ylabel('Shannon Diversity Index', fontsize=12)
        plt.xlabel('Sample Group', fontsize=12)
        plt.ylim(0, max(plot_data['diversity_values']) * 1.2)
        
        # Add sample count annotations
        for i, (label, count) in enumerate(zip(plot_data['labels'], plot_data['sample_counts'])):
            plt.text(i, 0.05, f'n={count}', ha='center', va='bottom', 
                    fontsize=10, style='italic')
        
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        
        # Save to bytes
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer.getvalue()
        
    except Exception as e:
        print(f"Error generating diversity plot: {e}", file=sys.stderr)
        return None

def generate_heatmap(analyzer, taxonomic_level):
    """Generate heatmap for top 20 most distinct taxa"""
    try:
        heatmap_data = analyzer.generate_heatmap_data(taxonomic_level)
        
        if not heatmap_data:
            return None
            
        # Create DataFrame for heatmap
        df = pd.DataFrame({
            'Taxon': heatmap_data['taxa'],
            'Control': heatmap_data['control_values'],
            'UC': heatmap_data['uc_values']
        })
        
        # Set index to taxa names
        df.set_index('Taxon', inplace=True)
        
        # Create the heatmap
        plt.figure(figsize=(12, 10))
        
        # Normalize data for better visualization
        df_normalized = df.div(df.max(axis=1), axis=0)
        
        # Create heatmap
        sns.heatmap(df_normalized, 
                   annot=True, 
                   fmt='.2f',
                   cmap='RdYlBu_r',
                   cbar_kws={'label': 'Normalized Abundance'},
                   linewidths=0.5,
                   square=True)
        
        plt.title(f'Top 20 Most Distinct Taxa - {taxonomic_level.title()} Level\n(Normalized Abundance)', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Sample Group', fontsize=12)
        plt.ylabel('Taxa', fontsize=12)
        
        # Rotate x-axis labels
        plt.xticks(rotation=0)
        
        # Adjust layout
        plt.tight_layout()
        
        # Save to bytes
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer.getvalue()
        
    except Exception as e:
        print(f"Error generating heatmap: {e}", file=sys.stderr)
        return None

def create_pdf_report(analyzer, taxonomic_level, report_type, ai_summary):
    """Create PDF report with AI summary and visualizations"""
    try:
        # Create PDF document
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, 
                              topMargin=72, bottomMargin=18)
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Create custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.darkblue
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            alignment=TA_JUSTIFY
        )
        
        # Build story (content)
        story = []
        
        # Title
        report_title = f"AI-Powered Microbiome Analysis Report\n{taxonomic_level.title()} Level"
        story.append(Paragraph(report_title, title_style))
        story.append(Spacer(1, 20))
        
        # Report type indicator
        type_text = f"Report Type: {'Lay Summary' if report_type == 'lay' else 'Technical Summary'}"
        story.append(Paragraph(type_text, heading_style))
        story.append(Spacer(1, 12))
        
        # AI Summary
        story.append(Paragraph("Executive Summary", heading_style))
        story.append(Paragraph(ai_summary, body_style))
        story.append(Spacer(1, 20))
        
        # Generate and add diversity plot
        diversity_img = generate_diversity_plot(analyzer, taxonomic_level)
        if diversity_img:
            img_buffer = BytesIO(diversity_img)
            img = Image(img_buffer, width=6*inch, height=4*inch)
            story.append(Paragraph("Diversity Analysis", heading_style))
            story.append(img)
            story.append(Spacer(1, 20))
        
        # Generate and add heatmap
        heatmap_img = generate_heatmap(analyzer, taxonomic_level)
        if heatmap_img:
            img_buffer = BytesIO(heatmap_img)
            img = Image(img_buffer, width=6*inch, height=5*inch)
            story.append(Paragraph("Top 20 Most Distinct Taxa", heading_style))
            story.append(img)
            story.append(Spacer(1, 20))
        
        # Add summary table
        story.append(Paragraph("Summary Table", heading_style))
        
        # Get top 20 taxa data
        taxa_data = analyzer.calculate_taxa_control_uc_ratios(taxonomic_level)
        if taxa_data:
            top_20 = sorted(taxa_data, 
                           key=lambda x: abs(x['control_uc_ratio'] - 1) if x['control_uc_ratio'] != float('inf') else 0, 
                           reverse=True)[:20]
            
            # Create table data
            table_data = [['Rank', 'Taxon', 'Control Avg', 'UC Avg', 'UC StdDev', 'Ratio']]
            
            for i, taxon in enumerate(top_20, 1):
                ratio_str = f"{taxon['control_uc_ratio']:.2f}" if taxon['control_uc_ratio'] != float('inf') else "Inf"
                table_data.append([
                    str(i),
                    taxon['taxon'],
                    f"{taxon['control_avg']:.4f}",
                    f"{taxon['uc_avg']:.4f}",
                    f"{taxon['uc_std']:.4f}",
                    ratio_str
                ])
            
            # Create table
            table = Table(table_data, colWidths=[0.5*inch, 2.5*inch, 1*inch, 1*inch, 1*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            story.append(table)
        
        # Build PDF
        doc.build(story)
        
        # Get PDF content
        buffer.seek(0)
        pdf_content = buffer.getvalue()
        buffer.close()
        
        return pdf_content
        
    except Exception as e:
        print(f"Error creating PDF: {e}", file=sys.stderr)
        return None

def main():
    """Main CGI function"""
    try:
        # Set content type
        print("Content-Type: application/json")
        print()
        
        # Parse form data
        form = cgi.FieldStorage()
        
        # Get parameters
        taxonomic_level = form.getvalue('taxonomic_level')
        report_type = form.getvalue('report_type', 'technical')
        
        if not taxonomic_level:
            print(json.dumps({"success": False, "error": "Missing taxonomic_level parameter"}))
            return
        
        # Initialize analyzer
        analyzer = RealTimeMicrobiomeAnalyzer()
        
        # Generate AI summary
        ai_summary = analyzer.generate_ai_summary(taxonomic_level, report_type)
        
        if not ai_summary or ai_summary.startswith("Error"):
            print(json.dumps({"success": False, "error": ai_summary}))
            return
        
        # Create PDF report
        pdf_content = create_pdf_report(analyzer, taxonomic_level, report_type, ai_summary)
        
        if not pdf_content:
            print(json.dumps({"success": False, "error": "Failed to generate PDF"}))
            return
        
        # Encode PDF content
        pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
        
        # Return success response
        response = {
            "success": True,
            "message": f"AI summary generated successfully for {taxonomic_level} level",
            "report_type": report_type,
            "pdf_data": pdf_base64
        }
        
        print(json.dumps(response))
        
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))

if __name__ == "__main__":
    main()

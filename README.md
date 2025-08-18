# shotgunReporter

## Overview
A web-based microbiome analysis and visualization tool that provides interactive exploration of shotgun metagenomic sequencing data with AI-powered insights. This tool enables researchers to analyze and interpret complex microbiome datasets through intuitive visualizations and intelligent data interpretation.

Data included is from this paper in [Scientific reports](https://www.nature.com/articles/s41598-022-07995-7)

## Features

### Left Sidebar
- **Analysis Type Dropdown**: Choose between four main analysis categories:
  - Alpha Diversity (Shannon index only)
  - Beta Diversity (Bray-Curtis distance only)
  - Stacked Bar Plots
  - Krona Plots
  - **Visualize Specific Taxon** (NEW!)

### Dynamic Second Dropdown
- **Specific Options**: Once you select an analysis type, the second dropdown populates with available options:
  - **Alpha Diversity**: Shannon diversity index for each taxonomic level (Phylum through Species)
  - **Beta Diversity**: PCoA plots with Bray-Curtis distance for each taxonomic level
  - **Stacked Bar Plots**: Top 20 most abundant taxa plots for each taxonomic level (Phylum through Species)
  - **Krona Plots**: Interactive hierarchical visualizations of all samples combined
  - **Specific Taxon Analysis**: Taxonomic levels (Phylum, Class, Order, Family, Genus, Species) for deep-dive analysis

### Main Content Area
- Displays the selected plot/image
- Shows analysis information and descriptions
- Responsive design that works on different screen sizes

### Specific Taxon Visualization (NEW!)
- **Interactive Bar Charts**: Customizable bar plots showing individual taxon abundance across samples
- **Data Normalization**: Converts raw read counts to Reads Per Million (RPM) for cross-sample comparison
- **Color Customization**: Color pickers for Control vs. UC sample groups
- **Export Options**: Download plots as PNG and PDF with clean white backgrounds
- **Sample Comparison**: Control samples grouped together, UC samples shown individually
- **Layman Explanations**: Clear explanations of what each plot shows and how to interpret results

## How to Use

### Basic Analysis
1. **Open the webpage**: Open `index.html` in your web browser
2. **Select Analysis Type**: Choose from the first dropdown (Alpha Diversity, Beta Diversity, Stacked Bar Plots, or Krona Plots)
3. **Select Specific Option**: Choose the specific analysis/plot you want to view from the second dropdown
4. **View Results**: The selected plot will appear in the main content area with explanatory text

### Specific Taxon Analysis
1. **Select "Visualize Specific Taxon"** from the Analysis Type dropdown
2. **Choose Taxonomic Level**: Select Phylum, Class, Order, Family, Genus, or Species
3. **Select Individual Taxon**: Choose from the available taxa at that level
4. **Customize Colors**: Use color pickers to set Control and UC sample colors
5. **Export Results**: Download the interactive chart as PNG or PDF

## File Structure
The webpage expects the following files to be in the same directory:

### Static Plots (PNG)
- Alpha diversity plots: `alpha_diversity_[level]_Shannon.png`
- Beta diversity plots: `pcoa_[level]_bray_with_stats.png`
- Stacked bar plots: `stacked_barplot_[level]_top20.png`
- Krona plots: `all_krona_plots.html`

### Data Files (TSV)
- Kraken2 taxonomic abundance files: `all_child-UC_kraken2_250616_level_[2-7].tsv`
- Sample metadata: `metadata.tsv`

### Python Backend
- `simple_server.py`: HTTP server for serving the interface and handling API calls
- `extract_taxa_simple.py`: Data processing script for taxonomic analysis

## Technical Details
- **Frontend**: HTML5, CSS3, JavaScript with responsive design
- **Charts**: Chart.js for interactive bar plots and data visualization
- **Backend**: Python HTTP server with data processing capabilities
- **Data Processing**: Kraken2 TSV parsing and RPM normalization
- **Export**: PNG and PDF download with white background support
- **Error Handling**: Graceful fallback and user-friendly error messages

## Next Steps for Improvement
This is a working prototype that can be enhanced with:

### AI Integration (Coming Soon!)
- **GPT-OSS-20B Integration**: Local AI inference for intelligent data interpretation
- **Smart Plot Analysis**: AI-powered explanations of microbiome patterns and significance
- **Natural Language Queries**: Ask questions about your data in plain English
- **Intelligent Recommendations**: AI suggests related taxa to investigate and potential biomarkers

### Enhanced Features
- Statistical summary tables and significance testing
- Advanced interactive plots with Plotly or D3.js
- Search and filtering capabilities across taxonomic levels
- User authentication and data management
- Database integration for larger datasets
- Real-time data updates and collaboration features

## Browser Compatibility
- Chrome/Edge (recommended)
- Firefox
- Safari
- Mobile browsers (responsive design)

## Getting Started

### Quick Start
1. **Start the server**: Run `python3 simple_server.py` in your terminal
2. **Open browser**: Navigate to `http://localhost:8000/index.html`
3. **Start analyzing**: Use the interface to explore your microbiome data

### Server Requirements
- Python 3.6+
- No external dependencies (uses only standard library)
- Port 8000 must be available

### Data Requirements
- Kraken2 TSV files must be present in the project directory
- Static PNG plots should be in the same directory as `index.html`
- Server will automatically process and serve the data


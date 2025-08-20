# Microbiome Analysis Pipeline - AI Enhanced

## Overview

The pipeline starts with a Kraken2 results table like `all_child-UC_kraken2_250616.tsv`, on which `parse_taxa.py` script is run. This will split such a table into other tables divided by taxonomic level. On such tables, script `alpha-beta_diversity_norm.R` is run to generate diversity plots and stacked bar plots. File `all_krona_plots.html` is required to produce the krona plots presented here.

Samples included in the demo correspond to the following samples from project PRJNA759642:

|sample     | group	  | srr         |
|-----------|---------|-------------|
|PedUC47	  | UC	    | SRR15702647 |
|PedUC58	  | UC	    | SRR15702658 |
|PedCtrl59	| Control |	SRR15702659 |
|PedUC60	  | UC	    | SRR15702660 |


## 🚀 **New AI-Enhanced Features**

This pipeline now includes **advanced AI-powered analysis** capabilities that provide intelligent, data-driven insights into microbiome data:

### **🤖 AI-Powered Plot Explanations**
- **Dynamic AI Analysis**: Real-time AI explanations for all plot types (alpha diversity, beta diversity, stacked barplots, specific taxon)
- **Context-Aware Insights**: AI analyzes actual data values and provides specific, relevant interpretations
- **Multiple Plot Types**: Works with alpha diversity, beta diversity (PCoA), stacked barplots, and specific taxon visualizations
- **Intelligent Fallbacks**: Graceful degradation when AI services are unavailable

### **📊 AI-Generated Summary Reports**
- **Comprehensive Analysis**: Generate detailed reports with diversity analysis and heatmaps
- **Two Report Types**: 
  - **Lay Summary**: Easy-to-understand reports for non-specialists
  - **Technical Summary**: Scientific reports with detailed analysis
- **User-Selectable Taxonomic Levels**: Choose from Phylum, Class, Order, Family, Genus, or Species level
- **PDF Output**: Professional reports with embedded visualizations and tables
- **Top 20 Taxa Analysis**: Identify most distinct taxa between control and UC samples

### **📥 Enhanced Data Export**
- **Taxonomic Comparison Tables**: Download TSV/Excel files with Control vs UC abundance ratios
- **Standard Deviation Included**: UC sample variability metrics for better statistical analysis
- **Level-Specific Filtering**: Tables contain only taxa at the selected taxonomic level
- **Clean Taxon Names**: Proper taxonomic prefixes (f__, g__, s__) with readable formatting

### **🎨 Modern User Interface**
- **Professional Design**: Clean, modern interface with intuitive navigation
- **Responsive Layout**: Works on different screen sizes and devices
- **Loading Indicators**: Visual feedback during AI processing with spinning wheels
- **Error Handling**: Graceful error recovery and user-friendly messages

## 🔧 **Technical Architecture**

### **Backend Services**
- **Custom CGI Server**: `simple_server.py` handles all requests on port 8001
- **AI Analysis Engine**: `ai_realtime_analyzer.py` provides real-time data analysis
- **PDF Generation**: `ai_summary.py` creates professional reports with plots and tables
- **Data Processing**: Efficient handling of large microbiome datasets

### **AI Integration**
- **Ollama Support**: Integration with local Ollama for enhanced AI analysis
- **GPT-OSS-20B Model**: Advanced language model for microbiome interpretation
- **Fallback Mechanisms**: Basic analysis when AI services are unavailable
- **Real-time Processing**: Dynamic analysis based on actual data values

### **Data Formats**
- **Input**: Kraken2 TSV tables with taxonomic classifications
- **Output**: PNG plots, HTML reports, PDF summaries, TSV/Excel exports
- **Standards**: Compatible with standard microbiome analysis workflows

## 📁 **File Structure**

```
Dayhoff_JovelJ_shotgunReporter/
├── README.md                           # This file - main documentation
├── README_AI_Integration.md            # Detailed AI feature documentation
├── README_specific_taxon.md            # Specific taxon analysis guide
├── index_ai_enhanced.html             # Main AI-enhanced interface
├── simple_server.py                    # Custom CGI server
├── ai_realtime_analyzer.py            # AI analysis engine
├── cgi-bin/
│   ├── ai_analyze.py                  # AI plot explanation endpoint
│   ├── ai_summary.py                  # AI summary report generator
│   ├── extract_taxa.py                # Taxa extraction service
│   └── taxa_comparison.py            # Comparison table generator
├── Data Processing Scripts/
│   ├── parse_taxa.py                  # Taxonomic level splitting
│   ├── alpha-beta_diversity_norm.R    # Diversity analysis
│   └── convert_tsv2xlsx.py           # Format conversion utilities
├── Generated Plots/                    # All visualization outputs
├── Generated Reports/                  # AI-generated PDF summaries
└── requirements.txt                    # Python dependencies
```

## 🚀 **Quick Start**

### **1. Setup Environment**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Optional: Install Ollama for enhanced AI analysis
# Follow instructions at https://ollama.ai
ollama pull gpt-oss:20b
```

### **🚀 For Collaborators (Quick Setup)**
If you received this project folder from a colleague:

```bash
# 1. Navigate to the project folder
cd Dayhoff_JovelJ_shotgunReporter

# 2. Install required Python packages
pip install -r requirements.txt

# 3. Start the server
python simple_server.py

# 4. Open your browser and go to:
# http://localhost:8001/index_ai_enhanced.html
```

**That's it!** The application will be running and ready to use.

### **2. AI Setup (Optional but Recommended)**
For enhanced AI analysis capabilities, install and run Ollama with the gpt-oss:20b model:

```bash
# Install Ollama (macOS)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull the model
ollama pull gpt-oss:20b

# Start Ollama service
ollama serve
```

**Note:** The system will work without Ollama, but will provide basic summaries instead of AI-generated insights. The AI features include:
- Dynamic plot explanations
- Comprehensive analysis reports
- Enhanced data interpretation
- Professional PDF generation

### **3. Start the Server**
```bash
python simple_server.py
# Server runs at http://localhost:8001
```

### **4. Access the Interface**
- Open `http://localhost:8001/index_ai_enhanced.html`
- Select analysis type and options
- Use AI-powered features for enhanced insights
- Generate comprehensive reports and export data

## 🔍 **Key Features**

### **Core Analysis**
- **Alpha Diversity**: Shannon diversity analysis across taxonomic levels
- **Beta Diversity**: PCoA analysis with statistical testing
- **Stacked Barplots**: Top 20 taxa visualization
- **Krona Plots**: Interactive taxonomic hierarchy exploration
- **Specific Taxon Analysis**: Detailed analysis of individual taxa

### **AI Enhancements**
- **Smart Explanations**: Context-aware plot interpretations
- **Comprehensive Reports**: Professional PDF summaries with visualizations
- **Data Export**: Enhanced tables with statistical metrics
- **User Control**: Selectable taxonomic levels for all analyses

## 📊 **Data Requirements**

### **Input Format**
- Kraken2 output tables in TSV format
- Taxonomic classifications with standard prefixes (k__, p__, c__, o__, f__, g__, s__)
- Sample metadata for group comparisons (Control vs UC)

## 💻 **System Requirements for Collaborators**

### **Required Software**
- **Python 3.9 or higher** (check with `python --version`)
- **pip** (Python package installer, usually comes with Python)

### **Operating Systems**
- ✅ **macOS** (tested and working)
- ✅ **Linux** (should work with Python 3.9+)
- ⚠️ **Windows** (may need adjustments for paths)

### **Browser**
- **Any modern web browser** (Chrome, Firefox, Safari, Edge)
- **JavaScript enabled** (required for the interface)

### **Output Quality**
- High-resolution plots (300 DPI)
- Professional PDF reports
- Exportable data tables
- Interactive visualizations

## 🤝 **Contributing**

This pipeline is designed to be extensible and modular. Key areas for enhancement:
- Additional AI models and analysis types
- New visualization formats
- Enhanced statistical analysis
- Integration with other microbiome analysis tools

## 🔧 **Troubleshooting for Collaborators**

### **Common Issues & Solutions**

#### **"Port 8001 already in use" Error**
```bash
# Find and kill the process using port 8001
lsof -i :8001
kill -9 <PID>

# Or use a different port by editing simple_server.py
# Change PORT = 8001 to PORT = 8002
```

#### **"Module not found" Errors**
```bash
# Make sure you're in the project directory
pwd  # Should show path ending with Dayhoff_JovelJ_shotgunReporter

# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

#### **"Permission denied" Errors**
```bash
# On macOS/Linux, you might need:
chmod +x simple_server.py
```

#### **Browser shows "Connection refused"**
- Make sure the server is running (`python simple_server.py`)
- Check that you're using `http://localhost:8001` (not `https://`)
- Verify the port number matches what's in `simple_server.py`

## 📚 **Documentation**

- **README_AI_Integration.md**: Detailed AI feature documentation
- **README_specific_taxon.md**: Specific taxon analysis guide
- **Code Comments**: Comprehensive inline documentation
- **Example Outputs**: Sample reports and visualizations

## 🔬 **Scientific Applications**

This pipeline is designed for:
- **Microbiome Research**: Comprehensive analysis of microbial communities
- **Clinical Studies**: Control vs treatment group comparisons
- **Educational Use**: Clear visualizations and explanations
- **Publication Ready**: High-quality figures and statistical analysis

## 📞 **Support**

For technical support or feature requests:
- Check the documentation files
- Review code comments for implementation details
- Test with sample data to verify functionality

---

**Version**: AI-Enhanced v2.0  
**Last Updated**: August 2025  
**Features**: AI-powered analysis, comprehensive reporting, enhanced data export


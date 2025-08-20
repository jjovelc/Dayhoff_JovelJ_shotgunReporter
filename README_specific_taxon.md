# Specific Taxon Analysis Guide - Microbiome Analysis Pipeline

## 🎯 **Overview**

The Specific Taxon Analysis module provides **deep-dive analysis** of individual microbial taxa across different taxonomic levels. This feature allows researchers to examine the behavior of specific bacteria, archaea, or other microorganisms in detail, with enhanced AI-powered insights and comprehensive data export capabilities.

## 🚀 **Key Features**

### **1. Multi-Level Taxonomic Analysis**
- **6 Taxonomic Levels**: Phylum, Class, Order, Family, Genus, Species
- **Dynamic Selection**: Choose the taxonomic resolution that fits your research needs
- **Comprehensive Coverage**: Analyze taxa from broad phylum-level groups to specific species

### **2. AI-Enhanced Analysis**
- **Intelligent Insights**: AI provides context-aware interpretations of taxon behavior
- **Pattern Recognition**: Identify unusual abundance patterns or group differences
- **Biological Context**: Understand the ecological and health implications of findings

### **3. Enhanced Data Export**
- **Immediate Table Display**: Taxonomic comparison tables appear instantly upon level selection
- **Multiple Formats**: Download as TSV or Excel files with proper formatting
- **Statistical Metrics**: Include standard deviation for UC samples and Control/UC ratios
- **Level-Specific Filtering**: Tables contain only taxa at the selected taxonomic level

## 🔍 **How to Use**

### **Step 1: Select Analysis Type**
1. Open the main interface at `http://localhost:8001/index_ai_enhanced.html`
2. From the left sidebar, select **"Visualize Specific Taxon"** from the Analysis Type dropdown
3. The second dropdown will automatically populate with taxonomic levels

### **Step 2: Choose Taxonomic Level**
- **Phylum (Level 2)**: Broad bacterial groups (e.g., Firmicutes, Bacteroidetes)
- **Class (Level 3)**: More specific groupings within phyla
- **Order (Level 4)**: Taxonomic orders with similar characteristics
- **Family (Level 5)**: Closely related genera (e.g., Lachnospiraceae)
- **Genus (Level 6)**: Specific bacterial genera (e.g., Lactobacillus)
- **Species (Level 7)**: Individual bacterial species

### **Step 3: Select Individual Taxon**
1. Choose your desired taxonomic level
2. A third dropdown will appear with available taxa at that level
3. Select the specific taxon you want to analyze
4. The system will automatically generate an interactive bar chart

### **Step 4: Customize and Analyze**
- **Color Customization**: Use color pickers to set Control vs UC sample colors
- **Interactive Chart**: Hover over bars to see exact values
- **AI Explanation**: Click the 🤖 AI button for intelligent insights
- **Data Export**: Download the chart as PNG or PDF

## 📊 **Data Export Features**

### **Taxonomic Comparison Tables**
When you select a taxonomic level, the system automatically generates and displays a comprehensive comparison table:

#### **Table Contents**
- **Taxon Names**: Clean, readable names with proper taxonomic prefixes
- **Control Average**: Average abundance across control samples
- **UC Average**: Average abundance across UC samples
- **UC Standard Deviation**: Variability within UC sample group
- **Control/UC Ratio**: Relative abundance differences
- **Sample Counts**: Number of samples in each group

#### **Download Options**
- **TSV Format**: Tab-separated values for data analysis
- **Excel Format**: Formatted spreadsheets with proper headers
- **Immediate Access**: Tables appear instantly when level is selected

### **Chart Export**
- **PNG Format**: High-resolution images for presentations
- **PDF Format**: Vector graphics for publications
- **Clean Backgrounds**: Professional appearance with white backgrounds
- **Customizable Colors**: User-defined color schemes

## 🤖 **AI-Powered Insights**

### **Dynamic Analysis**
The AI system analyzes your specific taxon data and provides:

- **Abundance Patterns**: Interpretation of relative abundance across samples
- **Group Differences**: Analysis of Control vs UC patterns
- **Biological Significance**: Context about the taxon's role in the microbiome
- **Health Implications**: Potential clinical relevance of findings

### **Context-Aware Explanations**
- **Data-Driven Insights**: AI analyzes actual abundance values, not generic descriptions
- **Taxonomic Context**: Explanations tailored to the specific level and taxon
- **Sample-Specific Analysis**: Considers your specific sample groups and data patterns

## 🔧 **Technical Implementation**

### **Data Processing Pipeline**
1. **Input**: Kraken2 TSV tables with taxonomic classifications
2. **Normalization**: Conversion to Reads Per Million (RPM) for cross-sample comparison
3. **Level Filtering**: Extraction of taxa at the selected taxonomic level
4. **Statistical Analysis**: Calculation of means, standard deviations, and ratios
5. **Visualization**: Generation of interactive bar charts and comparison tables

### **File Requirements**
- **Taxonomic Data**: `all_child-UC_kraken2_250616_level_[2-7].tsv` files
- **Sample Metadata**: `metadata.tsv` with group assignments
- **Server Access**: Running `simple_server.py` on port 8001

## 📈 **Analysis Examples**

### **Example 1: Family-Level Analysis**
- **Selected Level**: Family (Level 5)
- **Available Taxa**: Lachnospiraceae, Ruminococcaceae, Bacteroidaceae, etc.
- **Analysis**: Compare abundance patterns across sample groups
- **Export**: Download family-level comparison table and individual taxon charts

### **Example 2: Genus-Level Analysis**
- **Selected Level**: Genus (Level 6)
- **Available Taxa**: Lactobacillus, Bifidobacterium, Clostridium, etc.
- **Analysis**: Detailed examination of specific bacterial genera
- **Export**: Comprehensive genus-level data with statistical metrics

### **Example 3: Species-Level Analysis**
- **Selected Level**: Species (Level 7)
- **Available Taxa**: Individual bacterial species
- **Analysis**: Most detailed taxonomic resolution
- **Export**: Species-specific abundance data and comparisons

## 🎨 **User Interface Features**

### **Responsive Design**
- **Desktop Optimization**: Full-featured interface for large screens
- **Mobile Compatibility**: Responsive design for tablets and phones
- **Touch Support**: Optimized for touch-based interactions

### **Visual Feedback**
- **Loading Indicators**: Show progress during data processing
- **Status Messages**: Clear feedback on operations and errors
- **Interactive Elements**: Hover effects and click responses

### **Professional Styling**
- **Clean Layout**: Modern, scientific appearance
- **Consistent Design**: Unified visual language throughout
- **Accessibility**: High contrast and readable fonts

## 📊 **Data Quality Features**

### **Input Validation**
- **File Format Checking**: Ensures proper TSV structure
- **Data Integrity**: Validates taxonomic classifications
- **Sample Consistency**: Checks group assignments and sample counts

### **Output Quality**
- **High Resolution**: 300 DPI output for publication quality
- **Statistical Accuracy**: Proper calculation of means and standard deviations
- **Format Consistency**: Standardized output across all taxonomic levels

## 🚨 **Troubleshooting**

### **Common Issues**

#### **1. No Taxa Available**
- **Cause**: Selected level may not have data in your dataset
- **Solution**: Try a different taxonomic level or check data files

#### **2. Chart Not Displaying**
- **Cause**: JavaScript errors or missing dependencies
- **Solution**: Check browser console and ensure Chart.js is loading

#### **3. Export Failures**
- **Cause**: File permissions or server issues
- **Solution**: Check server logs and file permissions

### **Error Recovery**
- **Graceful Degradation**: System continues working even if some features fail
- **User Feedback**: Clear error messages explaining what went wrong
- **Alternative Paths**: Multiple ways to achieve desired results

## 🔮 **Future Enhancements**

### **Planned Features**
- **Advanced Filtering**: Search and filter taxa by name or characteristics
- **Statistical Testing**: Significance testing for group differences
- **Comparative Analysis**: Compare multiple taxa simultaneously
- **Integration**: Connect with external microbiome databases

### **User Experience Improvements**
- **Batch Processing**: Analyze multiple taxa at once
- **Custom Reports**: Generate personalized analysis summaries
- **Collaboration Tools**: Share analyses with research teams
- **Mobile Apps**: Native mobile applications for field research

## 📚 **Additional Resources**

### **Related Documentation**
- **README.md**: Main project overview
- **README_AI_Integration.md**: AI feature documentation
- **Code Comments**: Inline documentation in source files

### **Example Workflows**
- **Clinical Research**: Step-by-step analysis for clinical studies
- **Educational Use**: Classroom exercises and tutorials
- **Publication Preparation**: Guidelines for creating publication-ready figures

### **Support and Community**
- **Technical Support**: Troubleshooting guides and FAQs
- **User Forums**: Community discussions and best practices
- **Training Materials**: Video tutorials and workshops

---

**Version**: AI-Enhanced v2.0  
**Last Updated**: August 2025  
**Features**: Multi-level analysis, AI insights, enhanced data export, professional visualizations

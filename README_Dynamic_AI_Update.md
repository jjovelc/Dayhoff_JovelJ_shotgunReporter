# Dynamic AI Analysis Update

## Overview

This update makes the AI analysis system dynamic for **alpha diversity**, **beta diversity (PCoA)**, and **stacked barplots**, similar to how it already worked for the "Visualize specific taxon" module.

## What Changed

### Before
- Alpha diversity, beta diversity, and stacked barplots showed only **static, generic text explanations**
- AI explanations were not personalized to the actual data
- No real-time analysis of plot data

### After
- All plot types now use **dynamic, real-time AI analysis**
- AI explanations are personalized based on actual data values from your TSV files
- Real-time extraction of diversity values, abundances, and sample comparisons

## Technical Changes Made

### 1. Enhanced AI Real-Time Analyzer (`ai_realtime_analyzer.py`)

Added new methods to extract actual data from your TSV files:

- **`extract_alpha_diversity_data(taxonomic_level)`** - Calculates Shannon diversity from abundance data
- **`extract_stacked_barplot_data(taxonomic_level)`** - Extracts top taxa and abundances
- **`extract_pcoa_data(taxonomic_level)`** - Gets abundance data for PCoA analysis
- **`get_sample_metadata()`** - Reads sample metadata to identify Control vs UC groups

### 2. Updated CGI Endpoint (`cgi-bin/ai_analyze.py`)

Modified to handle all plot types dynamically:

- **Alpha diversity**: Extracts actual diversity values and compares Control vs UC
- **PCoA**: Analyzes abundance patterns across samples
- **Stacked barplots**: Identifies top taxa and abundance patterns

### 3. Enhanced Frontend (`index_ai_enhanced.html`)

Updated JavaScript functions to:

- Pass taxonomic level information to AI analyzer
- Call real-time AI for all plot types
- Display dynamic explanations instead of static text

## How It Works Now

### Alpha Diversity Analysis
1. **Data Extraction**: Reads your TSV files (e.g., `all_child-UC_kraken2_250616_level_2.tsv`)
2. **Diversity Calculation**: Computes Shannon diversity for each sample
3. **Group Comparison**: Separates Control vs UC samples and calculates averages
4. **AI Analysis**: Generates personalized explanation with actual values

### PCoA Analysis
1. **Data Extraction**: Gets abundance data for all taxa in each sample
2. **Sample Grouping**: Identifies Control vs UC sample patterns
3. **AI Analysis**: Explains what the patterns mean for your data

### Stacked Barplot Analysis
1. **Data Extraction**: Identifies top 20 most abundant taxa
2. **Abundance Analysis**: Calculates relative abundances across samples
3. **AI Analysis**: Explains composition patterns and health implications

## Benefits

✅ **Personalized Explanations**: AI now references your actual data values
✅ **Real-time Analysis**: No more generic text - explanations are data-driven
✅ **Sample Comparisons**: Clear Control vs UC group comparisons
✅ **Actionable Insights**: Specific recommendations based on your data
✅ **Consistent Experience**: All plot types now work the same way

## Requirements

- **pandas**: Added to `requirements.txt` for data processing
- **numpy**: For mathematical calculations (diversity metrics)
- **Ollama**: Running locally with gpt-oss:20b model

## Testing

Use the test script to verify functionality:

```bash
python test_ai_endpoint.py
```

This will test all three plot types and show the dynamic AI responses.

## Example Output

### Before (Static)
> "This chart shows how diverse your gut bacteria community is. Think of it like having a variety of different plants in a garden - more variety is generally better for your health."

### After (Dynamic)
> "This alpha diversity plot shows how diverse your gut microbiome is across samples. Your average diversity is 0.830. Control samples show an average diversity of 1.010, while UC samples show 0.769. This comparison helps identify how your condition may affect microbiome diversity."

## File Structure

```
├── ai_realtime_analyzer.py          # Enhanced with data extraction methods
├── cgi-bin/ai_analyze.py           # Updated to handle all plot types
├── index_ai_enhanced.html          # Enhanced frontend with dynamic AI
├── requirements.txt                 # Added pandas dependency
├── test_ai_endpoint.py             # Test script for verification
└── README_Dynamic_AI_Update.md     # This documentation
```

## Next Steps

1. **Install Dependencies**: `pip install -r requirements.txt`
2. **Start Server**: Ensure your CGI server is running on port 8001
3. **Test Functionality**: Use the test script to verify everything works
4. **Enjoy Dynamic AI**: All your plots now have personalized, data-driven explanations!

## Troubleshooting

- **Data Not Found**: Ensure your TSV files are in the correct location
- **Metadata Issues**: Check that `metadata.tsv` has the correct column names (`sample`, `group`)
- **Server Errors**: Verify CGI endpoint is accessible at the expected URL
- **AI Failures**: Check that Ollama is running with the gpt-oss:20b model

The system now provides the same dynamic, personalized experience across all plot types that you previously only had with the "Visualize specific taxon" module!

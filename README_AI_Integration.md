# 🧬 AI-Enhanced Microbiome Reporter

This document describes the new AI capabilities added to your shotgun metagenomics reporter using the `gpt-oss:20b` model through Ollama.

## 🚀 What's New

Your microbiome reporter now includes **AI-powered plot explanations** that automatically generate simple, layman-friendly descriptions of complex microbiome visualizations. This makes your reports accessible to customers with no scientific background.

## ✨ Key Features

### Phase 1: Simple Plot Explanations (Current)
- **Automatic Plot Classification**: Identifies plot types and taxonomic levels
- **AI-Generated Explanations**: Simple language explanations using GPT-OSS-20B
- **Customer-Friendly Language**: High school reading level with relatable analogies
- **Fallback Explanations**: Built-in explanations if AI is unavailable
- **HTML Report Generation**: Beautiful, professional customer reports

### Future Phases (Planned)
- **Personalized Health Insights**: AI-based recommendations based on results
- **Literature Integration**: Connect findings to published research
- **Interactive Q&A**: Natural language queries about microbiome data

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.6 or higher
- Ollama (for running the AI model locally)

### Quick Start

1. **Run the setup script**:
   ```bash
   python setup_ai_explainer.py
   ```

2. **Or install manually**:
   ```bash
   pip install -r requirements.txt
   ollama pull gpt-oss:20b
   ```

3. **Start Ollama**:
   ```bash
   ollama serve
   ```

4. **Run the AI explainer**:
   ```bash
   python ai_plot_explainer.py
   ```

## 📊 How It Works

### 1. Plot Detection
The system automatically scans your directory for microbiome plots:
- **Stacked Barplots**: Relative abundance of bacteria types
- **Alpha Diversity**: Microbial community diversity
- **PCOA Plots**: Sample similarity/differences
- **Krona Plots**: Taxonomic hierarchies

### 2. AI Explanation Generation
For each plot, the system:
- Classifies the plot type and taxonomic level
- Sends a carefully crafted prompt to GPT-OSS-20B
- Generates simple, customer-friendly explanations
- Falls back to pre-written explanations if needed

### 3. Report Creation
The system creates:
- **JSON file**: Structured data with all explanations
- **HTML report**: Beautiful, professional customer-facing report
- **Console output**: Progress and sample explanations

## 🎯 Example Explanations

### Stacked Barplot (Phylum Level)
**AI Explanation**: "This chart shows the different types of bacteria found in your gut. The bigger each bar is, the more of that bacteria type you have. This helps us understand what's living in your digestive system."

### Alpha Diversity (Shannon)
**AI Explanation**: "This chart shows how diverse your gut bacteria community is. Think of it like having a variety of different plants in a garden - more variety is generally better for your health."

## 📁 File Structure

```
├── ai_plot_explainer.py      # Main AI explanation system
├── setup_ai_explainer.py     # Setup and installation helper
├── requirements.txt           # Python dependencies
├── README_AI_Integration.md  # This file
├── plot_explanations.json    # Generated explanations (output)
└── ai_explained_report.html  # Customer report (output)
```

## 🔧 Configuration

### Customizing the AI Model
Edit `ai_plot_explainer.py` to change:
- **Model**: Switch to different Ollama models
- **API Base**: Change Ollama server location
- **Temperature**: Adjust creativity of explanations
- **Max Tokens**: Control explanation length

### Customizing Explanations
Modify the `_create_explanation_prompt()` method to:
- Change the tone (more formal, more casual)
- Adjust technical level
- Add specific health context
- Include company branding

## 📈 Output Examples

### JSON Output Structure
```json
{
  "stacked_barplot_phylum_top20.png": {
    "plot_type": "stacked_barplot",
    "taxonomic_level": "phylum",
    "explanation": "This chart shows the different types of bacteria found in your gut..."
  }
}
```

### HTML Report Features
- **Responsive Design**: Works on all devices
- **Professional Styling**: Clean, medical-grade appearance
- **Plot Integration**: Images with AI explanations
- **Easy Navigation**: Clear sections for each plot type

## 🚨 Troubleshooting

### Common Issues

1. **"Cannot connect to Ollama API"**
   - Ensure Ollama is running: `ollama serve`
   - Check if Ollama is installed: `ollama --version`

2. **"Model not found"**
   - Pull the model: `ollama pull gpt-oss:20b`
   - Check available models: `ollama list`

3. **"No plot files found"**
   - Ensure PNG/JPG files are in the current directory
   - Check file permissions

4. **API request failures**
   - Verify Ollama is running and accessible
   - Check network connectivity
   - Ensure model is fully downloaded

### Performance Tips
- **Model Size**: GPT-OSS-20B requires ~40GB RAM
- **Processing Time**: First run may be slower as model loads
- **Batch Processing**: System processes all plots automatically

## 🔮 Future Enhancements

### Phase 2: Advanced Insights
- Personalized health recommendations
- Diet and lifestyle suggestions
- Comparative analysis with healthy populations

### Phase 3: Interactive Features
- Natural language queries about results
- Dynamic report customization
- Integration with health tracking apps

## 🤝 Contributing

To enhance the AI capabilities:
1. Modify prompt engineering in `_create_explanation_prompt()`
2. Add new plot types in `_classify_plot()`
3. Enhance fallback explanations
4. Improve HTML report styling

## 📚 Technical Details

### AI Model Specifications
- **Model**: gpt-oss:20b
- **Parameters**: 20 billion parameters
- **Context**: 8192 tokens
- **License**: Open source

### API Integration
- **Protocol**: HTTP REST API
- **Endpoint**: Ollama `/api/generate`
- **Authentication**: None (local deployment)
- **Rate Limiting**: None (local processing)

### Prompt Engineering
The system uses carefully crafted prompts that:
- Set the AI's role and tone
- Provide context about microbiome science
- Specify output requirements
- Include fallback mechanisms

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify Ollama installation and model availability
3. Check Python dependencies and versions
4. Review console output for error messages

---

**Note**: This AI integration runs entirely locally using Ollama, ensuring data privacy and security for your customers' microbiome results.

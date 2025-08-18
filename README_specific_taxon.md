# Specific Taxon Visualization Feature

This feature allows you to visualize the abundance of specific microbial taxa across your samples using an interactive web interface.

## How to Use

### 1. Start the Server
```bash
python3 simple_server.py
```
The server will start on `http://localhost:8000`

### 2. Open the Web Interface
Open `index.html` in your web browser. You can do this by:
- Double-clicking the file
- Opening `http://localhost:8000/index.html` in your browser

### 3. Using the New Feature

#### Step 1: Select Analysis Type
- Choose **"Visualize Specific Taxon"** from the first dropdown menu

#### Step 2: Select Taxonomic Level
- Choose the taxonomic level you want to explore:
  - **Phylum** (Level 2)
  - **Class** (Level 3)
  - **Order** (Level 4)
  - **Family** (Level 5)
  - **Genus** (Level 6)
  - **Species** (Level 7)

#### Step 3: Select Specific Taxon
- Choose the specific microbe you want to visualize from the dropdown
- The list will automatically populate with all available taxa at the selected level

#### Step 4: View Results
- A bar plot will be generated showing the abundance of the selected taxon across all samples
- The plot shows:
  - **Control sample** (PedCtrl59) in green
  - **UC samples** (PedUC47, PedUC58, PedUC60) in red
  - Data is normalized to **Reads Per Million (RPM)** for fair comparison

## What the Plots Show

### Bar Plot Interpretation
- **Y-axis**: Reads Per Million (RPM) - normalized abundance
- **X-axis**: Sample groups (Control vs UC samples)
- **Green bars**: Control sample
- **Red bars**: UC samples (individual bars for each sample)

### Data Summary
- **Control Sample**: Shows the abundance in the healthy control
- **UC Samples**: Shows individual abundances in each UC sample
- **UC Mean**: Average abundance across all UC samples

## Technical Details

### Data Processing
- Raw read counts are converted to RPM (Reads Per Million) for normalization
- This makes samples comparable regardless of sequencing depth
- Data is extracted from the `all_child-UC_kraken2_250616_level_X.tsv` files

### Taxonomic Levels
- **Level 2**: Phylum (e.g., Bacteroidota, Firmicutes)
- **Level 3**: Class (e.g., Bacteroidia, Clostridia)
- **Level 4**: Order (e.g., Bacteroidales, Clostridiales)
- **Level 5**: Family (e.g., Bacteroidaceae, Clostridiaceae)
- **Level 6**: Genus (e.g., Bacteroides, Clostridium)
- **Level 7**: Species (e.g., Bacteroides_fragilis)

### Sample Information
- **PedUC47**: UC sample 1
- **PedUC58**: UC sample 2
- **PedCtrl59**: Control sample
- **PedUC60**: UC sample 3

## Troubleshooting

### If the server won't start:
- Make sure you have Python 3 installed
- Check that all required files are in the same directory
- Ensure no other process is using port 8000

### If taxa don't load:
- Check that the TSV files exist and are readable
- Verify the file naming convention: `all_child-UC_kraken2_250616_level_X.tsv`

### If plots don't display:
- Make sure Chart.js is loading (check browser console for errors)
- Verify that the server is running and accessible

## Files Used

- `index.html` - Main web interface
- `simple_server.py` - HTTP server for handling requests
- `extract_taxa_simple.py` - Script for extracting taxa data
- `all_child-UC_kraken2_250616_level_X.tsv` - Data files for each taxonomic level

## Example Use Case

1. **Research Question**: "Is Bacteroidota more abundant in UC patients?"
2. **Select**: "Visualize Specific Taxon" → "Phylum" → "Bacteroidota"
3. **Result**: Bar plot showing Bacteroidota abundance across samples
4. **Interpretation**: Compare Control vs UC bars to see if there's a difference
5. **Conclusion**: If UC bars are consistently higher/lower, it suggests a disease association

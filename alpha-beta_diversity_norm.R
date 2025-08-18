# This script takes as input a series of kraken2 (mpa style) generated
# by running: python parse_taxa.py kraken2_mpa-style_report.tsv
# e.g. python parse_taxa.py inflammation_all_samples_kraken2-counts.tsv
# The data will be normalized, and alpha and beta diversity analyses
# conducted, and plots will be generated

# Make sure you have the required libraries, otherwise:
# BiocManager::install("phyloseq")
# install.packages("tidyverse")
# install.packages("remotes")
# remotes::install_github("vegandevs/vegan")
rm(list = ls())
library(phyloseq)
library(tidyverse)
library(vegan)

# Change directory to the directory where you have the input data
setwd("/Users/juanjovel/jj/dayhoff/pipelines/reporting_shotgun")

# Define the levels you want to iterate over
levels <- 1:7

# Define the taxonomic ranks
taxonomic_ranks <- c("Kingdom", "Phylum", "Class", "Order", "Family", "Genus", "Species")

# Function to extract terminal leaf from taxonomic string
extract_terminal_leaf <- function(taxa_name) {
  # Split by | and get the last non-empty element
  parts <- strsplit(taxa_name, "\\|")[[1]]
  parts <- parts[parts != "" & !is.na(parts)]
  if (length(parts) > 0) {
    terminal <- parts[length(parts)]
    # Remove prefixes like k__, p__, c__, etc.
    terminal <- gsub("^[kpcofgs]__", "", terminal)
    return(terminal)
  } else {
    return("Unknown")
  }
}

# Read metadata from file
sample_metadata_df <- read.csv("metadata.tsv", sep = '\t', header = TRUE, check.names = FALSE)
# Rename columns to match expected format
colnames(sample_metadata_df) <- c("SampleID", "Condition", "SRR")
# Set row names
row.names(sample_metadata_df) <- sample_metadata_df$SampleID

# Iterate over each level
for (level in levels) {
  # Generate file name based on level
  
  infile <- sprintf("all_child-UC_kraken2_250616_level_%d.tsv", level)
  
  # Extract level suffix and number
  level_suffix <- sprintf('level_%d', level)
  taxonomic_rank_name <- taxonomic_ranks[level]
  rank_name_for_file <- gsub(" ", "_", tolower(taxonomic_rank_name))
  
  # Read the OTU table from the file
  shotgun_table <- read.csv(infile, sep = '\t', header = TRUE, check.names = FALSE, row.names = 1)
  
  # Ensure taxa names in OTU table are consistent and formatted correctly
  taxa_names_in_otu_table <- rownames(shotgun_table)
  
  # For diversity indices calculations requiring raw counts
  otu_table_obj_raw <- otu_table(as.matrix(shotgun_table), taxa_are_rows = TRUE)
  
  # For parts of analysis where relative abundances are appropriate
  shotgun_table_relative_abundance <- apply(shotgun_table, 2, function(x) x / sum(x))
  otu_table_obj_relative <- otu_table(as.matrix(shotgun_table_relative_abundance), taxa_are_rows = TRUE)
  
  # Select the taxonomic ranks to use based on the level
  ranks_to_use <- taxonomic_ranks[1:level]
  
  # Create taxa information
  taxa_info <- data.frame(Taxa = taxa_names_in_otu_table) %>%
    separate(Taxa, into = ranks_to_use, sep = "\\|", fill = "right") %>%
    as.data.frame()
  
  row.names(taxa_info) <- taxa_names_in_otu_table
  
  tax_table_obj <- tax_table(as.matrix(taxa_info))
  
  samples <- colnames(shotgun_table)
  
  # Filter metadata to only include samples present in the OTU table
  sample_metadata_filtered <- sample_metadata_df[samples, , drop = FALSE]
  
  sample_metadata <- sample_data(sample_metadata_filtered)
  
  # Create phyloseq object for raw counts
  physeq_raw <- phyloseq(otu_table_obj_raw, tax_table_obj, sample_metadata)
  
  # Create phyloseq object for relative abundances
  # This object can be used for beta diversity analysis or other analyses where relative abundances are appropriate
  physeq_relative <- phyloseq(otu_table_obj_relative, tax_table_obj, sample_metadata)
  
  # Generate stacked bar plots for levels 2-7 (Phylum through Species)
  if (level >= 2) {
    cat(sprintf("\nGenerating stacked bar plot for %s (Level %d)...\n", taxonomic_rank_name, level))
    
    # Calculate mean relative abundance across all samples for each taxon
    mean_abundance <- rowMeans(shotgun_table_relative_abundance)
    
    # Get top N most abundant taxa
    n_taxa <- min(20, nrow(shotgun_table))  # Limit to 20 or fewer taxa
    top_taxa_indices <- order(mean_abundance, decreasing = TRUE)[1:n_taxa]
    top_taxa_names <- rownames(shotgun_table)[top_taxa_indices]
    
    # Prepare data for plotting
    plot_data <- data.frame()
    for (taxon in top_taxa_names) {
      for (sample in samples) {
        abundance <- shotgun_table_relative_abundance[taxon, sample]
        terminal_leaf <- extract_terminal_leaf(taxon)
        condition <- sample_metadata_filtered[sample, "Condition"]
        
        plot_data <- rbind(plot_data, data.frame(
          Sample = sample,
          Terminal_Leaf = terminal_leaf,
          Relative_Abundance = abundance,
          Condition = condition
        ))
      }
    }
    
    # Create color palette
    n_colors <- length(unique(plot_data$Terminal_Leaf))
    discrete_palette <- c(
      # RColorBrewer Accent (8 colors)
      RColorBrewer::brewer.pal(8, "Accent"),
      # Additional pastel colors
        "#E6194B", #/* strong red */
        "#3CB44B", #/* green */
        "#FFE119", #/* bright yellow */
        "#4363D8", #/* blue */
        "#F58231", #/* orange */
        "#911EB4", #/* purple */
        "#46F0F0", #/* cyan */
        "#F032E6", #/* magenta */
        "#BCF60C", #/* lime */
        "#FABEBE", #/* light pink */
        "#008080", #/* teal */
        "#E6BEFF", #/* lavender */
        "#9A6324", #/* brown */
        "#FFFAC8", #/* cream */
        "#800000", #/* maroon */
        "#AAFFC3", #/* mint */
        "#808000", #/* olive */
        "#000075"  #/* navy */ 
    )
    
    # Remove duplicates and select needed colors
    discrete_palette <- unique(discrete_palette)
    colors <- discrete_palette[1:min(n_colors, length(discrete_palette))]
    
    # If we still need more colors, supplement with generated pastels
    if (n_colors > length(discrete_palette)) {
      additional_needed <- n_colors - length(discrete_palette)
      hues <- seq(0, 1, length.out = additional_needed + 1)[1:additional_needed]
      additional_colors <- hsv(h = hues, s = 0.35, v = 0.85)
      colors <- c(colors, additional_colors)
    }
    
    # Create stacked bar plot with consistent bar widths using single x-axis
    p_stacked <- ggplot(plot_data, aes(x = Sample, y = Relative_Abundance, fill = Terminal_Leaf)) +
      geom_bar(stat = "identity", position = "stack", width = 0.7) +
      scale_fill_manual(values = colors) +
      theme_bw() +
      theme(
        axis.text.x = element_text(angle = 45, hjust = 1),
        legend.title = element_text(size = 12),
        legend.text = element_text(size = 10),
        plot.title = element_text(size = 14, hjust = 0.5),
        strip.background = element_rect(fill = "white", color = "black"),
        strip.text = element_text(size = 12, face = "bold")
      ) +
      labs(
        x = "Sample",
        y = "Relative Abundance",
        fill = taxonomic_rank_name,
        title = paste("Top", n_taxa, "Most Abundant", taxonomic_rank_name, "- Stacked Bar Plot")
      ) +
      # Use facet_grid instead of facet_wrap for better control
      facet_grid(. ~ Condition, scales = "free_x", space = "free_x") +
      # Force equal bar widths by setting fixed x-axis expansion
      scale_x_discrete(expand = c(0.025, 0.025))
    
    # Save stacked bar plot
    stacked_plot_filename <- paste("stacked_barplot_", rank_name_for_file, "_top", n_taxa, ".png", sep = "")
    ggsave(stacked_plot_filename, plot = p_stacked, width = 12, height = 8, dpi = 300)
    
    cat(sprintf("Stacked bar plot saved as: %s\n", stacked_plot_filename))
  }
  
  # Alpha diversity calculations should use raw counts
  indices <- c("Observed", "Chao1", "Shannon", "Simpson")
  for (index in indices) {
    p <- plot_richness(physeq_raw, x = "Condition", measures = index) + 
      geom_boxplot(aes(color = Condition)) +
      ggtitle(paste(level_suffix, index, sep = "_"))
    
    # Save plot
    plot_filename <- paste("alpha_diversity_", rank_name_for_file, "_", index, ".png", sep = "")
    ggsave(plot_filename, plot = p, width = 10, height = 8)
  }
  
  # Beta diversity analysis can use the relative abundance data
  distances <- c("bray", "jaccard")
  for (dist in distances) {
    distance_matrix <- phyloseq::distance(physeq_relative, method = dist)
    pcoa_results <- cmdscale(distance_matrix, eig = TRUE)
    pcoa_df <- as.data.frame(pcoa_results$points)
    
    # Check how many dimensions we have and handle accordingly
    n_dims <- ncol(pcoa_df)
    if (n_dims < 2) {
      cat(sprintf("Warning: PCoA for %s %s only produced %d dimension(s). Skipping 2D plot.\n", 
                  level_suffix, dist, n_dims))
      next
    }
    
    # Rename columns to V1, V2 for consistency
    colnames(pcoa_df)[1:2] <- c("V1", "V2")
    pcoa_df$condition <- sample_metadata_filtered$Condition
    
    # Conduct PERMANOVA using adonis2
    permanova_results <- adonis2(distance_matrix ~ Condition, data = sample_metadata_filtered)
    # Conduct ANOSIM
    anosim_results <- anosim(distance_matrix, sample_metadata_filtered$Condition)
    
    # Extract p-value from PERMANOVA results
    permanova_pvalue <- permanova_results$`Pr(>F)`[1]
    
    # Add error checking for p-value extraction
    if (is.null(permanova_pvalue) || is.na(permanova_pvalue)) {
      permanova_pvalue <- "NA"
      cat("Warning: Could not extract PERMANOVA p-value\n")
    }
    
    # Print results
    cat(sprintf("\n%s %s PERMANOVA Results:\n", level_suffix, dist))
    print(permanova_results)
    cat(sprintf("\n%s %s ANOSIM Results:\n", level_suffix, dist))
    print(anosim_results)
    
    # Plot PCoA with corrected p-value access
    p <- ggplot(pcoa_df, aes(x = V1, y = V2, color = condition)) +
      geom_point(size = 5) +
      geom_text(aes(label = row.names(pcoa_df)), nudge_x = 0.02, nudge_y = 0.02, check_overlap = TRUE) +
      theme_bw() +
      theme(legend.position = 'top', legend.title = element_blank()) +
      ggtitle(paste(level_suffix, dist, "PERMANOVA p =", format(permanova_pvalue, digits = 4), "ANOSIM R =", format(anosim_results$statistic, digits = 4)))
    
    # Save plot with results
    plot_filename <- paste("pcoa_", rank_name_for_file, "_", dist, "_with_stats.png", sep = "")
    ggsave(plot_filename, plot = p, width = 10, height = 8)
  }
}

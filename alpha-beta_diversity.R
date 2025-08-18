library(phyloseq)
library(ggplot2)
library(tidyverse)
library(vegan)


setwd("/Users/juanjovel/Library/CloudStorage/OneDrive-UniversityofCalgary/jj/UofC/data_analysis/me/courses/2025/shotgun")

# Define the levels you want to iterate over
levels <- 1:7

# Define the taxonomic ranks
taxonomic_ranks <- c("Kingdom", "Phylum", "Class", "Order", "Family", "Genus", "Species")

# Iterate over each level
for (level in levels) {
  # Generate file name based on level
  infile <- sprintf("inflammation_all_samples_kraken2-counts_10up_level_%d.tsv", level)
  if (!file.exists(infile)) {
    cat(sprintf("File %s does not exist. Skipping level %d.\n", infile, level))
    next
  }

  # Extract level suffix and number
  level_suffix <- sprintf("level_%d", level)
  taxonomic_rank_name <- taxonomic_ranks[level]
  rank_name_for_file <- gsub(" ", "_", tolower(taxonomic_rank_name))
  level_number <- level

  # Select the taxonomic ranks to use based on the level
  ranks_to_use <- taxonomic_ranks[1:level_number]

  cat(sprintf("Processing %s (%s)...\n", level_suffix, taxonomic_rank_name))

  # Read the OTU table from the file
  shotgun_table <- read.csv(infile, sep = "\t", header = TRUE, check.names = FALSE, row.names = 1)

  cat(sprintf("Original data dimensions: %d taxa, %d samples\n", nrow(shotgun_table), ncol(shotgun_table)))

  # Data preprocessing - remove rows with all zeros and handle missing values
  shotgun_table[is.na(shotgun_table)] <- 0
  shotgun_table <- shotgun_table[rowSums(shotgun_table) > 0, ]

  cat(sprintf("After filtering zero-sum taxa: %d taxa, %d samples\n", nrow(shotgun_table), ncol(shotgun_table)))

  # Check if we have enough data to proceed
  if (nrow(shotgun_table) < 2) {
    cat(sprintf("Not enough taxa (< 2) for %s. Skipping.\n", level_suffix))
    next
  }

  # Ensure taxa names in OTU table are consistent and formatted correctly
  taxa_names_in_otu_table <- rownames(shotgun_table)

  otu_table_obj <- otu_table(as.matrix(shotgun_table), taxa_are_rows = TRUE)

  # Create taxa information
  taxa_info <- data.frame(Taxa = taxa_names_in_otu_table) %>%
    separate(Taxa, into = ranks_to_use, sep = "\\|", fill = "right") %>%
    as.data.frame()

  row.names(taxa_info) <- taxa_names_in_otu_table # Ensure row names match OTU table

  tax_table_obj <- tax_table(as.matrix(taxa_info))

  samples <- colnames(shotgun_table)

  # metadata
  sample_metadata_df <- data.frame(
    SampleID = samples,
    Condition = c("Control", "Control", "Control", "Control", "Control", "Treatment", "Treatment", "Treatment", "Treatment", "Treatment")
  )

  row.names(sample_metadata_df) <- sample_metadata_df$SampleID

  sample_metadata <- sample_data(sample_metadata_df)

  # Create phyloseq object
  physeq <- phyloseq(otu_table_obj, tax_table_obj, sample_metadata)

  # Alpha diversity
  cat("Computing alpha diversity...\n")
  indices <- c("Observed", "Chao1", "ACE", "Shannon", "Simpson", "InvSimpson")
  for (index in indices) {
    tryCatch(
      {
        p <- plot_richness(physeq, x = "Condition", measures = index) +
          geom_boxplot(aes(color = Condition)) +
          ggtitle(paste(level_suffix, index, sep = "_"))

        # Save plot
        plot_filename <- paste("alpha_diversity_", rank_name_for_file, "_", index, ".png", sep = "")
        ggsave(plot_filename, plot = p, width = 10, height = 8)
        cat(sprintf("  Saved: %s\n", plot_filename))
      },
      error = function(e) {
        cat(sprintf("  Error with %s: %s\n", index, e$message))
      }
    )
  }

  # Beta diversity with PERMANOVA and ANOSIM
  cat("Computing beta diversity...\n")
  distances <- c("bray", "jaccard", "jsd")
  for (dist in distances) {
    cat(sprintf("  Processing %s distance...\n", dist))
    tryCatch(
      {
        # Calculate distance matrix
        distance_matrix <- phyloseq::distance(physeq, method = dist)

        # Debug: Check distance matrix properties
        cat(sprintf("    Distance matrix class: %s\n", class(distance_matrix)))
        cat(sprintf("    Distance matrix dimensions: %s\n", paste(dim(as.matrix(distance_matrix)), collapse = "x")))

        # Convert to matrix for checking
        dist_mat <- as.matrix(distance_matrix)

        # Check for problematic values
        has_na <- any(is.na(dist_mat))
        has_inf <- any(is.infinite(dist_mat))
        has_nan <- any(is.nan(dist_mat))

        cat(sprintf("    Has NA: %s, Has Inf: %s, Has NaN: %s\n", has_na, has_inf, has_nan))

        # Additional diagnostics
        cat(sprintf(
          "    Distance range: %s to %s\n",
          format(min(dist_mat), digits = 4),
          format(max(dist_mat), digits = 4)
        ))
        cat(sprintf("    Matrix rank: %d\n", qr(dist_mat)$rank))

        if (has_na || has_inf || has_nan) {
          cat(sprintf("    Warning: Invalid values in distance matrix for %s %s. Skipping.\n", level_suffix, dist))
          next
        }

        # Try multiple approaches for PCoA
        pcoa_results <- NULL

        # Method 1: Standard cmdscale
        tryCatch(
          {
            pcoa_results <- cmdscale(distance_matrix, eig = TRUE, k = 2)
            if (is.null(pcoa_results) || is.null(dim(pcoa_results)) || ncol(pcoa_results) < 2) {
              pcoa_results <- NULL
            }
          },
          error = function(e) {
            cat(sprintf("    cmdscale failed: %s\n", e$message))
            pcoa_results <<- NULL
          }
        )

        # Method 2: Try with different parameters if first method failed
        if (is.null(pcoa_results)) {
          tryCatch(
            {
              cat("    Trying cmdscale with add=TRUE...\n")
              pcoa_results <- cmdscale(distance_matrix, eig = TRUE, k = 2, add = TRUE)
              if (is.null(pcoa_results) || is.null(dim(pcoa_results)) || ncol(pcoa_results) < 2) {
                pcoa_results <- NULL
              }
            },
            error = function(e) {
              cat(sprintf("    cmdscale with add=TRUE failed: %s\n", e$message))
              pcoa_results <<- NULL
            }
          )
        }

        # Method 3: Use capscale from vegan as alternative
        if (is.null(pcoa_results)) {
          tryCatch(
            {
              cat("    Trying capscale as alternative...\n")
              cap_result <- capscale(distance_matrix ~ 1)
              pcoa_coords <- scores(cap_result)$sites[, 1:2]
              pcoa_results <- pcoa_coords
            },
            error = function(e) {
              cat(sprintf("    capscale failed: %s\n", e$message))
              pcoa_results <<- NULL
            }
          )
        }

        # Check if any method succeeded
        if (is.null(pcoa_results)) {
          cat(sprintf("    Warning: All PCoA methods failed for %s %s. Skipping plotting.\n", level_suffix, dist))

          # Still run statistical tests even if plotting fails
          cat("    Running PERMANOVA and ANOSIM without plotting...\n")
          permanova_results <- adonis2(distance_matrix ~ Condition, data = sample_metadata_df, permutations = 999)
          anosim_results <- anosim(distance_matrix, sample_metadata_df$Condition, permutations = 999)

          cat(sprintf("\n%s %s PERMANOVA Results:\n", level_suffix, dist))
          print(permanova_results)
          cat(sprintf("\n%s %s ANOSIM Results:\n", level_suffix, dist))
          print(anosim_results)

          next
        }

        # Create data frame for plotting
        pcoa_df <- data.frame(
          PC1 = pcoa_results[, 1],
          PC2 = pcoa_results[, 2],
          SampleID = rownames(pcoa_results),
          stringsAsFactors = FALSE
        )

        # Match conditions properly
        pcoa_df$Condition <- sample_metadata_df$Condition[match(pcoa_df$SampleID, sample_metadata_df$SampleID)]

        # Conduct PERMANOVA
        cat("    Running PERMANOVA...\n")
        permanova_results <- adonis2(distance_matrix ~ Condition, data = sample_metadata_df, permutations = 999)

        # Conduct ANOSIM
        cat("    Running ANOSIM...\n")
        anosim_results <- anosim(distance_matrix, sample_metadata_df$Condition, permutations = 999)

        # Print results
        cat(sprintf("\n%s %s PERMANOVA Results:\n", level_suffix, dist))
        print(permanova_results)
        cat(sprintf("\n%s %s ANOSIM Results:\n", level_suffix, dist))
        print(anosim_results)

        # Extract p-value and R statistic for plot title
        permanova_p <- permanova_results$`Pr(>F)`[1]
        anosim_r <- anosim_results$statistic

        # Plot PCoA
        p <- ggplot(pcoa_df, aes(x = PC1, y = PC2, color = Condition)) +
          geom_point(size = 5) +
          geom_text(aes(label = SampleID), nudge_x = 0.02, nudge_y = 0.02, check_overlap = TRUE) +
          theme_bw() +
          theme(legend.position = "top", legend.title = element_blank()) +
          labs(
            x = "PC1",
            y = "PC2",
            title = sprintf(
              "%s %s - PERMANOVA p = %s, ANOSIM R = %s",
              level_suffix, dist,
              format(permanova_p, digits = 4, scientific = FALSE),
              format(anosim_r, digits = 4, scientific = FALSE)
            )
          )

        # Save plot with results
        plot_filename <- paste("pcoa_", rank_name_for_file, "_", dist, "_with_stats.png", sep = "")
        ggsave(plot_filename, plot = p, width = 10, height = 8)

        cat(sprintf("    Successfully created plot: %s\n", plot_filename))
      },
      error = function(e) {
        cat(sprintf("    Error processing %s %s: %s\n", level_suffix, dist, e$message))
        cat(sprintf("    Error details: %s\n", toString(e$call)))
      }
    )
  }

  cat(sprintf("Completed processing for %s\n\n", level_suffix))
}

cat("Analysis complete!\n")

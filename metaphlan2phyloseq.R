metaphlanToPhyloseq <- function(
  metaphlandir,
  metadat=NULL,
  simplify=TRUE){
  ## tax is a matrix or data.frame with the table of taxonomic abundances, rows are taxa, columns are samples
  ## metadata is an optional data.frame of specimen metadata, rows are samples, columns are variables
  ## if simplify=TRUE, use only the most detailed level of taxa names in the final object
  ## metaphlanToPhyloseq("~/Downloads/metaphlan_bugs_list")
  .getMetaphlanTree <- function(removeGCF=TRUE, simplify=TRUE){
    if (!requireNamespace("ape")) {
      stop("Please install the ape package to read Newick trees")
    }
    nwkfile <- bzfile(system.file("extdata/metaphlan2_selected.tree.reroot.nwk.bz2",
                                  package="curatedMetagenomicData"))
    tree <- ape::read.tree(nwkfile)
    close(nwkfile)
    if(removeGCF)
      tree$tip.label <- sub("\\|GCF_[0-9]+$", "", tree$tip.label)
    if(simplify)
      tree$tip.label <- gsub(".+\\|", "", tree$tip.label)
    return(tree)
  }
  .joinListOfMatrices <- function(obj) {
    rnames <- Reduce(union, lapply(obj, rownames))
    cnames <- names(obj)
    if (!all(isUnique(cnames))) {
      stop("Column names are not unique.")
    }
    output <- matrix(0,
                     nrow = length(rnames),
                     ncol = length(cnames),
                     dimnames = list(rnames, cnames)
    )
    for (i in seq_along(obj)) {
      output[match(rownames(obj[[i]]), rownames(output)), i] <- obj[[i]][, 1]
    }
    return(output)
  }
  fnames <- list.files(metaphlandir)
  bug.l <- lapply(fnames, function(x){
    res <- read.delim(file.path(metaphlandir, x), stringsAsFactors = FALSE, row.names = 1)
    colnames(res) <- x
    return(res)
  })
  names(bug.l) <- fnames
  tax <- .joinListOfMatrices(bug.l)
  xnames = rownames(tax)
  shortnames = gsub(".+\\|", "", xnames)
  if(simplify){
    rownames(tax) = shortnames
  }
  x2 = strsplit(xnames, split="|", fixed=TRUE)
  taxmat = matrix(NA, ncol=max(sapply(x2, length)), nrow=length(x2))
  colnames(taxmat) = c("Kingdom", "Phylum", "Class", "Order", "Family", "Genus", "Species", "Strain")[1:ncol(taxmat)]
  rownames(taxmat) = rownames(tax)
  for (i in 1:nrow(taxmat)){
    taxmat[i, 1:length(x2[[i]])] <- x2[[i]]
  }
  taxmat = gsub("[a-z]__", "", taxmat)
  taxmat = phyloseq::tax_table(taxmat)
  otutab = phyloseq::otu_table(tax, taxa_are_rows=TRUE)
  tree <- .getMetaphlanTree(simplify=simplify)
  if(is.null(metadat)){
    metadat <- data.frame(file=fnames, row.names=fnames, stringsAsFactors = FALSE)
  }
  res = phyloseq::phyloseq(taxmat, otutab, phyloseq::sample_data(metadat), tree)
  return(res)
}

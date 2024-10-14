# TCGA Data Scraper

This Python script automates the download of gene expression data from the **The Cancer Genome Atlas (TCGA)** via the **Xena Browser**. The data is compressed as `.gz` files and then decompressed into `.tsv` files, which are stored in a directory called `cohorts`.

## Requirements

To run this script, you will need the following Python packages:

- `selenium` - For web scraping
- `requests` - For downloading files
- `gzip` - For decompressing `.gz` files
- `shutil` - For file operations
- A working **Google Chrome** installation and **ChromeDriver**

Install the necessary Python packages with the following commands:

```bash
pip install selenium requests

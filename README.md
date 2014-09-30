# Genome Fetcher

Fetch genomes from ftp.ncbi.nih.gov

## Setup
(sudo) pip install -r requirements.txt

## Usage

The two commands are search and fetch.  Each find the same results.  
Search displays the results, while fetch silently downloads them.

### Searching

*   gfetch.py search --name staphylococcus aureus # Finds all staph aureus genomes
*   gfetch.py search --status gapless_chromosome
*   gfetch.py search --name staphylococcus aureus --status gapless_chromosome --verbose

### Fetching
*   gfetch.py fetch --name staphylococcus aureus --status gapless_chromosome --outdir genomes

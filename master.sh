#!/bin/sh

# Query the database for HTML documents from page_downloads 
# where the scrape date range is D/M/YYYY to D+14/M+1/YYY[Y|Y+1].
# Write tab-sep results to html_docs/MM_YYYY_html.tsv
# Please use options [--year | -y] YYYY [--month | -m] MM [--day | -d] DD
html_docs/get_html.py 

# Use Lynx on the HTML on disk (in html_docs/MM_YYYY_html.tsv) to 
# extract text from HTML. Write the tab-sep extracted results to 
# lynx_docs/MM_YYYY_lx.tsv
# Note: lynx_docs/get_lynx_docs.py is deprecated: slow and skips prev step.
# Please use options [--year | -y] YYYY [--month | -m] MM 
lynx_docs/get_lx_docs.py

# Get names from an extracted doc using Stanford NER:
# Writes JSON to all_names/all_names_<dataset>.txt
# Please use options [--year | -y] YYYY [--month | -m] MM 
all_names/corenlp_all_names.py

# Cluster names by string similarity, map unique names to
# docs (and dates) where they are mentioned
# Writes JSON to corefs/corefs_<dataset>.txt
corefs/learn_unique_names.py

# Add field to corefs/corefs_<dataset>.txt with the verb used to describe a 
# killing within the sentence(s) that include each coreference tuple. 
# Put the result in corefs/corefs_by_vb_<dataset>.txt
corefs/get_fatalities.py


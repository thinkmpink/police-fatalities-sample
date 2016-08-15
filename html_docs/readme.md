*Description*

Each month-and-a-half untracked tsv file contains all the news articles found 
in "page_downloads" from that month, and the time split is monthly:
 `M_YYYY_html.tsv`: MM 1, 2015 to (M+1) 15, 2015 scrape date

The overlap is intended to correct for delay in reporting events as well
as extended discussion that may continue in the news well after the event.

Each document has 3 tab-separated columns: "ID", "scrapedate", and "rawhtml"

`get_html.py` writes these documents

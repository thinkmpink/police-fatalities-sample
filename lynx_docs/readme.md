**Script**

`get_lx_docs.py` outputs tsv files of the form `lynx_docs/<dataset>_lx.tsv`. 
These documents contains a month-and-a-half worth of HTML data from 
`html_docs/<dataset>_html.tsv` that has been converted to text using Lynx, 
a unix tool. 
- The Python wrapper for Lynx is in `newsevents/text_extraction/wrappers.py.` 
- Each entry is of the form: ID, Scrape date, Article body.

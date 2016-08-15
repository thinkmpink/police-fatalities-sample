**Scripts**

- `ner.py` uses Stanford CoreNLP NER or spaCy to collect names from the 
Lynx-extracted documents in `../lynx_docs/<dataset>_lx.tsv` and writes them 
to `./all_names_<dataset>.json` in the format: {'date': 'DD-MM-YYYY', 'docid': 
12345, 'name_candidates': [], 'fatal_verbs': []}

- `json_to_text_names.py` writes all names from the json object representation 
saved in `./all_names_<dataset>.json` to a set of names separated by newlines 
in a text file `./<dataset>_names_only.txt`
